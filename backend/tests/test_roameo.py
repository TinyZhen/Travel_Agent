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
    st = client.post("/api/message", json={"message": "Boston day trip on Nov 7, history"}).json()
    sid = st["session_id"]
    assert st["status"] == "awaiting_approval"
    assert client.get(f"/api/export/{sid}.ics").status_code == 404
    st = client.post("/api/message", json={"message": "approve", "session_id": sid}).json()
    assert st["status"] == "approved"
    ics = client.get(f"/api/export/{sid}.ics")
    assert ics.status_code == 200 and "BEGIN:VEVENT" in ics.text


def test_unknown_session():
    assert client.post("/api/message", json={"message": "hi", "session_id": "nope"}).status_code == 404
