"""Roameo API. Run: uvicorn app:app --port 8000 --reload (from backend/)."""
from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

import llm
from agents.orchestrator import SESSIONS, new_session

app = FastAPI(title="Roameo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Message(BaseModel):
    message: str
    session_id: str | None = None


@app.get("/api/health")
def health():
    return {"ok": True, "llm": llm.available(), "model": llm.DEFAULT_MODEL if llm.available() else None,
            "live_tools": {k: bool(os.getenv(k)) for k in
                           ["SERPAPI_API_KEY", "GOOGLE_API_KEY", "TICKETMASTER_API_KEY"]}}


@app.post("/api/message")
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


@app.get("/api/export/{session_id}.ics", response_class=PlainTextResponse)
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
