"""Pydantic schemas for webhook payloads, job tracking, and agent outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class EventSource(str, Enum):
    """Supported simulated event sources."""

    FORM = "form"
    GITHUB = "github"
    EMAIL = "email"
    MANUAL = "manual"


class JobStatus(str, Enum):
    """Lifecycle states for background processing jobs."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TextSubmittedEvent(BaseModel):
    """Generic text-submission event received through a webhook."""

    event_id: str = Field(..., min_length=3, description="Unique event delivery ID.")
    event_type: str = Field(
        ...,
        min_length=3,
        description="Type of external event, such as support.form_submitted.",
    )
    source: EventSource = Field(..., description="System that produced the event.")
    text: str = Field(..., min_length=10, description="Text that the agent should analyse.")
    user_email: str | None = Field(
        default=None,
        description="Optional user email. Kept simple to avoid an extra email-validator dependency.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("user_email")
    @classmethod
    def user_email_should_look_like_email(cls, value: str | None) -> str | None:
        """Validate simple email shape without requiring an external dependency.

        Args:
            value: Optional email string.

        Returns:
            The original value when it is empty or looks like an email.

        Raises:
            ValueError: If the email value is present but malformed.
        """
        if value is None or value == "":
            return value
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("user_email must look like an email address.")
        return value


class GitHubIssueEvent(BaseModel):
    """Simplified GitHub issue webhook payload for classroom simulation."""

    event_id: str = Field(..., min_length=3)
    action: Literal["opened", "edited", "reopened", "closed"]
    repository: str = Field(..., min_length=2)
    issue_number: int = Field(..., ge=1)
    issue_title: str = Field(..., min_length=3)
    issue_body: str = Field(..., min_length=10)
    sender: str = Field(..., min_length=2)

    def to_text_event(self) -> TextSubmittedEvent:
        """Convert a GitHub issue event into the generic text event shape.

        Returns:
            TextSubmittedEvent with the issue title/body as agent input.
        """
        return TextSubmittedEvent(
            event_id=self.event_id,
            event_type=f"github.issue.{self.action}",
            source=EventSource.GITHUB,
            text=f"Issue #{self.issue_number}: {self.issue_title}\n\n{self.issue_body}",
            metadata={
                "repository": self.repository,
                "issue_number": self.issue_number,
                "sender": self.sender,
                "github_action": self.action,
            },
        )


class AgentResult(BaseModel):
    """Structured output produced by the summarisation agent."""

    summary: str = Field(..., min_length=3)
    category: str = Field(..., min_length=2)
    priority: Literal["low", "medium", "high"]
    recommended_action: str = Field(..., min_length=5)


class JobAcceptedResponse(BaseModel):
    """Response returned immediately after a webhook is accepted."""

    job_id: str
    status: JobStatus
    message: str


class JobRecord(BaseModel):
    """In-memory job record used for demo state tracking."""

    job_id: str
    status: JobStatus
    event_id: str
    event_type: str
    source: EventSource
    created_at: datetime
    updated_at: datetime
    result: AgentResult | None = None
    error: str | None = None


class JobStatusResponse(BaseModel):
    """Response returned when checking the status of a background job."""

    job_id: str
    status: JobStatus
    event_id: str
    event_type: str
    source: EventSource
    created_at: datetime
    updated_at: datetime
    result: AgentResult | None = None
    error: str | None = None


class JobListResponse(BaseModel):
    """Response returned when listing recent jobs."""

    jobs: list[JobStatusResponse]


class HealthResponse(BaseModel):
    """Health check response for the FastAPI service."""

    status: Literal["ok"]
    app_name: str
    version: str
    mock_llm_enabled: bool
