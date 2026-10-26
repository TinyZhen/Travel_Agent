"""Roameo API. Run: uvicorn app:app --port 8000 --reload (from backend/)."""
from __future__ import annotations

import os
import pathlib
import secrets
import time
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import llm
from agents import guide as guide_agent
from agents.orchestrator import SESSIONS, new_session
from schemas import TraceStep

app = FastAPI(title="Roameo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ---- public-demo protection: optional access code + per-visitor rate limit
ACCESS_CODE = os.getenv("ROAMEO_ACCESS_CODE", "")
RATE_LIMIT = int(os.getenv("ROAMEO_RATE_LIMIT", "60"))  # requests per visitor per hour
_hits: dict[str, deque] = defaultdict(deque)


def guard(request: Request):
    if ACCESS_CODE:
        given = request.headers.get("x-access-code") or request.query_params.get("code") or ""
        if not secrets.compare_digest(given, ACCESS_CODE):
            raise HTTPException(401, "Access code required.")
    who = request.headers.get("x-forwarded-for", request.client.host if request.client else "?").split(",")[0]
    q, now = _hits[who], time.time()
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        raise HTTPException(429, "Too many requests from this visitor; try again later.")
    q.append(now)


class Message(BaseModel):
    message: str
    session_id: str | None = None


@app.get("/api/health")
def health():
    return {"ok": True, "access_code_required": bool(ACCESS_CODE), "llm": llm.available(), "model": llm.DEFAULT_MODEL if llm.available() else None,
            "live_tools": {k: bool(os.getenv(k)) for k in
                           ["SERPAPI_API_KEY", "GOOGLE_API_KEY", "TICKETMASTER_API_KEY"]}}


@app.post("/api/message", dependencies=[Depends(guard)])
def message(req: Message):
    if req.session_id:
        sess = SESSIONS.get(req.session_id)
        if not sess:
            raise HTTPException(404, "Unknown session; start a new one.")
    else:
        sess = new_session()
    try:
        return sess.handle(req.message)
    except Exception as e:  # keep the demo alive; surface the error to the UI
        sess.state.status = "error"
        sess.state.questions = [f"Something went wrong: {type(e).__name__}: {e}"]
        return sess.state


@app.get("/api/guide", dependencies=[Depends(guard)])
def guide(session_id: str, name: str):
    """Visit guide for one stop of the current plan (generated on demand, cached)."""
    sess = SESSIONS.get(session_id)
    if not sess or not sess.state.plan:
        raise HTTPException(404, "Unknown session.")
    found = guide_agent.find_stop(sess.state.plan, sess.state.research, name)
    if not found:
        raise HTTPException(404, "That stop isn't in the current plan.")
    place, item, day = found
    g = guide_agent.guide_for(place, item, sess.state.spec, day)
    if "error" not in g:
        sess.log(TraceStep(agent="Guide", action=f"guide for {name}",
                           detail=f"{len(g.get('exhibitions', []))} current exhibitions from "
                                  f"{len(g.get('sources', []))} web results" if g.get("web_checked")
                           else "highlights and visit plan"))
    return g


@app.get("/api/export/{session_id}.ics", response_class=PlainTextResponse, dependencies=[Depends(guard)])
def export_ics(session_id: str):
    sess = SESSIONS.get(session_id)
    if not sess or not sess.state.plan or sess.state.status != "approved":
        raise HTTPException(404, "No approved plan for this session.")
    return PlainTextResponse(to_ics(sess.state), media_type="text/calendar",
                             headers={"Content-Disposition": "attachment; filename=roameo-trip.ics"})


def to_ics(state) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Roameo//EN"]
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    n = 0
    for day in state.plan.days:
        clock = datetime.combine(day.date, datetime.min.time()) + timedelta(hours=9 if day != state.plan.days[0] else 14)
        for it in day.items:
            if it["kind"] == "event" and it.get("time"):
                start = datetime.combine(day.date, datetime.strptime(it["time"], "%H:%M").time())
                end = start + timedelta(hours=2)
            else:
                start, end = clock, clock + timedelta(hours=it.get("hours", 2))
                clock = end + timedelta(minutes=30)
            n += 1
            lines += ["BEGIN:VEVENT", f"UID:{state.session_id}-{n}@roameo", f"DTSTAMP:{stamp}",
                      f"DTSTART:{start:%Y%m%dT%H%M%S}", f"DTEND:{end:%Y%m%dT%H%M%S}",
                      f"SUMMARY:{it['name']}", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


# Serve the built frontend from the same origin (one URL for the public demo).
STATIC = pathlib.Path(os.getenv("ROAMEO_STATIC", pathlib.Path(__file__).resolve().parents[1] / "frontend" / "dist"))
if STATIC.is_dir():
    app.mount("/", StaticFiles(directory=STATIC, html=True), name="frontend")
