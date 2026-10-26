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
from agents import composer, critic, intake, research
from agents.composer import Constraints
from schemas import SessionState, TraceStep
from tools import resolve_city

MAX_REPAIRS = 5
APPROVE_RE = re.compile(r"^\s*(approve|approved|looks good|lgtm|confirm|perfect)\b", re.I)
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
        s, c, t = self.state, self.constraints, message.lower()
        if APPROVE_RE.search(message):
            s.status = "approved"
            accepted = f"; human accepted open issues: {'; '.join(s.plan.issues)}" if s.plan.issues else ""
            s.questions = []
            self.log(TraceStep(agent="Orchestrator", action="human approved",
                               detail="itinerary exported; nothing booked automatically" + accepted))
            return
        moves, target = [], None
        if re.search(r"\b(cheaper|too expensive|save money|lower cost)\b", t):
            target = s.plan.total_cost - 1
            moves.append(f"cheaper: target below ${s.plan.total_cost:,.0f}")
        if re.search(r"\b(different|another|other|change the) hotel\b|don'?t like the hotel", t) and s.plan.hotel:
            c.excluded.add(s.plan.hotel["name"])
            moves.append(f"exclude hotel {s.plan.hotel['name']}")
        if re.search(r"\b(different|another|other|change the) (flight|airline)\b", t) and s.plan.flight:
            c.excluded.add(s.plan.flight["airline"])
            moves.append(f"exclude airline {s.plan.flight['airline']}")
        if re.search(r"\b(nicer|better|upgrade|luxury) hotel\b", t):
            c.max_hotel_tier = "luxury"
            s.spec.hotel_preference = "luxury"
            moves.append("upgrade hotel")
        for d in s.plan.days:
            for it in d.items:
                key = next((w for w in re.findall(r"[a-z]+", it["name"].lower())
                            if len(w) > 3 and w not in {"the", "museum", "national", "park"}), None)
                if key and re.search(rf"\b(skip|remove|drop|without|no)\b[^.,;]*\b{re.escape(key)}", t):
                    c.excluded.add(it["name"])
                    moves.append(f"remove {it['name']}")
        before = s.spec.model_dump()
        fields, method = intake.extract(message, self.today, feedback=True)
        old, new = resolve_city(s.spec.destination or ""), resolve_city(fields.get("destination") or "")
        if old and new and old["name"] == new["name"]:
            fields.pop("destination")  # "New York" → "New York City" is not a change
        if "interests" in fields:
            fields["interests"] = sorted(set(s.spec.interests) | set(fields["interests"]))
        if re.search(r"\bi'?ll drive\b|\bdrive instead\b", t):
            fields["transport"] = "drive"
        self.provided |= fields.keys()
        s.spec = intake.apply_defaults(intake.merge(s.spec, fields), self.provided)
        changed = {k for k in fields if before.get(k) != s.spec.model_dump().get(k)}
        self.log(TraceStep(agent="Feedback", action=f"interpreted feedback ({method})",
                           detail="; ".join(moves + [f"{k}→{getattr(s.spec, k)}" for k in sorted(changed)])
                           or "no actionable change found"))
        if not moves and not changed:
            s.questions = ["I wasn't sure what to change. Try e.g. \"cheaper\", \"different hotel\", "
                           "\"skip Central Park\", \"budget is $900\", or \"approve\"."]
            return
        s.questions = intake.validate(s.spec, self.today)
        if s.questions:
            s.status = "needs_clarification"
            return
        self._plan(research_again=bool(changed & RESEARCH_FIELDS), target=target)


SESSIONS: dict[str, Session] = {}


def new_session(today: Optional[date] = None) -> Session:
    sess = Session(today)
    SESSIONS[sess.state.session_id] = sess
    return sess
