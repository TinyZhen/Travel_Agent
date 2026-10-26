"""Research agent: decides which tools a trip needs, calls them, and checks coverage.

With an LLM it runs a real tool-calling loop (the model picks tools and arguments
step by step). Without one, a rule policy picks the same tools. In both cases a
guardrail re-runs any essential tool the plan cannot do without.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import llm
import tools
from schemas import TraceStep, TripSpec

MAX_STEPS = 8

SYSTEM = """You are the Research agent of a travel planner. Gather what is needed to plan this trip
by calling tools. Skip tools that are not needed (e.g. no flights when the traveler drives or stays local,
no hotels for a day trip). Pass the traveler's interests to attraction and event searches.
When you have enough, reply with the single word DONE."""


def required_tools(spec: TripSpec) -> list[str]:
    need = ["search_attractions", "get_weather"]
    if spec.nights > 0:
        need += ["search_hotels", "search_events"]
    if spec.transport == "fly":
        need.append("search_flights")
    return need


def _default_args(name: str, spec: TripSpec) -> dict:
    d, s = spec.destination, spec.start_date.isoformat()
    return {
        "search_flights": {"origin": spec.origin, "destination": d, "date": s, "travelers": spec.travelers,
                           "nights": spec.nights},
        "search_hotels": {"destination": d, "checkin": s, "nights": spec.nights, "travelers": spec.travelers},
        "search_attractions": {"destination": d, "interests": spec.interests},
        "search_events": {"destination": d, "start_date": s, "nights": spec.nights, "interests": spec.interests},
        "get_weather": {"destination": d, "start_date": s, "nights": spec.nights},
    }[name]


def _execute(name: str, args: dict) -> list:
    try:
        return tools.REGISTRY[name](**args)
    except Exception as e:  # tool bugs must not kill the whole plan
        return [{"error": f"{type(e).__name__}: {e}"}]


def _call_many(calls: list[tuple[str, dict]], results: dict, log: Callable[[TraceStep], None]) -> list[str]:
    """Run independent tool calls in parallel (live APIs take seconds each); log in request order."""
    with ThreadPoolExecutor(max_workers=max(len(calls), 1)) as pool:
        outs = list(pool.map(lambda c: _execute(*c), calls))
    return [_record(name, out, results, log) for (name, _), out in zip(calls, outs)]


def _record(name: str, out: list, results: dict, log: Callable[[TraceStep], None]) -> str:
    results[name] = out
    errors = [r["error"] for r in out if isinstance(r, dict) and "error" in r]
    src = {r.get("source") for r in out if isinstance(r, dict) and r.get("source")}
    log(TraceStep(agent="Research", action=f"call {name}",
                  detail=(f"error: {errors[0]}" if errors else f"{len(out)} results ({', '.join(sorted(src)) or 'n/a'})")))
    return json.dumps(out[:6], default=str)


def run(spec: TripSpec, log: Callable[[TraceStep], None]) -> dict:
    results: dict = {}
    if llm.available():
        try:
            _llm_loop(spec, results, log)
        except Exception as e:
            log(TraceStep(agent="Research", action="LLM loop failed, using rule policy", detail=str(e)[:160]))
    # Guardrail: make sure every essential tool ran (this is also the whole policy in rule mode).
    missing = [n for n in required_tools(spec) if n not in results]
    if missing and llm.available():
        log(TraceStep(agent="Research", action="guardrail", detail=f"required but skipped: {', '.join(missing)}"))
    _call_many([(n, _default_args(n, spec)) for n in missing], results, log)
    return results


def _llm_loop(spec: TripSpec, results: dict, log: Callable[[TraceStep], None]) -> None:
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": "Trip spec:\n" + spec.model_dump_json(indent=1)}]
    for _ in range(MAX_STEPS):
        msg = llm.chat(messages, tools=tools.SCHEMAS)
        calls = msg.tool_calls or []
        if not calls:
            log(TraceStep(agent="Research", action="finished", detail=(msg.content or "")[:120]))
            return
        messages.append({"role": "assistant", "content": msg.content or "",
                         "tool_calls": [c.model_dump() for c in calls]})
        valid = []
        for c in calls:
            try:
                args = json.loads(c.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            if c.function.name in tools.REGISTRY:
                valid.append((c, {**_default_args(c.function.name, spec), **args}))
        contents = dict(zip([c.id for c, _ in valid],
                            _call_many([(c.function.name, a) for c, a in valid], results, log)))
        for c in calls:
            messages.append({"role": "tool", "tool_call_id": c.id,
                             "content": contents.get(c.id, json.dumps({"error": f"unknown tool {c.function.name}"}))})
        if all(n in results for n in required_tools(spec)):
            # Everything the plan needs is in; skip the extra "anything else?" round trip.
            log(TraceStep(agent="Research", action="finished", detail="all required tools called"))
            return
