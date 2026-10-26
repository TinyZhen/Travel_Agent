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
        if ops.get("pace") and ops["pace"] != c.pace:
            c.pace = ops["pace"]
            moves.append(f"pace → {c.pace}")
        for tag in ops.get("less", []):
            c.boost[tag] = c.boost.get(tag, 0) - 3
            moves.append(f"less {tag}")
        for tag in ops.get("more", []):
            c.boost[tag] = c.boost.get(tag, 0) + 2
            moves.append(f"more {tag}")
            unused = [a for a in _candidates(s.research) if tag in a.get("tags", [])
                      and a["name"] not in current and a["name"] not in c.excluded]
            if len(unused) < 2:  # not enough left to add: go find more
                research.search_more(s.spec, s.research, MORE_QUERIES.get(tag, f"{tag}s"), self.log)
        for name in ops.get("add_places", []):
            hit = _match(name, [a["name"] for a in _candidates(s.research)])
            if not hit:
                found = research.search_more(s.spec, s.research, name, self.log, limit=1)
                hit = found[0]["name"] if found else None
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
        if re.search(r"\bi'?ll drive\b|\bdrive instead\b", message.lower()):
            fields["transport"] = "drive"
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
            c.previous, c.must_include = set(), set()
        else:
            c.previous = set(current)  # revise the current plan instead of starting over
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
            if all(m.startswith("more ") for m in moves) and not changed:
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
    n = name.lower().strip()
    return next((o for o in options if n == o.lower()), None) or \
        next((o for o in options if n in o.lower() or o.lower() in n), None)


SESSIONS: dict[str, Session] = {}


def new_session(today: Optional[date] = None) -> Session:
    sess = Session(today)
    SESSIONS[sess.state.session_id] = sess
    return sess
