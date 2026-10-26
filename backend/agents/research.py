"""Research agent: decides which tools a trip needs, calls them, and checks coverage.

With an LLM it runs a real tool-calling loop (the model picks tools and arguments
step by step). Without one, a rule policy picks the same tools. In both cases a
guardrail re-runs any essential tool the plan cannot do without.
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import llm
import tools
from tools import _haversine_km
from schemas import TraceStep, TripSpec

MAX_STEPS = 8

SYSTEM = """You are the Research agent of a travel planner. Gather what is needed to plan this trip
by calling tools. Use search_attractions without a query for the initial plan (concerts and shows come
from search_events, not search_attractions). Skip tools that are not needed (e.g. no flights when the traveler drives or stays local,
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
    return [_record(name, out, results, log, args) for (name, args), out in zip(calls, outs)]


MERGE_TOOLS = {"search_attractions", "search_events"}


def _record(name: str, out: list, results: dict, log: Callable[[TraceStep], None], args: dict = None) -> str:
    good = [r for r in out if isinstance(r, dict) and "error" not in r]
    prev = results.get(name)
    if prev and name in MERGE_TOOLS:
        # The model may call a tool twice (e.g. "top sights" and "ski resorts"): keep both, never replace.
        known = {r.get("name") for r in prev if isinstance(r, dict)}
        results[name] = prev + [r for r in good if r.get("name") not in known]
    elif not prev or good:
        results[name] = out  # but an empty or failed retry never wipes out good results
    errors = [r["error"] for r in out if isinstance(r, dict) and "error" in r]
    src = {r.get("source") for r in out if isinstance(r, dict) and r.get("source")}
    q = f' "{args["query"]}"' if args and args.get("query") else ""
    log(TraceStep(agent="Research", action=f"call {name}{q}",
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
    for act in spec.activities:
        search_activity(spec, results, act, log)
    _seasonal_extras(spec, results, log)
    return results


def search_activity(spec: TripSpec, results: dict, activity: str, log: Callable[[TraceStep], None]) -> list[dict]:
    """Find places for an activity the traveler asked for (e.g. ski areas, which are usually outside the city)."""
    found = [a for a in _execute("search_activity", {"destination": spec.destination, "activity": activity})
             if isinstance(a, dict) and "error" not in a]
    results[f"activity:{activity}"] = found
    radius = tools.D.ACTIVITIES[activity][1]
    log(TraceStep(agent="Research", action=f"search activity: {activity}",
                  detail=(f"{len(found)} places within {radius} km; best: {found[0]['name']} ({found[0]['km_from_city']} km)"
                          if found else f"nothing found within {radius} km")))
    return found


def _seasonal_extras(spec: TripSpec, results: dict, log: Callable[[TraceStep], None]) -> None:
    """Cold trip? Look for indoor options and winter-only things instead of planning around parks."""
    weather = [w for w in results.get("get_weather") or [] if isinstance(w, dict) and "high_c" in w]
    if not weather or not any(w["high_c"] <= 5 or (w.get("snow_cm") or 0) >= 1 for w in weather):
        return
    lows = min(w["high_c"] for w in weather)
    log(TraceStep(agent="Research", action="season check",
                  detail=f"cold trip (highs down to {lows}°C, {weather[0].get('source')}): looking for indoor and winter options"))
    queries = ["indoor attractions"]
    if spec.start_date.month == 12 or (spec.start_date.month == 11 and spec.start_date.day >= 15):
        queries.append("holiday markets")
    queries.append("ice skating")
    for q in queries:
        search_more(spec, results, q, log)


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


def _same_place(a: dict, b: dict) -> bool:
    """'Eastern Market Shed 5' and 'Eastern Market' are one stop, not two."""
    if a["name"] == b["name"]:
        return True
    words = lambda n: {w for w in re.findall(r"[a-z]+", n.lower()) if len(w) > 3 and w not in
                       {"museum", "park", "the", "center", "centre", "market", "detroit", "city", "national"}}
    shared = words(a["name"]) & words(b["name"])
    close = a.get("lat") is not None and b.get("lat") is not None and _haversine_km(a, b) < 0.4
    return (close and bool(shared)) or (close and _haversine_km(a, b) < 0.08) or len(shared) >= 2


def search_more(spec: TripSpec, results: dict, query: str, log: Callable[[TraceStep], None],
                limit: int = 6) -> list[dict]:
    """Targeted follow-up search when the traveler asks for more of something (or a specific place).
    New places are merged into the existing research results; returns only the new ones."""
    found = _execute("search_attractions", {"destination": spec.destination,
                                            "interests": spec.interests, "query": query})
    existing = [a for a in results.get("search_attractions") or [] if isinstance(a, dict) and a.get("name")]
    new = []
    for a in found:
        if isinstance(a, dict) and a.get("name") and not any(_same_place(a, b) for b in existing + new):
            new.append(a)
    new = new[:limit]
    results.setdefault("search_attractions", []).extend(new)
    src = sorted({a.get("source") for a in new}) or ["nothing new"]
    log(TraceStep(agent="Research", action=f"search more: {query}", detail=f"{len(new)} new places ({', '.join(src)})"))
    return new
