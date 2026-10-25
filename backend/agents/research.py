"""Research agent: decides which tools a trip needs, calls them, and checks coverage.

With an LLM it runs a real tool-calling loop (the model picks tools and arguments
step by step). Without one, a rule policy picks the same tools. In both cases a
guardrail re-runs any essential tool the plan cannot do without.
"""
from __future__ import annotations

import json
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
        "search_flights": {"origin": spec.origin, "destination": d, "date": s, "travelers": spec.travelers},
        "search_hotels": {"destination": d, "checkin": s, "nights": spec.nights},
        "search_attractions": {"destination": d, "interests": spec.interests},
        "search_events": {"destination": d, "start_date": s, "nights": spec.nights, "interests": spec.interests},
        "get_weather": {"destination": d, "start_date": s, "nights": spec.nights},
    }[name]


def _call(name: str, args: dict, results: dict, log: Callable[[TraceStep], None]) -> str:
    try:
        out = tools.REGISTRY[name](**args)
    except Exception as e:  # tool bugs must not kill the whole plan
        out = [{"error": f"{type(e).__name__}: {e}"}]
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
    for name in required_tools(spec):
        if name not in results:
            if llm.available():
                log(TraceStep(agent="Research", action="guardrail", detail=f"{name} was skipped but is required"))
            _call(name, _default_args(name, spec), results, log)
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
        for c in calls:
            name = c.function.name
            try:
                args = json.loads(c.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            if name not in tools.REGISTRY:
                content = json.dumps({"error": f"unknown tool {name}"})
            else:
                content = _call(name, {**_default_args(name, spec), **args}, results, log)
            messages.append({"role": "tool", "tool_call_id": c.id, "content": content})
