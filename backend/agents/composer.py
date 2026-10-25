"""Composer agent: turns research results into a priced, day-by-day plan.

Selection and scheduling are deterministic (so cost math is always right);
the LLM, when available, only writes the friendly summary.
"""
from __future__ import annotations

import math
from datetime import timedelta
from typing import Optional

import llm
from schemas import DayPlan, Plan, TraceStep, TripSpec
from tools import resolve_city

FOOD_PER_DAY = {"budget": 45, "mid": 70, "luxury": 120, "any": 70}
LOCAL_TRANSIT_PER_DAY = 15
TIER_ORDER = ["budget", "mid", "luxury"]


class Constraints:
    """Knobs the Critic (or human feedback) can turn when asking for a revision."""

    def __init__(self):
        self.max_hotel_tier = "luxury"
        self.cheapest_flight = False
        self.skip_paid_events = False
        self.free_attractions_only = False
        self.excluded: set[str] = set()


def _ok(rows) -> list:
    return [r for r in rows or [] if isinstance(r, dict) and "error" not in r]


def pick_flight(flights: list, c: Constraints) -> Optional[dict]:
    flights = [f for f in _ok(flights) if f.get("airline") not in c.excluded]
    if not flights:
        return None
    if c.cheapest_flight:
        return min(flights, key=lambda f: f["price_per_person"])
    # Prefer daytime departures within 25% of the cheapest fare.
    cheapest = min(f["price_per_person"] for f in flights)
    good = [f for f in flights if f["price_per_person"] <= cheapest * 1.25
            and 8 <= int(f["departure_time"][11:13]) <= 18]
    return min(good or flights, key=lambda f: f["price_per_person"])


def pick_hotel(hotels: list, spec: TripSpec, c: Constraints) -> Optional[dict]:
    hotels = [h for h in _ok(hotels) if h["name"] not in c.excluded]
    max_i = TIER_ORDER.index(c.max_hotel_tier)
    allowed = [h for h in hotels if TIER_ORDER.index(h.get("tier", "mid")) <= max_i]
    if not allowed:
        return None
    pref = spec.hotel_preference if spec.hotel_preference != "any" else "mid"
    pref = TIER_ORDER[min(TIER_ORDER.index(pref), max_i)]
    same = [h for h in allowed if h.get("tier") == pref]
    pool = same or allowed
    return max(pool, key=lambda h: (h.get("rating", 0), -h["nightly_price"]))


def compose(spec: TripSpec, research: dict, c: Constraints) -> Plan:
    plan = Plan()
    travelers = spec.travelers
    rooms = math.ceil(travelers / 2)
    days_n = spec.nights + 1

    if spec.transport == "fly":
        plan.flight = pick_flight(research.get("search_flights"), c)
    if spec.nights > 0:
        plan.hotel = pick_hotel(research.get("search_hotels"), spec, c)

    weather = {w["date"]: w for w in _ok(research.get("get_weather"))}
    attractions = [a for a in _ok(research.get("search_attractions")) if a["name"] not in c.excluded]
    if c.free_attractions_only:
        attractions = [a for a in attractions if not a.get("cost_per_person")]
    events = [e for e in _ok(research.get("search_events")) if e["name"] not in c.excluded]
    if c.skip_paid_events:
        events = [e for e in events if not e.get("price_per_person")]
    interests = set(spec.interests)

    used: set[str] = set()
    for i in range(days_n):
        day = spec.start_date + timedelta(days=i)
        w = weather.get(day.isoformat())
        rainy = bool(w and (w.get("rain_chance") or 0) >= 60)
        capacity = 8 if days_n == 1 else (4 if i in (0, days_n - 1) else 8)
        dp = DayPlan(date=day, weather=(f"{w['high_c']}°C, {w['rain_chance']}% rain" if w else None),
                     rain_chance=w.get("rain_chance") if w else None)
        # Rainy days put indoor sights first; otherwise keep interest ranking.
        ranked = sorted(attractions, key=lambda a: ((not a.get("indoor")) if rainy else False,
                                                    -a.get("match", 0)))
        hours = 0.0
        for a in ranked:
            if a["name"] in used or hours + a.get("hours", 2) > capacity:
                continue
            used.add(a["name"])
            hours += a.get("hours", 2)
            dp.items.append({"kind": "attraction", "name": a["name"], "hours": a.get("hours", 2),
                             "indoor": a.get("indoor"), "lat": a.get("lat"), "lng": a.get("lng"),
                             "cost": (a.get("cost_per_person") or 0) * travelers, "source": a.get("source")})
        for e in events:
            if e["date"] == day.isoformat() and e["name"] not in used and \
                    (not interests or interests & set(e.get("tags", []))):
                used.add(e["name"])
                dp.items.append({"kind": "event", "name": e["name"], "time": e.get("time"),
                                 "cost": (e.get("price_per_person") or 0) * travelers,
                                 "url": e.get("url"), "source": e.get("source")})
                break  # at most one evening event per day
        plan.days.append(dp)

    # ---- costs
    cb: dict[str, float] = {}
    if plan.flight:
        cb["flights"] = plan.flight["price_per_person"] * travelers
    if spec.transport == "drive":
        o, d = resolve_city(spec.origin), resolve_city(spec.destination)
        hours = (d or {}).get("drive_hours") or 4
        cb["gas_and_tolls"] = round(hours * 60 * 2 * 0.18 + 20)
        cb["parking"] = 35 * spec.nights
    if plan.hotel:
        cb["hotel"] = plan.hotel["nightly_price"] * spec.nights * rooms
    cb["activities"] = sum(it["cost"] for d in plan.days for it in d.items)
    cb["food_estimate"] = FOOD_PER_DAY[spec.hotel_preference] * days_n * travelers
    cb["local_transit_estimate"] = LOCAL_TRANSIT_PER_DAY * days_n * travelers
    plan.cost_breakdown = {k: round(v, 2) for k, v in cb.items()}
    plan.total_cost = round(sum(cb.values()), 2)
    return plan


def summarize(spec: TripSpec, plan: Plan, log=None) -> str:
    highlights = [it["name"] for d in plan.days for it in d.items][:5]
    fallback = (f"{spec.nights + 1}-day trip to {spec.destination} from {spec.start_date:%b %d}"
                + (f", staying at {plan.hotel['name']}" if plan.hotel else "")
                + (f", flying {plan.flight['airline']}" if plan.flight else "")
                + f". Highlights: {', '.join(highlights)}. Estimated total ${plan.total_cost:,.0f}"
                + (f" (budget ${spec.budget_usd:,.0f})." if spec.budget_usd else "."))
    if not llm.available():
        return fallback
    try:
        msg = llm.chat([
            {"role": "system", "content": "Write a warm 3-sentence trip summary. Use ONLY facts given; do not add places or prices."},
            {"role": "user", "content": fallback + "\nDay plan:\n" + "\n".join(
                f"{d.date}: " + "; ".join(it["name"] for it in d.items) for d in plan.days)}],
            temperature=0.5, max_tokens=250)
        return (msg.content or fallback).strip()
    except Exception as e:
        if log:
            log(TraceStep(agent="Composer", action="LLM summary failed, using template",
                          detail=f"{type(e).__name__}: {e}"[:160]))
        return fallback
