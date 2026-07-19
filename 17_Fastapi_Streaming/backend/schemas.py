"""Pydantic schemas for productivity events and assistant runs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


EventType = Literal["email", "calendar", "task"]
Priority = Literal["low", "normal", "high", "urgent"]
RunStatus = Literal["queued", "running", "completed", "failed"]


class ProductivityEventCreate(BaseModel):
    """Incoming event payload used to simulate Gmail, Calendar, and task triggers."""

    event_type: EventType = Field(..., description="Type of productivity event.")
    title: str = Field(..., min_length=3, max_length=120)
    source: str = Field(default="mock", max_length=50)
    priority: Priority = Field(default="normal")
    payload: dict[str, Any] = Field(default_factory=dict)


class ProductivityEvent(ProductivityEventCreate):
    """Stored productivity event returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    created_at: datetime


class AssistantRun(BaseModel):
    """Stored assistant run connected to one productivity event."""

    id: str
    event_id: str
    status: RunStatus
    final_output: str | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class StreamChunk(BaseModel):
    """A persisted token/delta emitted during an assistant run."""

    id: int
    run_id: str
    sequence: int
    content: str
    created_at: datetime


class TriggerResponse(BaseModel):
    """Response returned when a mock event has been triggered."""

    event_id: str
    run_id: str
    websocket_url: str
    status: RunStatus


class StartRunResponse(BaseModel):
    """Response returned when a queued run has been started."""

    run_id: str
    status: RunStatus
    message: str
