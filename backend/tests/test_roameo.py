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


def test_access_code(monkeypatch):
    import app as app_module
    monkeypatch.setattr(app_module, "ACCESS_CODE", "letmein")
    assert client.post("/api/message", json={"message": "hi"}).status_code == 401
    ok = client.post("/api/message", json={"message": "hi"}, headers={"X-Access-Code": "letmein"})
    assert ok.status_code == 200


SKI = [{"name": "Test Ski Hill", "lat": 42.50, "lng": -83.30, "tags": ["skiing", "winter", "outdoors"],
        "activity": "skiing", "indoor": False, "cost_per_person": 90, "cost_estimated": True, "hours": 4,
        "rating": 4.4, "km_from_city": 25, "match": 3, "source": "google_maps"}]


def _ski_tool(monkeypatch, places):
    import tools
    monkeypatch.setitem(tools.REGISTRY, "search_activity", lambda destination, activity: places)


def test_requested_activity_gets_a_full_day(monkeypatch):
    from datetime import date
    from agents.orchestrator import new_session
    _ski_tool(monkeypatch, SKI)
    st = new_session(date(2026, 10, 26)).handle("Detroit on Dec 22 for 3 days from Boston, include a ski trip")
    ski = [(i, it) for i, d in enumerate(st.plan.days) for it in d.items if it.get("activity") == "skiing"]
    assert len(ski) == 1
    day, item = ski[0]
    assert day == 1 and item["travel"]["mode"] == "drive" and "You asked for skiing" in item["why"]


def test_asking_for_activity_later_adds_it_or_says_why_not(monkeypatch):
    from datetime import date
    from agents.orchestrator import new_session
    _ski_tool(monkeypatch, [])
    s = new_session(date(2026, 10, 26))
    s.handle("Detroit on Dec 22 for 3 days from Boston")
    st = s.handle("i want to go ski")
    assert any("couldn't find anywhere for skiing" in q for q in st.questions)
    assert not any("ski" in it["name"].lower() or it.get("activity") for d in st.plan.days for it in d.items)
    _ski_tool(monkeypatch, SKI)
    s = new_session(date(2026, 10, 26))
    s.handle("Detroit on Dec 22 for 3 days from Boston")
    st = s.handle("i want to go ski")
    assert "+ Test Ski Hill" in st.plan.changes


def test_repeated_tool_call_never_wipes_results():
    from agents import research
    results, log = {}, (lambda step: None)
    research._record("search_attractions", [{"name": "Art Museum"}, {"name": "Zoo"}], results, log)
    research._record("search_attractions", [], results, log, {"query": "ski resorts"})
    research._record("search_attractions", [{"name": "Zoo"}, {"name": "Park"}], results, log)
    assert [a["name"] for a in results["search_attractions"]] == ["Art Museum", "Zoo", "Park"]
    research._record("search_flights", [{"airline": "A"}], results, log)
    research._record("search_flights", [{"error": "timeout"}], results, log)
    assert results["search_flights"] == [{"airline": "A"}]


def test_another_activity_day_keeps_the_trip(monkeypatch):
    from datetime import date
    from agents.orchestrator import new_session
    _ski_tool(monkeypatch, SKI)
    s = new_session(date(2026, 10, 26))
    st = s.handle("Detroit on Dec 22 for a week from Boston, include a ski trip")
    nights, before = st.spec.nights, len([it for d in st.plan.days for it in d.items if it["kind"] == "event"])
    st = s.handle("another ski day please")
    assert st.spec.nights == nights == 6
    assert sum(it.get("activity") == "skiing" for d in st.plan.days for it in d.items) == 2
    assert len([it for d in st.plan.days for it in d.items if it["kind"] == "event"]) == before


def test_vague_requests_for_more_things_to_do_are_understood():
    from agents.feedback import rule_parse
    for msg in ["add some activity", "day 3 - 6 you dont have any thing for me, add some activity",
                "why only day 2", "these days are empty"]:
        assert rule_parse(msg, []).get("fill"), msg
    assert not rule_parse("make it cheaper", []).get("fill")
