"""Shared data structures passed between the agents."""
from __future__ import annotations

from datetime import date
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class TripSpec(BaseModel):
    """What the user wants. Produced by the Intake agent, edited by feedback."""
    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    nights: int = 2
    travelers: int = 1
    budget_usd: Optional[float] = None
    interests: list[str] = Field(default_factory=list)
    transport: Literal["fly", "drive", "local"] = "fly"
    hotel_preference: Literal["budget", "mid", "luxury", "any"] = "any"
    assumptions: list[str] = Field(default_factory=list)


class TraceStep(BaseModel):
    agent: str
    action: str
    detail: str = ""


class DayPlan(BaseModel):
    date: date
    weather: Optional[str] = None
    rain_chance: Optional[int] = None
    items: list[dict[str, Any]] = Field(default_factory=list)


class Plan(BaseModel):
    flight: Optional[dict[str, Any]] = None
    hotel: Optional[dict[str, Any]] = None
    days: list[DayPlan] = Field(default_factory=list)
    cost_breakdown: dict[str, float] = Field(default_factory=dict)
    total_cost: float = 0.0
    summary: str = ""
    issues: list[str] = Field(default_factory=list)
    revisions: int = 0
    changes: list[str] = Field(default_factory=list)  # what a revision added/removed


Status = Literal["needs_clarification", "awaiting_approval", "approved", "error"]


class SessionState(BaseModel):
    session_id: str
    status: Status = "needs_clarification"
    spec: TripSpec = Field(default_factory=TripSpec)
    questions: list[str] = Field(default_factory=list)
    research: dict[str, Any] = Field(default_factory=dict)
    plan: Optional[Plan] = None
    trace: list[TraceStep] = Field(default_factory=list)
    history: list[dict[str, str]] = Field(default_factory=list)
    mode: str = "demo"
