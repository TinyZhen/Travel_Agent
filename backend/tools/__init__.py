"""Tools the Research agent can call.

Each tool tries its live API when credentials are configured and falls back to
the offline sample data otherwise (or when the live call fails). Every result
carries a `source` field so the UI and the evaluation can tell them apart.
"""
from __future__ import annotations

import json
import math
import os
import re
import zlib
from datetime import date, datetime, timedelta
from typing import Any, Optional

import requests
from dotenv import load_dotenv

from fixtures import demo_data as D

load_dotenv()
TIMEOUT = 8


def offline() -> bool:
    return os.getenv("ROAMEO_OFFLINE") == "1"


def _seed(*parts: Any) -> int:
    return zlib.crc32("|".join(map(str, parts)).encode())


def _parse_date(d: str | date) -> date:
    return d if isinstance(d, date) else datetime.strptime(d, "%Y-%m-%d").date()


def _haversine_km(a: dict, b: dict) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a["lat"], a["lng"], b["lat"], b["lng"]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


# ---------------------------------------------------------------- city lookup
def resolve_city(name: str) -> Optional[dict]:
    """Map a free-text city name to coordinates and airport codes."""
    if not name:
        return None
    key = name.strip().lower().rstrip(".")
    key = D.CITY_ALIASES.get(key, key)
    for k, info in D.CITIES.items():
        if key == k or key.startswith(k) or k in key:
            return {**info, "key": k}
    if offline():
        return None
    try:
        r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                         params={"name": name, "count": 1}, timeout=TIMEOUT).json()
        hit = (r.get("results") or [None])[0]
        if hit:
            return {"name": hit["name"], "lat": hit["latitude"], "lng": hit["longitude"],
                    "iata": None, "city_code": None, "key": None, "drive_hours": None}
    except requests.RequestException:
        pass
    return None


def drive_hours(origin: str, destination: str) -> Optional[float]:
    """Rough driving time: straight-line distance × 1.25 road factor at 85 km/h."""
    o, d = resolve_city(origin), resolve_city(destination)
    if not o or not d:
        return None
    return round(_haversine_km(o, d) * 1.25 / 85, 1)


# --------------------------------------------------------------------- SerpApi
# One key gives live Google Flights, Google Hotels and Google Events results.
# (Amadeus Self-Service, used by the first prototype, was shut down in July 2026.)
_CACHE: dict[str, Any] = {}


def _serpapi(params: dict) -> Optional[dict]:
    if not os.getenv("SERPAPI_API_KEY") or offline():
        return None
    key = json.dumps(params, sort_keys=True)
    if key in _CACHE:  # the free plan has 250 searches/month; don't spend them twice
        return _CACHE[key]
    try:
        res = requests.get("https://serpapi.com/search.json", timeout=25, params={
            **params, "api_key": os.getenv("SERPAPI_API_KEY"), "hl": "en", "gl": "us", "currency": "USD"}).json()
    except (requests.RequestException, ValueError):
        return None
    if "error" in res:
        return None
    _CACHE[key] = res
    return res


# -------------------------------------------------------------------- flights
def search_flights(origin: str, destination: str, date: str, travelers: int = 1, nights: int = 2) -> list[dict]:
    o, d = resolve_city(origin), resolve_city(destination)
    if not o or not d:
        return [{"error": f"Unknown city: {origin if not o else destination}"}]
    if o.get("iata") and d.get("iata"):
        live = _google_flights(o["iata"], d["iata"], date, nights)
        if live:
            return live
    km = _haversine_km(o, d)
    base = 60 + km * 0.11
    out = []
    for i, airline in enumerate(D.AIRLINES):
        s = _seed(o["iata"], d["iata"], date, airline)
        dep_h = 6 + (s % 14)
        dur_h = round(0.8 + km / 750, 1)
        dep = datetime.combine(_parse_date(date), datetime.min.time()) + timedelta(hours=dep_h)
        out.append({
            "airline": airline, "from": o["iata"], "to": d["iata"],
            "departure_time": dep.isoformat(timespec="minutes"),
            "arrival_time": (dep + timedelta(hours=dur_h)).isoformat(timespec="minutes"),
            "price_per_person": round(base * (0.8 + (s % 60) / 100)),
            "round_trip": True, "source": "demo",
        })
    return sorted(out, key=lambda f: f["price_per_person"])


def _google_flights(o: str, d: str, day: str, nights: int) -> list[dict]:
    ret = (_parse_date(day) + timedelta(days=max(nights, 1))).isoformat()
    res = _serpapi({"engine": "google_flights", "departure_id": o, "arrival_id": d,
                    "outbound_date": day, "return_date": ret, "type": 1, "adults": 1})
    if not res:
        return []
    out = []
    for offer in (res.get("best_flights") or []) + (res.get("other_flights") or []):
        legs = offer.get("flights") or []
        if not legs or not offer.get("price"):
            continue
        out.append({
            "airline": legs[0].get("airline", "?"), "from": legs[0]["departure_airport"]["id"],
            "to": legs[-1]["arrival_airport"]["id"],
            "departure_time": legs[0]["departure_airport"]["time"].replace(" ", "T"),
            "arrival_time": legs[-1]["arrival_airport"]["time"].replace(" ", "T"),
            "stops": len(legs) - 1, "price_per_person": float(offer["price"]),
            "round_trip": True, "source": "google_flights",
            "url": res.get("search_metadata", {}).get("google_flights_url"),
        })
    return sorted(out, key=lambda f: f["price_per_person"])[:8]


# --------------------------------------------------------------------- hotels
def search_hotels(destination: str, checkin: str, nights: int = 2, travelers: int = 1) -> list[dict]:
    c = resolve_city(destination)
    if not c:
        return [{"error": f"Unknown city: {destination}"}]
    live = _google_hotels(c, checkin, nights, travelers)
    if live:
        return live
    weekend = _parse_date(checkin).weekday() >= 4
    out = []
    for tier, suffix, price, rating in D.HOTEL_TIERS:
        s = _seed(c["name"], suffix)
        nightly = round(price * (1.15 if weekend else 1.0) * (0.9 + (s % 25) / 100))
        out.append({
            "name": f"{c['name']} {suffix}", "tier": tier, "nightly_price": nightly,
            "total_price": nightly * nights, "rating": rating,
            "lat": c["lat"] + ((s % 40) - 20) / 1000, "lng": c["lng"] + ((s // 40 % 40) - 20) / 1000,
            "source": "demo",
        })
    return sorted(out, key=lambda h: h["nightly_price"])


def _google_hotels(c: dict, checkin: str, nights: int, travelers: int) -> list[dict]:
    out_date = (_parse_date(checkin) + timedelta(days=max(nights, 1))).isoformat()
    res = _serpapi({"engine": "google_hotels", "q": f"hotels in {c['name']}", "check_in_date": checkin,
                    "check_out_date": out_date, "adults": min(max(travelers, 1), 2)})
    if not res:
        return []
    out = []
    for h in res.get("properties", []):
        nightly = (h.get("rate_per_night") or {}).get("extracted_lowest")
        if not nightly or h.get("type") == "vacation rental":
            continue
        gps = h.get("gps_coordinates") or {}
        if gps and _haversine_km(c, {"lat": gps["latitude"], "lng": gps["longitude"]}) > 12:
            continue  # Google mixes in suburbs (e.g. New Jersey for "hotels in New York")
        out.append({"name": h.get("name"), "nightly_price": float(nightly), "total_price": float(nightly) * nights,
                    "rating": h.get("overall_rating"), "stars": h.get("extracted_hotel_class"),
                    "lat": gps.get("latitude"), "lng": gps.get("longitude"), "url": h.get("link"),
                    "source": "google_hotels"})
    if not out:
        return []
    # Tier by price within this city and date (stars say little about value: a 4-star can be cheap).
    prices = sorted(h["nightly_price"] for h in out)
    lo, hi = prices[len(prices) // 3], prices[2 * len(prices) // 3]
    for h in out:
        h["tier"] = "budget" if h["nightly_price"] <= lo else "mid" if h["nightly_price"] <= hi else "luxury"
    return sorted(out, key=lambda h: h["nightly_price"])


# ---------------------------------------------------------------- attractions
def search_attractions(destination: str, interests: Optional[list[str]] = None,
                       query: Optional[str] = None) -> list[dict]:
    """Curated real landmarks for built-in cities; Google Maps (via SerpApi) for anything else,
    including targeted searches like query="museums" when the traveler asks for more."""
    c = resolve_city(destination)
    if not c:
        return [{"error": f"Unknown city: {destination}"}]
    interests = [i.lower() for i in (interests or [])]
    rows = D.ATTRACTIONS.get(c.get("key") or "", [])
    curated = []
    for name, lat, lng, tags, indoor, cost, hours in rows:
        curated.append({"name": name, "lat": lat, "lng": lng, "tags": tags, "indoor": indoor,
                        "cost_per_person": cost, "cost_estimated": True, "hours": hours,
                        "match": sum(1 for t in tags if t in interests), "source": "curated"})
    if query or not curated:
        live = _google_maps(c, query or "top sights", interests)
        if query and curated:  # targeted search adds to the curated list, never replaces it
            names = {a["name"] for a in curated}
            return sorted(curated, key=lambda a: -a["match"]) + [a for a in live if a["name"] not in names]
        if live:
            return live
    if not curated and os.getenv("GOOGLE_API_KEY") and not offline():
        return _google_attractions(c)
    return sorted(curated, key=lambda a: -a["match"])


PLACE_TAGS = [  # (keyword in Google's place type, tags, indoor, typical cost per person, hours)
    ("museum", ["museum"], True, 25, 2.5), ("gallery", ["art", "museum"], True, 0, 1.5),
    ("art", ["art"], True, 20, 2), ("histor", ["history"], False, 0, 1.5), ("memorial", ["history"], False, 0, 1),
    ("monument", ["history", "landmark"], False, 0, 1), ("park", ["nature", "outdoors"], False, 0, 1.5),
    ("garden", ["nature", "outdoors"], False, 0, 1.5), ("zoo", ["family", "nature"], False, 25, 2.5),
    ("aquarium", ["family", "nature"], True, 40, 2), ("science", ["science", "family"], True, 25, 2.5),
    ("market", ["food", "shopping"], True, 15, 1.5), ("observ", ["landmark", "architecture"], True, 40, 1.5),
    ("church", ["architecture", "history"], True, 0, 1), ("cathedral", ["architecture", "history"], True, 0, 1),
    ("bridge", ["landmark", "outdoors"], False, 0, 1), ("theater", ["art", "music"], True, 0, 1),
    ("library", ["architecture", "history"], True, 0, 1), ("landmark", ["landmark"], False, 0, 1),
]


def _tags_for(text: str) -> list[str]:
    t = text.lower()
    tags = [tag for kw, tags_, *_ in PLACE_TAGS if kw in t for tag in tags_]
    return list(dict.fromkeys(tags)) or [t.rstrip("s")]


def _google_maps(c: dict, query: str, interests: list[str]) -> list[dict]:
    res = _serpapi({"engine": "google_maps", "type": "search", "q": f"{query} in {c['name']}",
                    "ll": f"@{c['lat']},{c['lng']},13z"})
    if not res:
        return []
    out = []
    for r in res.get("local_results", []):
        gps = r.get("gps_coordinates") or {}
        if not gps or (r.get("rating") or 0) < 4.2 or (r.get("reviews") or 0) < 100:
            continue
        if _haversine_km(c, {"lat": gps["latitude"], "lng": gps["longitude"]}) > 15:
            continue
        kind = " ".join([r.get("type") or ""] + (r.get("types") or [])).lower()
        hit = next((row for row in PLACE_TAGS if row[0] in kind), None)
        if not hit:
            continue  # unknown place type (venue, shop, office…): not a sight we can schedule reliably
        tags = _tags_for(kind)
        out.append({"name": r.get("title"), "lat": gps["latitude"], "lng": gps["longitude"], "tags": tags,
                    "indoor": hit[2] if hit else False, "cost_per_person": hit[3] if hit else 0,
                    "cost_estimated": True, "hours": hit[4] if hit else 1.5, "rating": r.get("rating"),
                    "match": sum(1 for t in tags if t in interests), "source": "google_maps",
                    "url": f"https://www.google.com/maps/place/?q=place_id:{r['place_id']}" if r.get("place_id") else None})
    return out[:10]


def _google_attractions(c: dict) -> list[dict]:
    try:
        res = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", params={
            "location": f"{c['lat']},{c['lng']}", "radius": 6000, "type": "tourist_attraction",
            "key": os.getenv("GOOGLE_API_KEY")}, timeout=TIMEOUT).json()
    except requests.RequestException:
        return []
    if res.get("status") != "OK":
        return []
    out = []
    for a in res.get("results", []):
        if a.get("rating", 0) >= 4.2 and a.get("user_ratings_total", 0) >= 50:
            loc = a["geometry"]["location"]
            out.append({"name": a["name"], "lat": loc["lat"], "lng": loc["lng"],
                        "tags": a.get("types", [])[:3], "indoor": "museum" in a.get("types", []),
                        "cost_per_person": 0, "hours": 2, "match": 0, "rating": a.get("rating"),
                        "source": "google_places"})
    return out[:8]


# --------------------------------------------------------------------- events
def search_events(destination: str, start_date: str, nights: int = 2,
                  interests: Optional[list[str]] = None) -> list[dict]:
    c = resolve_city(destination)
    if not c:
        return [{"error": f"Unknown city: {destination}"}]
    start = _parse_date(start_date)
    live = _google_events(c["name"], start, nights)
    if not live and os.getenv("TICKETMASTER_API_KEY") and not offline():
        live = _ticketmaster(c["name"], start, nights)
    if live:
        return live
    out = []
    for offset in range(nights + 1):
        day = start + timedelta(days=offset)
        for weekday, title, tags, price, t in D.EVENTS:
            if day.weekday() == weekday:
                out.append({"name": f"{title} — {c['name']}", "date": day.isoformat(), "time": t,
                            "tags": tags, "price_per_person": price, "source": "demo"})
    return out


EVENT_TAGS = {
    "music": ["concert", "jazz", "band", "live music", "symphony", "orchestra", "tour", "dj", "festival"],
    "comedy": ["comedy", "stand-up", "improv"], "art": ["art", "gallery", "exhibit", "museum", "theater", "theatre"],
    "food": ["food", "wine", "beer", "tasting", "market"], "family": ["kids", "family", "children"],
    "nightlife": ["party", "club", "night"], "sports": ["game", "vs", "match", "marathon"],
}


def _tag_event(title: str) -> list[str]:
    t = title.lower()
    return [tag for tag, words in EVENT_TAGS.items() if any(w in t for w in words)]


def _google_events(city: str, start: date, nights: int) -> list[dict]:
    # Google Events only surfaces the next ~10 days of events: exact dates in the query return nothing,
    # date filters and paging are ignored (tested Oct 2026). Later trips fall through to Ticketmaster or samples.
    if (start - date.today()).days > 10:
        return []
    res = _serpapi({"engine": "google_events", "q": f"Events in {city}"})
    return _parse_events((res or {}).get("events_results", []), start,
                         {start + timedelta(days=i) for i in range(nights + 1)})


def _parse_events(raw: list[dict], start: date, days: set) -> list[dict]:
    out, seen = [], set()
    for e in raw:
        if e.get("title") in seen:
            continue
        seen.add(e.get("title"))
        when = (e.get("date") or {}).get("start_date", "")  # e.g. "Nov 20"
        m = re.match(r"([A-Za-z]{3})\s+(\d{1,2})", when)
        if not m:
            continue
        try:
            day = datetime.strptime(f"{m[1]} {m[2]} {start.year}", "%b %d %Y").date()
        except ValueError:
            continue
        if day not in days:
            continue
        clock = (e.get("date") or {}).get("when", "").split(",")[-1]  # "Fri, Nov 13, 8 – 10 PM" → " 8 – 10 PM"
        tm, ampm = re.search(r"(\d{1,2})(?::(\d{2}))?\s*([AP]M)?", clock), re.search(r"[AP]M", clock)
        time = None
        if tm and ampm:  # start time; "8 – 10 PM" borrows the PM
            time = f"{int(tm[1]) % 12 + (12 if (tm[3] or ampm[0]) == 'PM' else 0):02d}:{tm[2] or '00'}"
        out.append({"name": e.get("title"), "date": day.isoformat(), "time": time, "tags": _tag_event(e.get("title", "")),
                    "price_per_person": None, "venue": (e.get("venue") or {}).get("name"),
                    "url": e.get("link"), "source": "google_events"})
    return out


def _ticketmaster(city: str, start: date, nights: int) -> list[dict]:
    try:
        res = requests.get("https://app.ticketmaster.com/discovery/v2/events.json", params={
            "apikey": os.getenv("TICKETMASTER_API_KEY"), "city": city, "size": 10, "sort": "date,asc",
            "startDateTime": f"{start}T00:00:00Z",
            "endDateTime": f"{start + timedelta(days=nights + 1)}T00:00:00Z"}, timeout=TIMEOUT)
        res.raise_for_status()
    except requests.RequestException:
        return []
    out = []
    for e in res.json().get("_embedded", {}).get("events", []):
        st = e.get("dates", {}).get("start", {})
        prices = e.get("priceRanges") or [{}]
        out.append({"name": e.get("name"), "date": st.get("localDate"), "time": st.get("localTime", "")[:5],
                    "tags": [c.get("segment", {}).get("name", "").lower() for c in e.get("classifications", [])],
                    "price_per_person": prices[0].get("min"), "url": e.get("url"),
                    "source": "ticketmaster"})
    return out


# -------------------------------------------------------------------- weather
def get_weather(destination: str, start_date: str, nights: int = 2) -> list[dict]:
    c = resolve_city(destination)
    if not c:
        return [{"error": f"Unknown city: {destination}"}]
    start = _parse_date(start_date)
    days = [start + timedelta(days=i) for i in range(nights + 1)]
    if not offline() and (days[-1] - date.today()).days <= 15:
        try:
            r = requests.get("https://api.open-meteo.com/v1/forecast", params={
                "latitude": c["lat"], "longitude": c["lng"], "timezone": "auto",
                "daily": "temperature_2m_max,precipitation_probability_max",
                "start_date": days[0].isoformat(), "end_date": days[-1].isoformat()}, timeout=TIMEOUT).json()
            daily = r["daily"]
            return [{"date": d, "high_c": t, "rain_chance": p, "source": "open-meteo"}
                    for d, t, p in zip(daily["time"], daily["temperature_2m_max"],
                                       daily["precipitation_probability_max"])]
        except (requests.RequestException, KeyError, ValueError):
            pass
    out = []
    for d in days:
        s = _seed(c["name"], d)
        out.append({"date": d.isoformat(), "high_c": round(22 - abs(d.month - 7) * 3 + (s % 7) - 3),
                    "rain_chance": (s % 10) * 10, "source": "seasonal-estimate"})
    return out


REGISTRY = {
    "search_flights": search_flights,
    "search_hotels": search_hotels,
    "search_attractions": search_attractions,
    "search_events": search_events,
    "get_weather": get_weather,
}

SCHEMAS = [
    {"type": "function", "function": {
        "name": "search_flights", "description": "Round-trip flight options between two cities.",
        "parameters": {"type": "object", "properties": {
            "origin": {"type": "string"}, "destination": {"type": "string"},
            "date": {"type": "string", "description": "YYYY-MM-DD"}, "travelers": {"type": "integer"},
            "nights": {"type": "integer", "description": "nights before the return flight"}},
            "required": ["origin", "destination", "date"]}}},
    {"type": "function", "function": {
        "name": "search_hotels", "description": "Hotel options with nightly and total price.",
        "parameters": {"type": "object", "properties": {
            "destination": {"type": "string"}, "checkin": {"type": "string"}, "nights": {"type": "integer"},
            "travelers": {"type": "integer"}},
            "required": ["destination", "checkin"]}}},
    {"type": "function", "function": {
        "name": "search_attractions", "description": "Top attractions, ranked by match with interests.",
        "parameters": {"type": "object", "properties": {
            "destination": {"type": "string"}, "interests": {"type": "array", "items": {"type": "string"}},
            "query": {"type": "string", "description": "optional targeted search, e.g. 'museums' or 'jazz clubs'"}},
            "required": ["destination"]}}},
    {"type": "function", "function": {
        "name": "search_events", "description": "Events (concerts, markets, shows) during the stay.",
        "parameters": {"type": "object", "properties": {
            "destination": {"type": "string"}, "start_date": {"type": "string"}, "nights": {"type": "integer"},
            "interests": {"type": "array", "items": {"type": "string"}}},
            "required": ["destination", "start_date"]}}},
    {"type": "function", "function": {
        "name": "get_weather", "description": "Daily forecast (or seasonal estimate) for the stay.",
        "parameters": {"type": "object", "properties": {
            "destination": {"type": "string"}, "start_date": {"type": "string"}, "nights": {"type": "integer"}},
            "required": ["destination", "start_date"]}}},
]
