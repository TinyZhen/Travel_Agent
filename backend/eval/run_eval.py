"""Scenario evaluation for Roameo.

    cd backend
    ROAMEO_OFFLINE=1 python -m eval.run_eval          # deterministic, no keys needed
    python -m eval.run_eval --runs 3                  # with OPENROUTER_API_KEY: LLM mode, repeated

Each case is a scripted conversation plus checks on the final state. Cases marked
`known_limitation` document behaviour we expect to be imperfect; they are reported,
not hidden. Results go to docs/evaluation_results[_llm].md and .json.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time
from datetime import date
from typing import Callable

import llm
from agents.orchestrator import new_session

TODAY = date(2026, 10, 25)  # fixed so relative dates are reproducible
DOCS = pathlib.Path(__file__).resolve().parents[2] / "docs"


def tools_called(st) -> set[str]:
    # 'call search_attractions "top sights"' is still the search_attractions tool
    return {t.action.removeprefix("call ").split(" ")[0] for t in st.trace if t.action.startswith("call ")}


def items(st) -> list[dict]:
    """Activities only (no meals, arrival or hotel logistics)."""
    return [it for d in st.plan.days for it in d.items if it["kind"] in ("attraction", "event")] if st.plan else []


Check = tuple[str, Callable]

CASES: list[dict] = [
    dict(id="T1", category="Functional / E2E", title="Complete request → priced plan",
         turns=["Weekend trip from Boston to New York on Nov 13 with my partner, we love museums and jazz, budget $1500"],
         expected="Plan for 2 travelers, Nov 13–15, all 5 tools used, total ≤ $1500, no questions.",
         checks=[("status awaiting approval", lambda s, _: s.status == "awaiting_approval"),
                 ("2 travelers, 2 nights", lambda s, _: (s.spec.travelers, s.spec.nights) == (2, 2)),
                 ("start date 2026-11-13", lambda s, _: str(s.spec.start_date) == "2026-11-13"),
                 ("all 5 tools called", lambda s, _: len(tools_called(s)) == 5),
                 ("within budget", lambda s, _: s.plan.total_cost <= 1500),
                 ("museum interest used", lambda s, _: sum("museum" in (it["name"].lower()) for it in items(s)) >= 2)]),
    dict(id="T2", category="Human-in-the-loop", title="Missing date → agent asks, then plans",
         turns=["I want to go from Boston to Chicago for 3 nights", "Nov 20"],
         expected="Turn 1 asks for a date; turn 2 produces a plan starting Nov 20.",
         checks=[("asked for date first", lambda s, h: "date" in " ".join(h[0]["questions"]).lower()),
                 ("then planned", lambda s, _: s.status == "awaiting_approval" and s.plan is not None),
                 ("date applied", lambda s, _: str(s.spec.start_date) == "2026-11-20")]),
    dict(id="T3", category="Human-in-the-loop", title="Missing destination → asks",
         turns=["Plan me a relaxing trip from Boston next weekend"],
         expected="Asks where to go; does not invent a destination.",
         checks=[("asks where", lambda s, _: any("where" in q.lower() for q in s.questions)),
                 ("no plan invented", lambda s, _: s.plan is None)]),
    dict(id="T4", category="Failure handling", title="Unknown city → asks for clarification",
         turns=["Take me from Boston to Atlantis on Nov 20"],
         expected="Says it cannot find the city and asks which one is meant.",
         checks=[("asks about the city", lambda s, _: any("couldn't find" in q for q in s.questions)),
                 ("no plan", lambda s, _: s.plan is None)]),
    dict(id="T5", category="Failure handling", title="Past date is rejected",
         turns=["Trip from Boston to Montreal on 2026-03-03 for 2 nights"],
         expected="Flags the date as in the past and asks again.",
         checks=[("flags past date", lambda s, _: any("past" in q for q in s.questions))]),
    dict(id="T6", category="Human-in-the-loop", title="Infeasible budget → escalate, not fake it",
         turns=["Chicago for 4 days starting Nov 20 from Boston, budget $300"],
         expected="Critic tries cheaper options, then asks the human (raise budget / shorten / drive).",
         checks=[("\"4 days\" = 3 nights", lambda s, _: s.spec.nights == 3),
                 ("critic revised ≥2 times", lambda s, _: s.plan.revisions >= 2),
                 ("over-budget is reported, not hidden", lambda s, _: any(i.startswith("over_budget") for i in s.plan.issues)),
                 ("asks human with options", lambda s, _: any("raise the budget" in q for q in s.questions))]),
    dict(id="T7", category="Functional", title="Driving → no flight search, driving costs",
         turns=["Road trip from Boston to Montreal on Nov 14 for 2 nights, I'll drive"],
         expected="Flights tool not called; gas/parking appear in the cost breakdown.",
         checks=[("no flight tool", lambda s, _: "search_flights" not in tools_called(s)),
                 ("gas & parking costed", lambda s, _: {"gas_and_tolls_estimate", "parking_estimate"} <= s.plan.cost_breakdown.keys())]),
    dict(id="T8", category="Functional", title="Local day trip → no flight or hotel",
         turns=["Day trip in Boston on Nov 7, I live in Boston and like history"],
         expected="Treated as local: no flight, no hotel; the first sight matches the history interest.",
         checks=[("local transport", lambda s, _: s.spec.transport == "local"),
                 ("no flight/hotel tools", lambda s, _: not {"search_flights", "search_hotels"} & tools_called(s)),
                 ("history first", lambda s, _: "history" in items(s)[0].get("why", ""))]),
    dict(id="T9", category="Real-world adaptation", title="Rainy day → indoor activities first",
         turns=["New York Nov 6 for 2 nights with museums, from Boston"],
         expected="On days with ≥60% rain the first activity is indoors.",
         checks=[("rain rule respected", lambda s, _: all(
             [it for it in d.items if it["kind"] == "attraction"][0].get("indoor") for d in s.plan.days
             if (d.rain_chance or 0) >= 60 and any(it["kind"] == "attraction" for it in d.items)))]),
    dict(id="T10", category="Human-in-the-loop", title="Feedback: \"cheaper\" really lowers price",
         turns=["Weekend in New York on Nov 13 from Boston, budget $2000", "make it cheaper"],
         expected="Second plan total is strictly lower than the first.",
         checks=[("price dropped", lambda s, h: s.plan.total_cost < h[0]["total"])]),
    dict(id="T11", category="Human-in-the-loop", title="Feedback: \"different hotel\"",
         turns=["Washington DC on Nov 20 for 2 nights from Boston", "I'd like a different hotel"],
         expected="Hotel changes; the rejected one is not re-proposed.",
         checks=[("hotel changed", lambda s, h: s.plan.hotel["name"] != h[0]["hotel"])]),
    dict(id="T12", category="Human-in-the-loop", title="Feedback: skip a specific place",
         turns=["San Francisco on Nov 20 for 3 nights from Boston", "skip the Ferry Building please"],
         expected="The Ferry Building is removed from the itinerary.",
         checks=[("Ferry Building was in first plan", lambda s, h: any("Ferry Building" in n for n in h[0]["names"])),
                 ("Ferry Building removed", lambda s, _: s.plan and not any("Ferry Building" in it["name"] for it in items(s)))]),
    dict(id="T13", category="Safety / oversight", title="Nothing exported before approval",
         turns=["Philadelphia on Nov 20 for 2 nights from Boston", "approve"],
         expected="Status only becomes approved after explicit human approval.",
         checks=[("awaiting before approval", lambda s, h: h[0]["status"] == "awaiting_approval"),
                 ("approved after", lambda s, _: s.status == "approved")]),
    dict(id="T14", category="Functional", title="Group of 4 → 2 rooms, per-person costs scale",
         turns=["Family of 4 from Boston to Chicago on Nov 20 for 2 nights, kids love science"],
         expected="Hotel cost = 2 rooms; family/science attractions prioritised.",
         checks=[("2 rooms priced", lambda s, _: s.plan.cost_breakdown["hotel"] == s.plan.hotel["nightly_price"] * 2 * 2),
                 ("family/science picks", lambda s, _: any(n in it["name"] for it in items(s) for n in ("Field Museum", "Shedd")))]),
    dict(id="T15", category="Failure handling", title="Vague feedback → asks instead of guessing",
         turns=["Montreal on Nov 20 for 2 nights from Boston", "hmm not sure"],
         expected="No change to the plan; agent explains what it can change.",
         checks=[("plan unchanged", lambda s, h: s.plan.total_cost == h[0]["total"]),
                 ("helpful question", lambda s, _: any("wasn't sure" in q for q in s.questions))]),
    dict(id="T16", category="Human-in-the-loop", title="Raise budget after escalation",
         turns=["Chicago for 4 days starting Nov 20 from Boston, budget $600", "budget is $1400"],
         expected="After the human raises the budget, the plan fits and the question disappears.",
         checks=[("fits new budget", lambda s, _: s.plan.total_cost <= 1400),
                 ("no open question", lambda s, _: not s.questions)]),
    dict(id="T19", category="Human-in-the-loop", title="No origin → asks, never assumes",
         turns=["Weekend in Chicago on Nov 20, budget $1200", "Philadelphia"],
         expected="Asks where the traveler is leaving from; the bare answer becomes the origin, not the destination.",
         checks=[("asked for origin", lambda s, h: any("leaving from" in q for q in h[0]["questions"])),
                 ("answer used as origin", lambda s, _: (s.spec.origin, s.spec.destination) == ("Philadelphia", "Chicago")),
                 ("flight from PHL", lambda s, _: s.plan.flight["from"] == "PHL")]),
    dict(id="T20", category="Real-world adaptation", title="Cutting cost keeps what the traveler loves",
         turns=["Weekend in New York on Nov 13 from Boston, I love museums, budget $600"],
         expected="Critic cuts cost but keeps at least one museum, because museums are the stated interest.",
         checks=[("critic had to cut", lambda s, _: s.plan.revisions >= 2),
                 ("within budget", lambda s, _: s.plan.total_cost <= 600),
                 ("a museum survives", lambda s, _: any("Museum" in it["name"] for it in items(s)))]),
    dict(id="T21", category="Human-in-the-loop", title="\"More museums\" revises, doesn't restart",
         turns=["Weekend in New York on Nov 13 from Boston, we like food and walking, budget $2500",
                "I want to go to more museums"],
         expected="If a museum can be added, it is (keeping most of the plan, changes reported); if every known museum "
                  "is already in, the agent says so and leaves the plan unchanged.",
         checks=[("museum added, or honest 'no more' with plan unchanged", lambda s, h:
                  any(c.startswith("+ ") and "Museum" in c for c in s.plan.changes)
                  or (any("couldn't fit" in q for q in s.questions) and [it["name"] for it in items(s)] == h[0]["names"])),
                 ("most of the plan kept", lambda s, h: len(set(h[0]["names"]) & {it["name"] for it in items(s)})
                  >= len(h[0]["names"]) / 2)]),
    dict(id="T22", category="Human-in-the-loop", title="\"Slower pace\" lightens the days",
         turns=["Chicago on Nov 20 for 3 nights from Boston, budget $3000", "too packed, slower pace please"],
         expected="Fewer sights per day after the change; days start later.",
         checks=[("fewer sights", lambda s, h: sum(it["kind"] == "attraction" for it in items(s)) < h[0]["sights"])]),
    dict(id="T23", category="Failure handling", title="A state is not a city → asks which city",
         turns=["I want to go to Michigan on Dec 22 from Boston for 3 days", "Detroit"],
         expected="Asks which city in Michigan (suggesting Detroit, Ann Arbor, Grand Rapids), then plans Detroit.",
         checks=[("asked which city", lambda s, h: any("is a state" in q for q in h[0]["questions"])),
                 ("planned Detroit", lambda s, _: s.spec.destination == "Detroit" and s.plan is not None)]),
    dict(id="T24", category="Real-world adaptation", title="Winter trip → indoor first, little outdoor time",
         turns=["Detroit on Dec 22 for 2 nights from Boston, we like art and history"],
         expected="Cold days get at most one ordinary outdoor stop; the traveler is warned about the cold.",
         checks=[("days marked cold", lambda s, _: all(d.condition in ("cold", "freezing", "snowy") for d in s.plan.days)),
                 ("≤1 outdoor stop per day", lambda s, _: all(
                     sum(it["kind"] == "attraction" and not it.get("indoor") and not it.get("winter") for it in d.items) <= 1
                     for d in s.plan.days)),
                 ("cold warning", lambda s, _: any("Pack warm" in q for q in s.questions))]),
    dict(id="T25", category="Real-world adaptation", title="Seasonal closures respected",
         turns=["Chicago on Jan 15 for 2 nights from Boston, I love architecture"],
         expected="The river cruise (April–November only) is not scheduled in January.",
         checks=[("no river cruise", lambda s, _: not any("River Cruise" in it["name"] for it in items(s)))]),
    dict(id="T17", category="Known limitation", title="City outside demo data (Paris)", known_limitation=True,
         turns=["Paris on Nov 20 for 3 nights from Boston"],
         expected="Offline: cannot resolve the city and asks. Live: resolves via geocoding but has no airport code, so flights fail and the human is asked.",
         checks=[("handled without crashing, human asked", lambda s, _: bool(s.questions))]),
    dict(id="T18", category="Known limitation", title="Complex date phrase", known_limitation=True,
         turns=["New York the first weekend of December, from Boston"],
         expected="Rule parser can't resolve the phrase → asks for a date (LLM mode should resolve it to Dec 4).",
         checks=[("resolved to Dec 4", lambda s, _: str(s.spec.start_date) == "2026-12-04")]),
]


def run_case(case: dict) -> dict:
    sess = new_session(TODAY)
    snapshots, t0 = [], time.time()
    for msg in case["turns"]:
        st = sess.handle(msg)
        snapshots.append({"status": st.status, "questions": list(st.questions),
                          "names": [it["name"] for it in items(st)],
                          "sights": sum(it["kind"] == "attraction" for it in items(st)),
                          "total": st.plan.total_cost if st.plan else None,
                          "hotel": st.plan.hotel["name"] if st.plan and st.plan.hotel else None})
    elapsed = time.time() - t0
    results = []
    for name, fn in case["checks"]:
        try:
            ok = bool(fn(st, snapshots))
        except Exception as e:
            ok, name = False, f"{name} (error: {type(e).__name__})"
        results.append((name, ok))
    actual = (f"status={st.status}; " + (f"total=${st.plan.total_cost:,.0f}; revisions={st.plan.revisions}; "
                                         if st.plan else "") + (f"asked: {st.questions[0]}" if st.questions else ""))
    return {"id": case["id"], "category": case["category"], "title": case["title"],
            "expected": case["expected"], "actual": actual.strip("; "),
            "checks": results, "passed": all(ok for _, ok in results),
            "known_limitation": case.get("known_limitation", False), "seconds": round(elapsed, 2),
            "tools": sorted(tools_called(st))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=1, help="repeat each case to measure consistency")
    args = ap.parse_args()
    mode = "llm" if llm.available() else "rules (demo)"
    all_runs = [[run_case(c) for c in CASES] for _ in range(args.runs)]
    first = all_runs[0]
    consistency = {c["id"]: sum(r[i]["passed"] for r in all_runs) / args.runs for i, c in enumerate(CASES)}

    core = [r for r in first if not r["known_limitation"]]
    lines = [f"# Roameo evaluation results", "",
             f"- Mode: **{mode}**, runs per case: {args.runs}, reference date {TODAY}",
             f"- Core cases passed: **{sum(r['passed'] for r in core)}/{len(core)}**; "
             f"checks passed: {sum(ok for r in core for _, ok in r['checks'])}/{sum(len(r['checks']) for r in core)}",
             f"- Known-limitation cases: {sum(r['passed'] for r in first if r['known_limitation'])}/"
             f"{sum(r['known_limitation'] for r in first)} behaved ideally", "",
             "| ID | Category | Scenario | Expected | Actual | Result | Consistency |",
             "|---|---|---|---|---|---|---|"]
    for r in first:
        res = "✅ pass" if r["passed"] else ("⚠️ limitation" if r["known_limitation"] else "❌ fail")
        failed = [n for n, ok in r["checks"] if not ok]
        actual = r["actual"].replace("|", "/") + (f" — failed: {', '.join(failed)}" if failed else "")
        lines.append(f"| {r['id']} | {r['category']} | {r['title']} | {r['expected']} | {actual} | {res} | "
                     f"{consistency[r['id']]:.0%} |")
    DOCS.mkdir(exist_ok=True)
    stem = "evaluation_results" + ("_llm" if llm.available() else "")
    (DOCS / f"{stem}.md").write_text("\n".join(lines) + "\n")
    (DOCS / f"{stem}.json").write_text(json.dumps(
        {"mode": mode, "runs": args.runs, "results": first, "consistency": consistency}, indent=1, default=str))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
