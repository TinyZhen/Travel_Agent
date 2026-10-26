"""Intake agent: turn a free-text request (or a follow-up answer) into a TripSpec,
and decide whether the human must be asked for missing or invalid information."""
from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional

import llm
from schemas import TripSpec
from tools import drive_hours, resolve_city, us_state
from fixtures.demo_data import ACTIVITIES, ACTIVITY_WORDS, CITIES, CITY_ALIASES

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
INTEREST_WORDS = {
    "museum": ["museum", "museums", "gallery", "galleries"], "art": ["art", "arts", "painting"],
    "history": ["history", "historic", "historical"], "food": ["food", "foodie", "eat", "restaurants", "cuisine"],
    "nature": ["nature", "park", "parks", "hike", "hiking"], "music": ["music", "concert", "jazz", "live music"],
    "family": ["kids", "family", "children", "child"], "nightlife": ["nightlife", "bars", "clubs"],
    "science": ["science"], "shopping": ["shopping", "shops"], "architecture": ["architecture", "buildings"],
    "outdoors": ["outdoor", "outdoors", "walking"], "comedy": ["comedy", "stand-up"],
}
NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}

SYSTEM = """You are the Intake agent of a travel-planning system. Today is {today}.
Extract the trip request into JSON with keys:
origin (city the traveler leaves from, or null if not stated; never assume one), destination (city or null),
start_date (YYYY-MM-DD or null; resolve relative dates like "next weekend" from today; a weekend trip starts
on the Friday; copy explicit dates exactly as written even if they are in the past, because the system validates them),
nights (int; "N days" means N-1 nights, "a weekend" means 2 nights), travelers (int), budget_usd (number or null, total for the whole party),
interests (list from: museum, art, history, food, nature, music, family, nightlife, science, shopping, architecture, outdoors, comedy),
activities (specific things they want to DO, list from: skiing, hiking, ice skating, kayaking, beach, golf, spa, snow tubing),
transport ("fly", "drive" or "local"), hotel_preference ("budget","mid","luxury","any").
Only include keys the text actually supports; omit the rest. Do not invent a destination or date."""


# --------------------------------------------------------------- rule parser
def _num(tok: str) -> Optional[int]:
    return int(tok) if tok.isdigit() else NUM_WORDS.get(tok)


def _find_city(text: str, after: str) -> Optional[str]:
    names = sorted(list(CITIES) + list(CITY_ALIASES), key=len, reverse=True)
    for n in names:
        if re.search(rf"\b{after}\s+(?:the\s+)?{re.escape(n)}\b", text):
            return CITIES[CITY_ALIASES.get(n, n)]["name"]
    m = re.search(rf"\b{after}\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?)", text)
    return m.group(1) if m else None


NOT_PLACES = {"I", "I'd", "I'll", "I'm", "We", "My", "Me", "Plan", "Take", "Trip", "Weekend", "Road", "Day",
              "Family", "Please", "Make", "Find", "Book", "Help", "Want", "Show", "Things", "What", "Can", "Next",
              "This", "The", "A", "Budget"}


def _any_city(text: str, exclude: Optional[str], known_only: bool = False) -> Optional[str]:
    """Fallback: a known city mentioned anywhere, else the first capitalised place-like phrase."""
    low = text.lower()
    names = sorted(list(CITIES) + list(CITY_ALIASES), key=len, reverse=True)
    for n in names:
        name = CITIES[CITY_ALIASES.get(n, n)]["name"]
        if re.search(rf"\b{re.escape(n)}\b", low) and name != exclude:
            return name
    if known_only:
        return None
    skip = NOT_PLACES | {m.capitalize() for m in MONTHS} | {w.capitalize() for w in WEEKDAYS} \
        | {m.capitalize() + w for m in MONTHS for w in ["", "."]}
    for m in re.finditer(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)", text):
        words = [w for w in m.group(1).split() if w not in skip and not w.startswith(tuple(m.capitalize() for m in MONTHS))]
        if words and words[0] != exclude:
            return " ".join(words)
    return None


def _parse_date(text: str, today: date) -> Optional[date]:
    t = text.lower()
    if m := re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", t):
        return date(int(m[1]), int(m[2]), int(m[3]))
    if m := re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b", t):
        d = date(today.year, MONTHS[m[1]], int(m[2]))
        return d if d >= today else date(today.year + 1, d.month, d.day)
    if m := re.search(r"\b(\d{1,2})/(\d{1,2})\b", t):
        d = date(today.year, int(m[1]), int(m[2]))
        return d if d >= today else date(today.year + 1, d.month, d.day)
    if "tomorrow" in t:
        return today + timedelta(days=1)
    if "this weekend" in t or "next weekend" in t:
        friday = today + timedelta(days=(4 - today.weekday()) % 7)
        # On Mon-Thu "next weekend" means the one after this; on Fri-Sun it means the coming one.
        return friday + timedelta(days=7) if "next weekend" in t and today.weekday() < 4 else friday
    if m := re.search(r"\bnext (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", t):
        delta = (WEEKDAYS.index(m[1]) - today.weekday()) % 7 or 7
        return today + timedelta(days=delta)
    if m := re.search(r"\bin (\w+) weeks?\b", t):
        n = _num(m[1])
        return today + timedelta(weeks=n) if n else None
    return None


def rule_extract(text: str, today: date, feedback: bool = False) -> dict:
    t = text.lower()
    out: dict = {}
    origin = _find_city(text, "from") or _find_city(t, "from") \
        or _find_city(t, r"(?:live|based|located|i'm|i am|we're|we are) in")
    if origin:
        out["origin"] = origin
    if feedback:  # "skip Alcatraz" must not become a new destination
        dest = _any_city(text, exclude=origin, known_only=True)
    else:
        dest = _find_city(text, "to") or _find_city(text, "visit") or _find_city(text, "in") \
            or _find_city(t, "to") or _find_city(t, "visit") or _find_city(t, "in") \
            or _any_city(text, exclude=origin)
    if dest:
        out["destination"] = dest
    if d := _parse_date(text, today):
        out["start_date"] = d
    if m := re.search(r"\b(\d+|\w+)\s+nights?\b", t):
        if (n := _num(m[1])) is not None:
            out["nights"] = n
    elif m := re.search(r"\b(\d+|\w+)[\s-]+days?\b", t):
        if (n := _num(m[1])) is not None:
            out["nights"] = max(n - 1, 0)
    elif "weekend" in t:
        out["nights"] = 2
    elif "day trip" in t:
        out["nights"] = 0
    if m := re.search(r"(?:\$\s?(\d[\d,]*)|(\d[\d,]*)\s*(?:usd|dollars|bucks))", t):
        out["budget_usd"] = float((m[1] or m[2]).replace(",", ""))
    elif m := re.search(r"budget (?:is |of |to )?(\d[\d,]*)", t):
        out["budget_usd"] = float(m[1].replace(",", ""))
    if m := re.search(r"\b(?:family of|group of|for|party of)\s+(\d+|\w+)\s*(?:people|persons|of us|adults|travell?ers)?", t):
        if (n := _num(m[1])) and n < 20 and not re.search(rf"{m[1]}\s+(?:days?|nights?)", t):
            out["travelers"] = n
    if re.search(r"\b(with my|with a) (partner|wife|husband|girlfriend|boyfriend|friend)\b", t):
        out["travelers"] = 2
    if re.search(r"\b(drive|driving|by car|road trip)\b", t):
        out["transport"] = "drive"
    if re.search(r"\b(cheap|affordable|hostel)\b|\bbudget\b(?!\s*(?:is|of|to|around|about|:|\$|\d))", t):
        out["hotel_preference"] = "budget"
    elif re.search(r"\b(luxury|fancy|5-star|five star)\b", t):
        out["hotel_preference"] = "luxury"
    activities = [k for k, words in ACTIVITY_WORDS.items() if any(re.search(rf"\b{w}\b", t) for w in words)]
    if activities:
        out["activities"] = activities
    interests = [k for k, words in INTEREST_WORDS.items() if any(re.search(rf"\b{w}\b", t) for w in words)]
    if interests:
        out["interests"] = interests
    return out


# ---------------------------------------------------------------- the agent
def extract(text: str, today: Optional[date] = None, feedback: bool = False) -> tuple[dict, str]:
    """Return (fields, method). Uses the LLM when available, rules otherwise."""
    today = today or date.today()
    if llm.available():
        try:
            data = llm.chat_json(SYSTEM.format(today=today.isoformat()), text)
            if data.get("start_date"):
                data["start_date"] = date.fromisoformat(data["start_date"])
            data["activities"] = [a for a in data.get("activities") or [] if a in ACTIVITIES]
            return {k: v for k, v in data.items() if v not in (None, "", [])}, "llm"
        except Exception:
            pass
    return rule_extract(text, today, feedback), "rules"


def merge(spec: TripSpec, fields: dict) -> TripSpec:
    data = spec.model_dump()
    for k, v in fields.items():
        if k in data:
            data[k] = v
    new = TripSpec(**data)
    if new.destination and new.origin and new.destination.lower() == new.origin.lower():
        new.transport = "local"
    return new


def validate(spec: TripSpec, today: Optional[date] = None) -> list[str]:
    """Human-in-the-loop decision point #1: what must we ask before planning?"""
    today = today or date.today()
    qs = []
    if not spec.origin:
        qs.append("Where are you leaving from?")
    elif not resolve_city(spec.origin):
        qs.append(f"I couldn't find \"{spec.origin}\". Which city are you leaving from?")
    state = us_state(spec.destination or "") if spec.destination and not resolve_city(spec.destination) else None
    if not spec.destination:
        qs.append("Where would you like to go?")
    elif state:
        hint = f" (e.g. {', '.join(state[1])})" if state[1] else ""
        qs.append(f"{state[0]} is a state. Which city would you like to visit{hint}?")
    elif not resolve_city(spec.destination):
        qs.append(f"I couldn't find \"{spec.destination}\". Which city do you mean?")
    if not spec.start_date:
        qs.append("What date do you want to leave? (e.g. Nov 14, or \"next weekend\")")
    elif spec.start_date < today:
        qs.append(f"{spec.start_date:%b %d, %Y} is in the past. What date did you mean?")
    elif spec.start_date > today + timedelta(days=330):
        qs.append("Prices aren't published that far ahead. Can you pick a date within the next 11 months?")
    if spec.nights > 14:
        qs.append(f"{spec.nights} nights is longer than I can plan well. Can we plan up to 14 nights?")
    return qs


def apply_defaults(spec: TripSpec, provided: set[str]) -> TripSpec:
    """Recompute the visible assumption notes. `provided` = fields the human has stated so far."""
    notes = []
    if spec.start_date:
        end = spec.start_date + timedelta(days=spec.nights)
        notes.append(f"Dates: {spec.start_date:%a %b %d} – {end:%a %b %d, %Y}.")
    if "travelers" not in provided:
        notes.append("Assumed 1 traveler.")
    if "nights" not in provided:
        notes.append(f"Assumed {spec.nights} nights.")
    hours = drive_hours(spec.origin or "", spec.destination or "")
    if spec.transport == "fly" and hours is not None and hours <= 4.5 and "transport" not in provided:
        notes.append(f"{spec.destination} is about a {hours:.0f}h drive from {spec.origin}. "
                     "Still pricing flights; say \"I'll drive\" to switch.")
    spec.assumptions = notes
    return spec
