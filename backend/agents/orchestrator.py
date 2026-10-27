"""Orchestrator: runs the agents in order and owns the human-in-the-loop states.

    user message ─► Intake ─(missing info?)─► ask human ─┐
                      │                                   │
                      ▼                                   │
                  Research (tool calls) ◄─────────────────┘
                      │
                      ▼
          ┌──► Composer ──► Critic ──(issue + safe repair)──┐
          └─────────────────────────────────────────────────┘
                      │
                      ▼
          awaiting_approval ──(feedback)──► revise ──► ...
                      │
                (human approves) ─► approved, export .ics

Nothing is ever booked or paid for; approval only exports the itinerary.
"""
from __future__ import annotations

import copy
import re
import uuid
from datetime import date
from typing import Optional

import llm
from agents import composer, critic, feedback, intake, research
from agents.composer import Constraints
from schemas import SessionState, TraceStep
import tools
from tools import resolve_city

MAX_REPAIRS = 5
RESEARCH_FIELDS = {"origin", "destination", "start_date", "nights", "travelers", "transport", "interests"}


class Session:
    def __init__(self, today: Optional[date] = None):
        self.state = SessionState(session_id=uuid.uuid4().hex[:12],
                                  mode="llm" if llm.available() else "demo")
        self.constraints = Constraints()
        self.today = today or date.today()
        self.provided: set[str] = set()  # spec fields the human has stated at some point

    def log(self, step: TraceStep):
        self.state.trace.append(step)

    # ------------------------------------------------------------ entry point
    def handle(self, message: str) -> SessionState:
        s = self.state
        s.history.append({"role": "user", "content": message})
        if s.status == "approved":
            self.log(TraceStep(agent="Orchestrator", action="ignored", detail="plan already approved"))
        elif s.status == "awaiting_approval":
            self._feedback(message)
        else:
            self._intake(message)
        return s

    # ---------------------------------------------------------------- intake
    def _intake(self, message: str, merge_interests: bool = False):
        s = self.state
        fields, method = intake.extract(message, self.today)
        # A bare city answering "Where are you leaving from?" is the origin, not a new destination.
        asked_origin = any("leaving from" in q for q in s.questions)
        if asked_origin and "origin" not in fields and fields.get("destination") and s.spec.destination \
                and fields["destination"] != s.spec.destination:
            fields["origin"] = fields.pop("destination")
        if merge_interests and "interests" in fields:
            fields["interests"] = sorted(set(s.spec.interests) | set(fields["interests"]))
        self.provided |= fields.keys()
        s.spec = intake.apply_defaults(intake.merge(s.spec, fields), self.provided)
        self.log(TraceStep(agent="Intake", action=f"parsed request ({method})",
                           detail=", ".join(f"{k}={v}" for k, v in fields.items()) or "nothing new"))
        s.questions = intake.validate(s.spec, self.today)
        if s.questions:
            s.status = "needs_clarification"
            self.log(TraceStep(agent="Intake", action="ask human", detail=" | ".join(s.questions)))
            return
        self._plan(research_again=True)

    # ------------------------------------------------------------- planning
    def _plan(self, research_again: bool, target: Optional[float] = None):
        """`target` is a temporary price ceiling (used when the human asks for "cheaper")."""
        s = self.state
        if research_again or not s.research:
            s.research = research.run(s.spec, self.log)
        # Critic repairs work on a copy so they never outlive this plan
        # (e.g. raising the budget later lets the better hotel back in).
        c = copy.deepcopy(self.constraints)
        budget = min(filter(None, [target, s.spec.budget_usd]), default=None)
        repairs = 0
        while True:
            plan = composer.compose(s.spec, s.research, c)
            issues = critic.check(s.spec, plan, s.research, budget)
            self.log(TraceStep(agent="Critic", action="review",
                               detail=f"${plan.total_cost:,.0f} total; " + ("; ".join(issues) or "no issues")))
            move = critic.next_repair(issues, c, plan) if repairs < MAX_REPAIRS else None
            if not move:
                break
            repairs += 1
            self.log(TraceStep(agent="Critic", action="revise", detail=move))
        if target:
            self.constraints = c  # the human asked for cheaper: keep those savings
            if any(i.startswith("over_budget") for i in issues):
                self.log(TraceStep(agent="Critic", action="cannot go cheaper",
                                   detail=f"lowest found ${plan.total_cost:,.0f}"))
            issues = critic.check(s.spec, plan, s.research)
        plan.revisions = repairs
        plan.issues = issues
        plan.summary = composer.summarize(s.spec, plan, self.log)
        s.plan = plan
        s.status = "awaiting_approval"
        s.questions = self._escalations(issues)
        if target and plan.total_cost >= target:
            s.questions.append(f"${plan.total_cost:,.0f} is already the cheapest plan I can build "
                               "without dropping the hotel or shortening the trip.")
        if s.questions:
            self.log(TraceStep(agent="Orchestrator", action="escalate to human", detail=" | ".join(s.questions)))

    def _escalations(self, issues: list[str]) -> list[str]:
        """Human-in-the-loop decision point #2: problems the agents must not decide alone."""
        s, qs = self.state, []
        if any(i.startswith("over_budget") for i in issues):
            gap = s.plan.total_cost - s.spec.budget_usd
            n = max(s.spec.nights - 1, 0)
            opts = ["raise the budget", "make it a day trip" if n == 0 else f"shorten to {n} night{'s' if n > 1 else ''}"]
            if s.spec.transport == "fly":
                opts.append("drive instead of flying")
            qs.append(f"The cheapest plan I can build is ${s.plan.total_cost:,.0f}, "
                      f"${gap:,.0f} over your ${s.spec.budget_usd:,.0f} budget. Would you like to "
                      + ", ".join(opts[:-1]) + f", or {opts[-1]}?")
        if any(i.startswith("no_flight") for i in issues):
            qs.append("I couldn't find flights for that route/date. Try another date, or drive?")
        if any(i.startswith("no_hotel") for i in issues):
            qs.append("No hotel matched. Allow a higher hotel tier?")
        full_days = s.plan.days[1:-1] if len(s.plan.days) > 2 else []
        light = [d for d in full_days if sum(it["kind"] in ("attraction", "event") for it in d.items) <= 1]
        if light and not any(i.startswith("over_budget") for i in issues):
            dates = ", ".join(f"{d.date:%a %b %d}" for d in light)
            example = f"\"another {s.spec.activities[0]} day\"" if s.spec.activities else "\"snorkeling\" or \"hiking\""
            qs.append(f"{dates} {'is' if len(light) == 1 else 'are'} light: I've used the best options I found in "
                      f"{s.spec.destination}. Say \"add more activities\" and I'll search wider, name an activity "
                      f"(e.g. {example}), or keep {'it' if len(light) == 1 else 'them'} free.")
        road = tools.drive_route(s.spec.origin, s.spec.destination) if s.spec.transport == "drive" else None
        if road and road["hours"] > 9:
            qs.append(f"Driving {s.spec.origin} → {s.spec.destination} is about {road['hours']:.0f} hours "
                      f"({road['km']} km) each way, so your first and last days are on the road. "
                      "Keep driving, or say \"I'll fly\" and I'll price flights instead?")
        rough = [d for d in s.plan.days if d.condition in ("freezing", "snowy", "cold")]
        if rough and not qs:
            coldest = min(rough, key=lambda d: d.high_c if d.high_c is not None else 99)
            qs.append(f"Heads-up: expect {coldest.condition} weather (around {coldest.weather}, sunset {coldest.sunset}). "
                      "I put indoor stops first and kept outdoor time short. Pack warm layers.")
        if any(i.startswith("empty") for i in issues):
            qs.append("I found no activities for this city. Want me to plan a different city?")
        return qs

    # -------------------------------------------------------------- feedback
    def _feedback(self, message: str):
        s, c = self.state, self.constraints
        current = _activity_names(s.plan)
        ops, method = feedback.parse(message, current)
        if ops.get("approve"):
            s.status = "approved"
            accepted = f"; human accepted open issues: {'; '.join(s.plan.issues)}" if s.plan.issues else ""
            s.questions = []
            self.log(TraceStep(agent="Orchestrator", action="human approved",
                               detail="itinerary exported; nothing booked automatically" + accepted))
            return
        moves, notes, target = [], [], None
        stated_budget = intake.rule_extract(message, self.today, feedback=True).get("budget_usd")
        if ops.get("cheaper") and not (stated_budget and stated_budget > (s.spec.budget_usd or 0)):
            target = s.plan.total_cost - 1
            moves.append(f"cheaper: target below ${s.plan.total_cost:,.0f}")
        if ops.get("different_hotel") and s.plan.hotel:
            c.excluded.add(s.plan.hotel["name"])
            moves.append(f"exclude hotel {s.plan.hotel['name']}")
        if ops.get("different_flight") and s.plan.flight:
            c.excluded.add(s.plan.flight["airline"])
            moves.append(f"exclude airline {s.plan.flight['airline']}")
        if ops.get("upgrade_hotel"):
            c.max_hotel_tier = "luxury"
            s.spec.hotel_preference = "luxury"
            moves.append("upgrade hotel")
        for name in ops.get("remove_places", []):
            hit = _match(name, current)
            if hit:
                c.excluded.add(hit)
                c.must_include.discard(hit)
                moves.append(f"remove {hit}")
        if ops.get("fill"):
            found = research.widen(s.spec, s.research, self.log, want=len(_candidates(s.research)) + 8)
            if c.pace == "relaxed":
                c.pace = "normal"
            moves.append(f"fill empty time ({found} more places found)")
            if not found:
                notes.append(f"I've searched widely and used what I found in {s.spec.destination}. "
                              "Name an activity (e.g. \"snorkeling\", \"whale watching\", \"hiking\") and I'll look for it.")
        if ops.get("pace") and ops["pace"] != c.pace:
            c.pace = ops["pace"]
            moves.append(f"pace → {c.pace}")
        for tag in ops.get("less", []):
            c.boost[tag] = c.boost.get(tag, 0) - 3
            moves.append(f"less {tag}")
        if ops.get("activities"):  # "ski" is the request; "more outdoors" is just what it implies
            ops["more"] = [t for t in ops.get("more", []) if t not in ("outdoors", "nature", "winter")]
        for tag in ops.get("more", []):
            c.boost[tag] = c.boost.get(tag, 0) + 2
            moves.append(f"more {tag}")
            unused = [a for a in _candidates(s.research) if tag in a.get("tags", [])
                      and a["name"] not in current and a["name"] not in c.excluded]
            if len(unused) < 2:  # not enough left to add: go find more
                research.search_more(s.spec, s.research, MORE_QUERIES.get(tag, f"{tag}s"), self.log)
        for act in ops.get("activities", []):
            planned = next(((d, it) for d in s.plan.days for it in d.items if it.get("activity") == act), None)
            again = re.search(r"\b(another|second|one more|extra|again|two|2)\b", message.lower())
            if act in s.spec.activities and planned and again:
                s.spec.activities = s.spec.activities + [act]  # one more day of it
                moves.append(f"add another {act} day")
                continue
            if act in s.spec.activities and planned:
                d, it = planned
                notes.append(f"{act.capitalize()} is already in your plan: {it['name']} on {d.date:%a %b %d} "
                             f"at {it['start']}. Want a different place or day? Tell me which.")
                continue
            if act not in s.spec.activities:
                s.spec.activities = s.spec.activities + [act]
            found = s.research.get(f"activity:{act}") or research.search_activity(s.spec, s.research, act, self.log)
            if found:
                moves.append(f"add {act}: {found[0]['name']} ({found[0]['km_from_city']} km)")
            else:
                radius = tools.D.ACTIVITIES[act][1]
                notes.append(f"I couldn't find anywhere for {act} within {radius} km of {s.spec.destination}.")
        for name in ops.get("add_places", []):
            hit = _match(name, [a["name"] for a in _candidates(s.research)])
            if not hit:
                found = research.search_more(s.spec, s.research, name, self.log, limit=3)
                # Only accept a result that is actually the place they named, never a random nearby one.
                hit = _match(name, [a["name"] for a in found])
            if hit:
                c.must_include.add(hit)
                c.excluded.discard(hit)
                moves.append(f"add {hit}")
            else:
                notes.append(f"I couldn't find \"{name}\" in {s.spec.destination}.")

        before = s.spec.model_dump()
        fields, _ = intake.extract(message, self.today, feedback=True)
        old, new = resolve_city(s.spec.destination or ""), resolve_city(fields.get("destination") or "")
        if old and new and old["name"] == new["name"]:
            fields.pop("destination")  # "New York" → "New York City" is not a change
        if "interests" in fields:
            fields["interests"] = sorted(set(s.spec.interests) | set(fields["interests"]))
        fields.pop("activities", None)  # handled above as edit operations (keeps "another ski day")
        if re.search(r"\bi'?ll drive\b|\bdrive instead\b|\bwe'?ll drive\b", message.lower()):
            fields["transport"] = "drive"
        elif re.search(r"\b(i'?ll|we'?ll|let'?s) fly\b|\bfly instead\b|\b(take a|by) (plane|flight)\b", message.lower()):
            fields["transport"] = "fly"
        self.provided |= fields.keys()
        s.spec = intake.apply_defaults(intake.merge(s.spec, fields), self.provided)
        changed = {k for k in fields if before.get(k) != s.spec.model_dump().get(k)}
        self.log(TraceStep(agent="Feedback", action=f"interpreted feedback ({method})",
                           detail="; ".join(moves + [f"{k}→{getattr(s.spec, k)}" for k in sorted(changed)])
                           or "no actionable change found"))
        if not moves and not changed:
            s.plan.changes = []
            s.questions = notes or ["I wasn't sure what to change. Try e.g. \"more museums\", \"slower pace\", "
                                    "\"skip Central Park\", \"cheaper\", \"budget is $900\", or \"approve\"."]
            return
        s.questions = intake.validate(s.spec, self.today)
        if s.questions:
            s.status = "needs_clarification"
            return
        if "destination" in changed:
            c.previous, c.must_include, c.previous_day = set(), set(), {}
        else:
            c.previous = set(current)  # revise the current plan instead of starting over
            c.previous_day = {it["name"]: i for i, d in enumerate(s.plan.days) for it in d.items
                              if it["kind"] == "attraction" and not it.get("activity")}
            if ops.get("fill"):
                c.previous_day = {}  # filling the trip: keep every stop, but regroup days by area
        c.demote = set()
        wanted = ops.get("more", [])
        c.sticky = 5.0 if wanted else 0.6  # "more X": keep what's there, fit X into the gaps first
        original = copy.deepcopy(s.plan)
        self._plan(research_again=bool(changed & RESEARCH_FIELDS), target=target)
        for _ in range(3):  # no room for X? drop the least relevant existing stop and try again
            if not wanted or self._added_with_tag(current, wanted):
                break
            victim = self._least_relevant(current, c)
            if not victim:
                break
            c.demote.add(victim)
            self.log(TraceStep(agent="Composer", action="make room",
                               detail=f"no time left for more {'/'.join(wanted)}; dropping {victim}"))
            self._plan(research_again=False, target=target)
        c.sticky, c.demote = 0.6, set()
        if wanted and not self._added_with_tag(current, wanted):
            if all(m.startswith("more ") for m in moves) and changed <= {"interests"}:
                s.plan = original  # nothing gained: don't leave the reshuffle behind
                self.log(TraceStep(agent="Composer", action="kept plan", detail="no room gained; plan unchanged"))
            notes.append(f"I couldn't fit more {'/'.join(wanted)} in: every one I found in {s.spec.destination} "
                         "is already in your plan. Want me to add a day?")
        new = _activity_names(s.plan)
        s.plan.changes = [f"+ {n}" for n in new if n not in current] + [f"− {n}" for n in current if n not in new]
        self.log(TraceStep(agent="Composer", action="revised plan", detail=", ".join(s.plan.changes) or "no changes"))
        s.questions = notes + s.questions

    def _added_with_tag(self, before: list[str], tags: list[str]) -> bool:
        tagged = {a["name"] for a in _candidates(self.state.research) if set(a.get("tags", [])) & set(tags)}
        return any(n in tagged and n not in before for n in _activity_names(self.state.plan))

    def _least_relevant(self, before: list[str], c: Constraints):
        """The current stop that matters least to this traveler (no interest match, not asked for)."""
        info = {a["name"]: a for a in _candidates(self.state.research)}
        keep = set(self.state.spec.interests) | {t for t, w in c.boost.items() if w > 0}
        pool = [n for n in _activity_names(self.state.plan)
                if n in info and n in before and n not in c.must_include and n not in c.demote]
        if not pool:
            return None
        return min(pool, key=lambda n: (len(set(info[n].get("tags", [])) & keep), info[n].get("hours", 2)))


MORE_QUERIES = {"museum": "museums", "art": "art museums and galleries", "history": "historic sites",
                "nature": "parks and gardens", "outdoors": "parks", "food": "food markets",
                "architecture": "architecture landmarks", "science": "science museums",
                "family": "family attractions", "shopping": "shopping streets", "landmark": "landmarks"}


def _activity_names(plan) -> list[str]:
    return [it["name"] for d in plan.days for it in d.items if it["kind"] in ("attraction", "event")] if plan else []


def _candidates(research_results: dict) -> list[dict]:
    return [a for a in research_results.get("search_attractions") or [] if isinstance(a, dict) and "name" in a]


def _match(name: str, options: list[str]):
    """The option that is the place the traveler named: exact, contained, or all its key words present."""
    n = name.lower().strip()
    words = lambda x: set(re.findall(r"[a-z0-9]+", x.lower())) - {"the", "a", "of", "at", "in", "and", "park", "museum"}
    return next((o for o in options if n == o.lower()), None) or \
        next((o for o in options if n in o.lower() or o.lower() in n), None) or \
        next((o for o in options if words(name) and words(name) <= words(o)), None)


SESSIONS: dict[str, Session] = {}


def new_session(today: Optional[date] = None) -> Session:
    sess = Session(today)
    SESSIONS[sess.state.session_id] = sess
    return sess
