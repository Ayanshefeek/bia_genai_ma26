"""Pydantic request and response schemas for the avatar persona agent API."""

from typing import Literal

from pydantic import BaseModel, Field


AvatarState = Literal["idle", "listening", "thinking", "speaking", "error"]


class ChatRequest(BaseModel):
    """Request body for a persona agent chat turn."""

    message: str = Field(..., min_length=1, max_length=2000)
    persona_id: str = Field(default="bia_ai_mentor")
    include_audio: bool = Field(default=True)


class AvatarCue(BaseModel):
    """A small instruction that helps the frontend animate the avatar."""

    state: AvatarState
    duration_ms: int = Field(..., ge=100, le=60000)
    expression: str = Field(default="neutral")
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """Response returned after the agent generates an answer."""

    user_text: str
    assistant_text: str
    persona_id: str
    audio_url: str | None
    avatar_cues: list[AvatarCue]
    latency_ms: int
    cost_note: str
    mock_mode: bool


class PersonaSummary(BaseModel):
    """Visible summary of a persona option."""

    persona_id: str
    name: str
    role: str
    tone: str
    boundaries: list[str]


class TranscriptionResponse(BaseModel):
    """Response returned after uploaded speech is transcribed."""

    text: str
    mock_mode: bool
    cost_note: str
