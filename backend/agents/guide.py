"""Guide agent: turns a stop on the itinerary into a visit plan.

For museums and galleries it first searches the web for current exhibitions and only
reports exhibitions found in those results (with links). Highlights, the minute-by-minute
visit plan and tips are written by the LLM and labelled as such in the UI.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

import llm
import tools

_CACHE: dict[str, dict] = {}

SYSTEM = """You are the Guide agent of a travel planner. Write a practical visit guide for ONE stop.
Return JSON with keys:
summary: one sentence on what this place is and why it's worth the time,
highlights: 3-5 items [{{"name": ..., "why": ...}}] — specific things to see (works, rooms, viewpoints, spots),
exhibitions: [{{"title": ..., "dates": ..., "url": ...}}] — ONLY exhibitions that appear in the search results
  below and are plausibly on view on {visit_date}; copy the url from the result; [] if none or no results,
plan: [{{"minutes": int, "what": ...}}] — how to spend exactly {minutes} minutes there, in order; minutes must sum to {minutes},
tips: 2-3 short practical tips (tickets/entry, timing, where to start). Tips must agree with the plan.
Traveler interests: {interests}. Visit: {visit_date}, {start}–{end}.
Never invent exhibitions. If unsure about a detail, leave it out."""


def _needs_exhibitions(place: dict) -> bool:
    text = " ".join(place.get("tags", [])) + " " + place.get("name", "")
    return any(k in text.lower() for k in ("museum", "gallery", "art"))


def _exhibition_results(name: str, city: str, when: date) -> list[dict]:
    res = tools._serpapi({"engine": "google", "q": f"{name} {city} current exhibitions {when:%B %Y}", "num": 8})
    out = []
    for r in (res or {}).get("organic_results", [])[:8]:
        out.append({"title": r.get("title"), "snippet": r.get("snippet"), "url": r.get("link"),
                    "date": r.get("date")})
    return out


def guide_for(place: dict, item: dict, spec, visit_date: date) -> dict:
    key = f"{place.get('name')}|{visit_date:%Y-%m}|{item.get('start')}-{item.get('end')}|{','.join(spec.interests)}"
    if key in _CACHE:
        return _CACHE[key]
    if not llm.available():
        return {"error": "Visit guides need the LLM agents (set OPENROUTER_API_KEY)."}
    minutes = int(round((place.get("hours") or 2) * 60))
    results = _exhibition_results(place["name"], spec.destination, visit_date) if _needs_exhibitions(place) else []
    context = "\n".join(f"- {r['title']} | {r['snippet']} | {r['url']}" + (f" | {r['date']}" if r.get("date") else "")
                        for r in results) or "(no search results)"
    try:
        data = llm.chat_json(SYSTEM.format(visit_date=visit_date.isoformat(), minutes=minutes,
                                           interests=", ".join(spec.interests) or "general",
                                           start=item.get("start"), end=item.get("end")),
                             f"Stop: {place['name']} in {spec.destination}\nSearch results:\n{context}",
                             max_tokens=2500)
    except Exception as e:
        return {"error": f"Guide unavailable: {type(e).__name__}"}
    # Keep only exhibitions whose link really came from the search results.
    urls = {r["url"] for r in results}
    data["exhibitions"] = [x for x in data.get("exhibitions") or [] if x.get("url") in urls]
    data["sources"] = [{"title": r["title"], "url": r["url"]} for r in results[:3]]
    data["web_checked"] = bool(results)
    data["minutes"] = minutes
    _CACHE[key] = data
    return data


def find_stop(plan, research: dict, name: str) -> Optional[tuple[dict, dict, date]]:
    for d in plan.days:
        for it in d.items:
            if it["kind"] == "attraction" and it["name"] == name:
                place = next((a for a in research.get("search_attractions") or []
                              if isinstance(a, dict) and a.get("name") == name), {"name": name})
                return place, it, d.date
    return None
