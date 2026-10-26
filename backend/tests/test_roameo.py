"""Run with: cd backend && ROAMEO_OFFLINE=1 ROAMEO_FORCE_DEMO=1 pytest -q"""
import os

os.environ.setdefault("ROAMEO_OFFLINE", "1")
os.environ.setdefault("ROAMEO_FORCE_DEMO", "1")

import pytest
from fastapi.testclient import TestClient

from app import app
from eval.run_eval import CASES, run_case

client = TestClient(app)


@pytest.mark.parametrize("case", [c for c in CASES if not c.get("known_limitation")], ids=lambda c: c["id"])
def test_scenario(case):
    r = run_case(case)
    assert r["passed"], [n for n, ok in r["checks"] if not ok]


def test_api_flow_requires_approval_before_export():
    st = client.post("/api/message", json={"message": "Boston day trip on Nov 7, I live in Boston, history"}).json()
    sid = st["session_id"]
    assert st["status"] == "awaiting_approval"
    assert client.get(f"/api/export/{sid}.ics").status_code == 404
    st = client.post("/api/message", json={"message": "approve", "session_id": sid}).json()
    assert st["status"] == "approved"
    ics = client.get(f"/api/export/{sid}.ics")
    assert ics.status_code == 200 and "BEGIN:VEVENT" in ics.text


def test_unknown_session():
    assert client.post("/api/message", json={"message": "hi", "session_id": "nope"}).status_code == 404


def test_serpapi_parsing(monkeypatch):
    """Live providers parse SerpApi-shaped responses (no network)."""
    import tools
    from datetime import date, timedelta
    SOON = date.today() + timedelta(days=3)  # Google Events only covers the next ~10 days
    fake = {
        "google_flights": {"best_flights": [{"price": 212, "flights": [
            {"airline": "JetBlue", "departure_airport": {"id": "BOS", "time": "2026-11-13 08:05"},
             "arrival_airport": {"id": "JFK", "time": "2026-11-13 09:30"}}]}], "other_flights": []},
        "google_hotels": {"properties": [
            {"name": "Hotel A", "rate_per_night": {"extracted_lowest": 189}, "extracted_hotel_class": 3,
             "overall_rating": 4.3, "gps_coordinates": {"latitude": 40.75, "longitude": -73.99}},
            {"name": "No Price Inn"}]},
        "google_events": {"events_results": [
            {"title": "Jazz Night", "date": {"start_date": f"{SOON:%b} {SOON.day}",
                                             "when": f"{SOON:%a, %b} {SOON.day}, 8 – 10 PM"}, "link": "x"},
            {"title": "Out of range", "date": {"start_date": "Dec 25", "when": "Fri, Dec 25"}}]},
    }
    monkeypatch.setattr(tools, "_serpapi", lambda p: fake[p["engine"]])
    f = tools.search_flights("Boston", "New York", "2026-11-13", 2, 2)
    assert f[0]["source"] == "google_flights" and f[0]["price_per_person"] == 212 and f[0]["departure_time"] == "2026-11-13T08:05"
    h = tools.search_hotels("New York", "2026-11-13", 2)
    assert [x["name"] for x in h] == ["Hotel A"] and h[0]["tier"] == "budget" and h[0]["total_price"] == 378
    e = tools.search_events("New York", SOON.isoformat(), 2)
    assert len(e) == 1 and e[0]["time"] == "20:00" and e[0]["price_per_person"] is None and "music" in e[0]["tags"]


def test_guide_never_invents_exhibitions(monkeypatch):
    """Exhibitions must come from the web results; anything else the LLM returns is dropped."""
    from datetime import date
    import llm
    import tools
    from agents import guide
    from schemas import TripSpec
    monkeypatch.setattr(llm, "available", lambda: True)
    monkeypatch.setattr(tools, "_serpapi", lambda p: {"organic_results": [
        {"title": "Exhibitions", "snippet": "Real Show, Nov 1 – Dec 1", "link": "https://museum.example/exhibitions"}]})
    monkeypatch.setattr(llm, "chat_json", lambda *a, **k: {
        "summary": "s", "highlights": [], "tips": [], "plan": [{"minutes": 120, "what": "see it"}],
        "exhibitions": [{"title": "Real Show", "url": "https://museum.example/exhibitions"},
                        {"title": "Made-up Show", "url": "https://invented.example"}]})
    guide._CACHE.clear()
    spec = TripSpec(origin="Boston", destination="New York", start_date=date(2026, 11, 13))
    g = guide.guide_for({"name": "Some Museum", "tags": ["museum"], "hours": 2}, {"start": "10:00", "end": "12:00"},
                        spec, date(2026, 11, 13))
    assert [x["title"] for x in g["exhibitions"]] == ["Real Show"] and g["web_checked"]
