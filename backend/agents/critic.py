"""Critic agent: checks a plan against the spec and proposes the next repair.

Checks are deterministic on purpose: budget math, dates and coverage are things
an LLM should not be trusted to eyeball.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Optional

from agents.composer import TIER_ORDER, Constraints
from schemas import Plan, TripSpec


def check(spec: TripSpec, plan: Plan, research: dict, budget: Optional[float] = None) -> list[str]:
    issues = []
    budget = budget or spec.budget_usd
    if budget and plan.total_cost > budget:
        issues.append(f"over_budget: ${plan.total_cost:,.0f} > ${budget:,.0f}")
    if spec.transport == "fly" and not plan.flight:
        issues.append("no_flight: no flight option available")
    if spec.nights > 0 and not plan.hotel:
        issues.append("no_hotel: no hotel option fits the constraints")
    if plan.flight and plan.flight["departure_time"][:10] != spec.start_date.isoformat():
        issues.append(f"date_mismatch: flight departs {plan.flight['departure_time'][:10]}")
    valid_days = {spec.start_date + timedelta(days=i) for i in range(spec.nights + 1)}
    if any(d.date not in valid_days for d in plan.days):
        issues.append("date_mismatch: itinerary day outside trip dates")
    names = [it["name"] for d in plan.days for it in d.items if it["kind"] in ("attraction", "event")]
    if len(names) != len(set(names)):
        issues.append("duplicate: an item is scheduled twice")
    if plan.days and not names:
        issues.append("empty: no activities found")
    for d in plan.days:
        if (d.rain_chance or 0) >= 60 and \
                any(it["kind"] == "attraction" and not it.get("indoor") for it in d.items) and \
                not any(it.get("indoor") for it in d.items):
            issues.append(f"weather: {d.date} is rainy and has only outdoor plans")
    return issues


def next_repair(issues: list[str], c: Constraints, plan: Plan) -> Optional[str]:
    """Pick one cost-cutting move; None means we are out of safe automatic moves."""
    if not any(i.startswith("over_budget") for i in issues):
        return None
    tier = TIER_ORDER.index(plan.hotel.get("tier", "mid")) if plan.hotel else 0
    if tier > 0:
        c.max_hotel_tier = TIER_ORDER[tier - 1]
        return f"downgrade hotel to ≤ {c.max_hotel_tier}"
    if not c.cheapest_flight:
        c.cheapest_flight = True
        return "switch to cheapest flight"
    if not c.skip_paid_events:
        c.skip_paid_events = True
        return "drop paid events"
    if not c.free_attractions_only:
        c.free_attractions_only = True
        return "keep free attractions + top 2 matching your interests"
    if not c.free_attractions_strict:
        c.free_attractions_strict = True
        return "keep only free attractions"
    return None
