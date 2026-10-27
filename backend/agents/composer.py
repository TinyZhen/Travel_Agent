"""Composer agent: turns research results into a priced, day-by-day plan.

Selection and scheduling are deterministic (so cost math is always right);
the LLM, when available, only writes the friendly summary.
"""
from __future__ import annotations

import math
from urllib.parse import quote_plus
from datetime import timedelta
from typing import Optional

import llm
from schemas import DayPlan, Plan, TraceStep, TripSpec
from tools import _haversine_km, drive_hours, resolve_city

FOOD_PER_DAY = {"budget": 45, "mid": 70, "luxury": 120, "any": 70}
LOCAL_TRANSIT_PER_DAY = 15
TIER_ORDER = ["budget", "mid", "luxury"]


class Constraints:
    """Knobs the Critic (or human feedback) can turn when asking for a revision."""

    def __init__(self):
        self.max_hotel_tier = "luxury"
        self.cheapest_flight = False
        self.skip_paid_events = False
        self.free_attractions_only = False   # free sights + the 2 paid ones that best match interests
        self.free_attractions_strict = False  # free sights only
        self.excluded: set[str] = set()
        # Set by human feedback:
        self.boost: dict[str, float] = {}     # tag -> extra weight ("more museums", "less walking outdoors")
        self.pace = "normal"                  # relaxed | normal | packed
        self.must_include: set[str] = set()   # places the traveler asked for by name
        self.previous: set[str] = set()       # items of the plan being revised (keep edits minimal)
        self.sticky = 0.6                     # how strongly to keep previous items
        self.demote: set[str] = set()         # previous items we chose to drop to make room
        self.weather_strict = False           # Critic: bad-weather days must avoid outdoor stops


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
    return max(pool, key=lambda h: (h.get("rating") or 0, -h["nightly_price"]))


CAR_ACTIVITIES = {"skiing", "hiking", "snow tubing", "kayaking", "beach", "golf"}  # tours usually pick you up
PACE_END = {"relaxed": "17:00", "normal": "18:30", "packed": "20:00"}
PACE_START = {"relaxed": "10:00", "normal": "09:30", "packed": "08:30"}


def _hm(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _fmt(minutes: float) -> str:
    minutes = int(round(minutes / 5) * 5)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _leg(a: Optional[dict], b: dict) -> Optional[dict]:
    """Walking if close, otherwise public transit; rough city-travel model."""
    if not a or a.get("lat") is None or b.get("lat") is None:
        return None
    km = _haversine_km(a, b) * 1.3
    if km > 25:  # out of town (ski areas, state parks): you'll need a car
        return {"mode": "drive", "km": round(km), "minutes": round((10 + km / 60 * 60) / 5) * 5}
    if km <= 1.6:
        return {"mode": "walk", "km": round(km, 1), "minutes": max(5, round(km / 4.8 * 60 / 5) * 5)}
    return {"mode": "transit", "km": round(km, 1), "minutes": round((10 + km / 24 * 60) / 5) * 5}


def conditions(w: Optional[dict]) -> dict:
    """What the day's weather means for planning."""
    if not w:
        return {"label": None, "bad": False, "cold": False}
    hi, rain, snow = w.get("high_c", 15), w.get("rain_chance") or 0, w.get("snow_cm") or 0
    snowy = snow >= 1 or (rain >= 60 and hi <= 2)
    label = ("freezing" if hi <= -3 else "snowy" if snowy else "cold" if hi <= 5
             else "rainy" if rain >= 60 else "hot" if hi >= 32 else None)
    return {"label": label, "bad": label is not None, "cold": label in ("freezing", "snowy", "cold"),
            "sunset": _hm(w["sunset"]) if w.get("sunset") else None}
OUTDOOR_PENALTY = {"freezing": 4, "snowy": 3, "cold": 2, "rainy": 1.5, "hot": 1}


def _in_season(a: dict, month: int) -> bool:
    if not a.get("months"):
        return True
    first, last = a["months"]
    return first <= month <= last if first <= last else (month >= first or month <= last)


def _score(a: dict, c: Constraints, cond: dict) -> float:
    s = a.get("match", 0) + sum(c.boost.get(t, 0) for t in a.get("tags", []))
    if a["name"] in c.demote:
        s -= 5
    elif a["name"] in c.previous:
        s += c.sticky                               # keep revisions minimal
    s += 10 if a["name"] in c.must_include else 0
    winter = "winter" in a.get("tags", [])
    if winter:
        s += 1.5 if cond["cold"] else -3
    elif cond["bad"]:
        s += 1.5 if a.get("indoor") else -OUTDOOR_PENALTY[cond["label"]] * (4 if c.weather_strict else 1)
    return s


def _why(a: dict, spec: TripSpec, c: Constraints, cond: dict) -> str:
    if a["name"] in c.must_include:
        return "You asked for this"
    hits = [t for t in a.get("tags", []) if t in spec.interests or c.boost.get(t, 0) > 0]
    parts = [f"Matches your interest in {hits[0]}"] if hits else []
    if "winter" in a.get("tags", []) and cond["cold"]:
        parts.append("a cold-weather classic")
    elif cond["bad"] and a.get("indoor"):
        parts.append(f"indoor pick for a {cond['label']} day")
    if not a.get("cost_per_person"):
        parts.append("free")
    return "; ".join(parts) or ", ".join(a.get("tags", [])[:2]).capitalize()


def _describe(w: Optional[dict]) -> Optional[str]:
    if not w:
        return None
    s = f"high {w['high_c']}°C / low {w.get('low_c', w['high_c'] - 8)}°C"
    if (w.get("snow_cm") or 0) >= 0.5:
        s += f", snow {w['snow_cm']:g} cm"
    rain = w.get("rain_chance") or 0
    if rain:
        s += f", {rain}% chance of {'precipitation' if w['high_c'] <= 2 else 'rain'}"
    return s


CATEGORY_CAP = {"museum": 3, "park": 2, "garden": 2, "beach": 3, "tourist attraction": 4, "tour operator": 2}


def _over_cap(a: dict, spec: TripSpec, seen: dict[str, int]) -> bool:
    """A third ice rink is filler, not a plan: cap each kind of place per trip (more if it's their thing)."""
    cat = a.get("category")
    if not cat:
        return False
    cap = CATEGORY_CAP.get(cat, 1) + (2 if (a.get("tags") or [None])[0] in spec.interests else 0)
    return seen.get(cat, 0) >= cap


def maps_link(name: str, city: str) -> str:
    """A Google Maps link for any place, so every stop on the itinerary is clickable."""
    q = quote_plus(f"{name}, {city}")
    return f"https://www.google.com/maps/search/?api=1&query={q}"


def event_link(e: dict, city: str) -> Optional[str]:
    """The event's own page, or a web search for it when the source gave no link (never for sample events)."""
    if e.get("url") or e.get("source") == "demo":
        return e.get("url")
    return "https://www.google.com/search?q=" + quote_plus(f"{e['name']} {city} {e.get('date', '')} tickets")


def food_link(near: Optional[dict]) -> Optional[str]:
    if not near or near.get("lat") is None:
        return None
    return f"https://www.google.com/maps/search/restaurants/@{near['lat']},{near['lng']},16z"


def _fill_gaps(items: list[dict], cond: Optional[dict] = None) -> list[dict]:
    """Make long idle stretches explicit instead of leaving silent holes in the day."""
    out = []
    for it in items:
        if out and out[-1].get("end") and it.get("start"):
            gap_start = _hm(out[-1]["end"])
            gap_end = _hm(it["start"]) - ((it.get("travel") or {}).get("minutes") or 0)
            if gap_end - gap_start >= 90:
                near = next((x["name"] for x in reversed(out) if x["kind"] == "attraction"), None)
                warm = cond and cond.get("cold")
                out.append({"kind": "free", "name": ("Warm up indoors: café or shops" if warm else "Free time")
                            + (f" near {near}" if near else ""),
                            "start": _fmt(gap_start), "end": _fmt(gap_end)})
        out.append(it)
    return out


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
        must_see = [a["name"] for a in attractions if a.get("cost_per_person") and a.get("match", 0) > 0][:2]
        if c.free_attractions_strict:
            must_see = []
        attractions = [a for a in attractions if not a.get("cost_per_person") or a["name"] in must_see
                       or a["name"] in c.must_include]
    events = [e for e in _ok(research.get("search_events")) if e["name"] not in c.excluded]
    if c.skip_paid_events:  # unknown price counts as paid
        events = [e for e in events if e.get("price_per_person") == 0]
    interests = set(spec.interests) | {t for t, w in c.boost.items() if w > 0}

    city = resolve_city(spec.destination) or {}
    base = plan.hotel if plan.hotel and plan.hotel.get("lat") is not None else \
        {"name": "city centre", "lat": city.get("lat"), "lng": city.get("lng")}
    used: set[str] = set()
    seen: dict[str, int] = {}  # place categories already in the trip (ice rink, zoo, market…)
    # Activities the traveler asked for get a day of their own choosing: a full day if possible
    # (skiing: the coldest one), and the best-rated nearby place.
    activity_day: dict[int, dict] = {}
    for act in spec.activities:  # an activity can appear twice: "another ski day"
        taken = {a["name"] for a in activity_day.values() if a.get("activity") != act}
        # different activities go to different places (one operator may offer both snorkeling and whales)
        options = [a for a in research.get(f"activity:{act}") or [] if a["name"] not in c.excluded
                   and a["name"] not in taken]
        if not options:
            continue
        full = [j for j in range(days_n) if days_n == 1 or 0 < j < days_n - 1] or list(range(days_n))
        free = [j for j in full if j not in activity_day]
        if not free:
            continue  # no full day left for it
        if "winter" in options[0].get("tags", []):
            free.sort(key=lambda j: (weather.get((spec.start_date + timedelta(days=j)).isoformat()) or {}).get("high_c", 0))
        activity_day[free[0]] = options[0]
    for i in range(days_n):
        day = spec.start_date + timedelta(days=i)
        w = weather.get(day.isoformat())
        cond = conditions(w)
        dp = DayPlan(date=day, weather=_describe(w), rain_chance=w.get("rain_chance") if w else None,
                     high_c=w.get("high_c") if w else None, low_c=w.get("low_c") if w else None,
                     snow_cm=w.get("snow_cm") if w else None, sunset=w.get("sunset") if w else None,
                     condition=cond["label"], weather_basis=w.get("source") if w else None)
        clock, end = _hm(PACE_START[c.pace]), _hm(PACE_END[c.pace])

        # ---- arrival / departure logistics
        if i == 0 and plan.flight:
            arr = _hm(plan.flight["arrival_time"][11:16])
            dp.items.append({"kind": "arrival", "name": f"Land at {plan.flight['to']} ({plan.flight['airline']})",
                             "start": _fmt(arr), "end": _fmt(arr)})
            clock = arr + 60
        elif i == 0 and spec.transport == "drive":
            hours = drive_hours(spec.origin, spec.destination) or 4
            dp.items.append({"kind": "arrival", "name": f"Drive from {spec.origin} (~{hours:.0f}h)",
                             "start": "08:00", "end": _fmt(480 + hours * 60)})
            clock = 480 + hours * 60 + 15
        if i == 0 and plan.hotel:
            dp.items.append({"kind": "hotel", "name": f"Drop bags at {plan.hotel['name']}",
                             "start": _fmt(clock), "end": _fmt(clock + 30), "lat": base.get("lat"),
                             "lng": base.get("lng"), "travel": None})
            clock += 30
        if i == days_n - 1 and spec.nights > 0:
            dp.items.append({"kind": "hotel", "name": "Check out, leave bags at the front desk",
                             "start": _fmt(clock), "end": _fmt(clock + 15), "lat": base.get("lat"), "lng": base.get("lng")})
            clock += 15
            end = min(end, _hm("15:00") if spec.transport != "local" else end)

        # ---- evening event decides when the day's sightseeing must end
        todays = [e for e in events if e["date"] == day.isoformat() and e["name"] not in used]
        matches = lambda e: not interests or bool(interests & set(e.get("tags", [])))
        is_day = lambda e: bool(e.get("time")) and _hm(e["time"]) < _hm("17:00")
        # A daytime event takes sightseeing time, so it must match their interests.
        daytime = next((e for e in todays if is_day(e) and matches(e)), None)
        # Evenings are free anyway: prefer a match, otherwise any event beats an empty evening.
        evening = [e for e in todays if not is_day(e)]
        event = next((e for e in evening if matches(e)), None) or \
            (evening[0] if evening and not any(matches(e) for e in events) else None)
        if event and event.get("time"):
            end = min(end, _hm(event["time"]) - 90)  # leave time for dinner first

        # ---- sights: greedy best-next (interest score minus travel time), lunch once it's past noon
        pos, lunch_done, last_sight = base, clock >= _hm("14:00"), None

        # Relaxed pace: at most 2 activities on a full day (events count), 1 on travel days.
        n_events = int(bool(event)) + int(bool(daytime))
        cap = None if c.pace != "relaxed" else max(0, (1 if i in (0, days_n - 1) and days_n > 1 else 2) - n_events)
        if c.pace != "packed" and days_n > 2:
            # Few places for a long trip: spread them out instead of cramming the first days.
            spread = max(2, math.ceil(len(attractions) / (days_n - 1)))
            cap = spread if cap is None else min(cap, spread)
        slack = 30 if c.pace == "relaxed" else 0

        def fill(limit: int) -> None:
            nonlocal clock, pos, lunch_done, last_sight
            while cap is None or sum(x["kind"] == "attraction" for x in dp.items) < cap:
                if not lunch_done and clock >= _hm("12:00"):
                    dp.items.append({"kind": "meal", "url": food_link(pos), "name": f"Lunch near {last_sight or base['name']}",
                                     "start": _fmt(clock), "end": _fmt(clock + 60), "cost": 0})
                    clock, lunch_done = clock + 60, True
                best, best_val = None, None
                for a in attractions:
                    if a["name"] in used or not _in_season(a, day.month):
                        continue
                    leg = _leg(pos, a) or {"minutes": 20}
                    finish = clock + leg["minutes"] + a.get("hours", 2) * 60
                    if finish > limit:
                        continue  # doesn't fit; maybe a shorter one does
                    daylight_only = not a.get("indoor") and {"nature", "outdoors"} & set(a.get("tags", [])) \
                        and "winter" not in a.get("tags", [])
                    if daylight_only and cond.get("sunset") and finish > cond["sunset"] + 15:
                        continue  # parks and walks after dark aren't a plan
                    if c.weather_strict and cond["bad"] and not a.get("indoor") and "winter" not in a.get("tags", []) \
                            and any(x["kind"] == "attraction" and not x.get("indoor") and not x.get("winter")
                                    for x in dp.items):
                        continue  # bad weather: at most one outdoor stop, keep the rest of the day light
                    if _over_cap(a, spec, seen) and a["name"] not in c.must_include:
                        continue
                    val = _score(a, c, cond) * 10 - leg["minutes"] * 0.25
                    if best_val is None or val > best_val:
                        best, best_val = a, val
                if not best:
                    return
                leg = _leg(pos, best) or {"minutes": 20}
                arrive, dur = clock + leg["minutes"] + slack, best.get("hours", 2) * 60
                used.add(best["name"])
                dp.items.append({"kind": "attraction", "name": best["name"], "start": _fmt(arrive),
                                 "end": _fmt(arrive + dur), "hours": best.get("hours", 2), "indoor": best.get("indoor"),
                                 "lat": best.get("lat"), "lng": best.get("lng"), "travel": _leg(pos, best),
                                 "why": _why(best, spec, c, cond), "winter": "winter" in best.get("tags", []),
                                 "cost": (best.get("cost_per_person") or 0) * travelers,
                                 "cost_estimated": best.get("cost_estimated", False),
                                 "url": best.get("url") or maps_link(best["name"], spec.destination),
                                 "source": best.get("source")})
                clock, pos, last_sight = arrive + dur, best, best["name"]
                if best.get("category"):
                    seen[best["category"]] = seen.get(best["category"], 0) + 1

        if i in activity_day:  # the thing they asked for comes first, at the start of the day
            a = activity_day[i]
            if a["name"] in used:  # second day of the same activity: same place is fine
                a = {**a, "name": f"{a['name']} (day 2)"}
            leg = _leg(pos, a) or {"minutes": 30, "mode": "drive", "km": a.get("km_from_city")}
            if a.get("activity") in CAR_ACTIVITIES and leg["mode"] != "drive":  # no bus goes up the ski hill
                leg = {"mode": "drive", "km": leg["km"], "minutes": round((10 + leg["km"] / 50 * 60) / 5) * 5}
            arrive, dur = max(clock, _hm("09:00")) + leg["minutes"], a.get("hours", 3) * 60
            used.add(a["name"])
            dp.items.append({"kind": "attraction", "name": a["name"], "start": _fmt(arrive), "end": _fmt(arrive + dur),
                             "hours": a.get("hours"), "indoor": a.get("indoor"), "lat": a.get("lat"), "lng": a.get("lng"),
                             "travel": leg, "winter": "winter" in a.get("tags", []), "activity": a.get("activity"),
                             "why": f"You asked for {a['activity']}" + (f"; {a['km_from_city']} km out of town, by car"
                                                                        if (a.get("km_from_city") or 0) > 25 else "")
                                    + ("; lift ticket + rentals est." if a.get("activity") == "skiing" else "")
                                    + ("; rain is typical that day, check conditions before you go"
                                       if cond["label"] == "rainy" and "winter" in a.get("tags", []) else ""),
                             "cost": (a.get("cost_per_person") or 0) * travelers, "cost_estimated": True,
                             "url": a.get("url") or maps_link(a["name"], spec.destination), "source": a.get("source")})
            clock, pos, last_sight = arrive + dur, a, a["name"]
            if not lunch_done and arrive < _hm("12:30") < clock:
                lunch_done = True
                dp.items[-1]["why"] += "; lunch there"
        if daytime and clock <= _hm(daytime["time"]):
            ev = _hm(daytime["time"])
            fill(ev - 30)  # sights before the event, leaving time to get there
            used.add(daytime["name"])
            dp.items.append({"kind": "event", "name": daytime["name"], "start": daytime["time"],
                             "end": _fmt(ev + 120), "why": "Daytime event matching your interests"
                             if interests & set(daytime.get("tags", [])) else "Daytime event",
                             "cost": (daytime.get("price_per_person") or 0) * travelers,
                             "price_unknown": daytime.get("price_per_person") is None,
                             "url": event_link(daytime, spec.destination), "source": daytime.get("source")})
            clock = max(clock, ev) + 120
        fill(end)
        if not lunch_done and clock > _hm("12:00") and clock < _hm("16:00"):
            dp.items.append({"kind": "meal", "url": food_link(pos), "name": f"Lunch near {last_sight or base['name']}",
                             "start": _fmt(clock), "end": _fmt(clock + 60), "cost": 0})
            clock += 60

        # ---- dinner + event, or departure
        if i == days_n - 1 and spec.transport == "fly" and spec.nights > 0:
            dp.items.append({"kind": "departure", "name": f"Head to the airport for your flight home",
                             "start": _fmt(max(clock, _hm("15:00"))), "end": _fmt(max(clock, _hm("15:00")) + 60)})
        elif i == days_n - 1 and spec.transport == "drive" and spec.nights > 0:
            dp.items.append({"kind": "departure", "name": f"Drive back to {spec.origin}",
                             "start": _fmt(max(clock, _hm("15:00"))), "end": _fmt(max(clock, _hm("15:00")) + 60)})
        else:
            if event and event.get("time"):
                ev = _hm(event["time"])
                dp.items.append({"kind": "meal", "url": food_link(pos), "name": f"Dinner near {last_sight or base['name']}",
                                 "start": _fmt(ev - 90), "end": _fmt(ev - 20), "cost": 0})
                used.add(event["name"])
                dp.items.append({"kind": "event", "name": event["name"], "start": event["time"],
                                 "end": _fmt(ev + 120), "why": "Evening event matching your interests"
                                 if interests & set(event.get("tags", [])) else "Evening event",
                                 "cost": (event.get("price_per_person") or 0) * travelers,
                                 "price_unknown": event.get("price_per_person") is None,
                                 "url": event_link(event, spec.destination), "source": event.get("source")})
            else:
                dp.items.append({"kind": "meal", "url": food_link(pos), "name": f"Dinner near {last_sight or base['name']}",
                                 "start": _fmt(max(clock + 30, _hm("19:00"))),
                                 "end": _fmt(max(clock + 30, _hm("19:00")) + 75), "cost": 0})
        dp.items = _fill_gaps(dp.items, cond)
        plan.days.append(dp)

    # ---- costs
    cb: dict[str, float] = {}
    if plan.flight:
        cb["flights"] = plan.flight["price_per_person"] * travelers
    if spec.transport == "drive":
        hours = drive_hours(spec.origin, spec.destination) or 4
        cb["gas_and_tolls"] = round(hours * 60 * 2 * 0.18 + 20)
        cb["parking"] = 35 * spec.nights
    if plan.hotel:
        cb["hotel"] = plan.hotel["nightly_price"] * spec.nights * rooms
    cb["activities"] = sum(it.get("cost", 0) for d in plan.days for it in d.items)
    cb["food_estimate"] = FOOD_PER_DAY[spec.hotel_preference] * days_n * travelers
    cb["local_transit_estimate"] = LOCAL_TRANSIT_PER_DAY * days_n * travelers
    plan.cost_breakdown = {k: round(v, 2) for k, v in cb.items()}
    plan.total_cost = round(sum(cb.values()), 2)
    return plan


def summarize(spec: TripSpec, plan: Plan, log=None) -> str:
    highlights = [it["name"] for d in plan.days for it in d.items if it["kind"] in ("attraction", "event")][:5]
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
                f"{d.date} ({d.weather or 'weather unknown'}{', sunset ' + d.sunset if d.sunset else ''}): "
                + "; ".join(it["name"] for it in d.items if it["kind"] in ("attraction", "event"))
                for d in plan.days)
             + "\nIf the weather is cold, snowy or wet, say so briefly and what to pack."}],
            temperature=0.5, max_tokens=250)
        if not msg.content:
            raise ValueError("empty reply")
        return msg.content.strip()
    except Exception as e:
        if log:
            log(TraceStep(agent="Composer", action="LLM summary failed, using template",
                          detail=f"{type(e).__name__}: {e}"[:160]))
        return fallback
