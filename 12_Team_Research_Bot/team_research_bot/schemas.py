"""Pydantic schemas for serialized communication in the Team Research Bot.

The central teaching idea: every agent handoff should look like a typed API
contract, not a vague chat message.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentRole(str, Enum):
    """Named roles in the research team."""

    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    WRITER = "writer"
    FACT_CHECKER = "fact_checker"
    EDITOR = "editor"


class MessageType(str, Enum):
    """Allowed types of messages passed between agents."""

    TASK = "task"
    RESULT = "result"
    CRITIQUE = "critique"
    FINAL = "final"


class StrictBaseModel(BaseModel):
    """Base model with strict defaults for teaching schema discipline."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class EvidenceItem(StrictBaseModel):
    """A specific evidence snippet from the local source pack."""

    source_id: str = Field(..., description="Stable source identifier, e.g. SRC-001.")
    title: str = Field(..., description="Human-readable source title.")
    snippet: str = Field(..., min_length=30, description="Evidence text copied or summarized from source.")
    relevance_score: float = Field(..., ge=0, le=1, description="How relevant the evidence is to the query.")


class ResearchFinding(StrictBaseModel):
    """A research claim backed by evidence."""

    claim: str = Field(..., min_length=20)
    evidence: list[EvidenceItem] = Field(..., min_length=1)
    confidence: float = Field(..., ge=0, le=1)
    limitations: str = Field(..., description="What the evidence does not fully prove.")


class ResearchReport(StrictBaseModel):
    """Researcher output passed to the Writer agent."""

    topic: str
    findings: list[ResearchFinding] = Field(..., min_length=2)
    unresolved_questions: list[str] = Field(default_factory=list)
    overall_confidence: float = Field(..., ge=0, le=1)


class DraftSection(StrictBaseModel):
    """One section of the Writer's draft report."""

    heading: str
    content: str = Field(..., min_length=80)
    claim_ids: list[int] = Field(..., description="Indexes of ResearchFinding items used in this section.")


class DraftReport(StrictBaseModel):
    """Writer output passed to the Fact-Checker agent."""

    title: str
    executive_summary: str = Field(..., min_length=80)
    sections: list[DraftSection] = Field(..., min_length=2)
    risks_or_uncertainties: list[str] = Field(default_factory=list)
    source_ids_used: list[str] = Field(default_factory=list)


class ClaimCheck(StrictBaseModel):
    """Fact-check result for one claim or section."""

    claim: str
    verdict: Literal["supported", "partially_supported", "unsupported"]
    evidence_refs: list[str] = Field(default_factory=list)
    issue: str
    recommendation: str


class FactCheckReport(StrictBaseModel):
    """Fact-Checker output passed to the Writer or Editor."""

    checks: list[ClaimCheck] = Field(..., min_length=1)
    summary: str
    revision_required: bool
    overall_reliability: float = Field(..., ge=0, le=1)


class FinalReport(StrictBaseModel):
    """Editor output returned to the user."""

    title: str
    final_answer: str = Field(..., min_length=150)
    key_takeaways: list[str] = Field(..., min_length=3)
    caveats: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    editor_notes: str


class AgentMessage(StrictBaseModel):
    """Serializable envelope for any inter-agent handoff."""

    trace_id: str
    sender: AgentRole
    receiver: AgentRole
    message_type: MessageType
    task: str
    payload: dict[str, Any]
    confidence: float = Field(..., ge=0, le=1)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @field_validator("trace_id")
    @classmethod
    def trace_id_must_not_be_empty(cls, value: str) -> str:
        """Reject blank trace IDs because they break debugging."""

        if not value.strip():
            raise ValueError("trace_id cannot be blank")
        return value


class PipelineState(StrictBaseModel):
    """Shared state object used by the orchestrator across the team."""

    run_id: str = Field(default_factory=lambda: f"run_{uuid4().hex[:10]}")
    user_query: str
    source_ids_consulted: list[str] = Field(default_factory=list)
    messages: list[AgentMessage] = Field(default_factory=list)
    research_report: ResearchReport | None = None
    draft_report: DraftReport | None = None
    fact_check_report: FactCheckReport | None = None
    final_report: FinalReport | None = None
    revision_count: int = 0
    max_revisions: int = 1
    status: Literal["created", "running", "needs_revision", "completed", "failed"] = "created"
    errors: list[str] = Field(default_factory=list)


def new_trace_id(prefix: str = "trace") -> str:
    """Return a short unique trace ID for logs and messages."""

    return f"{prefix}_{uuid4().hex[:8]}"


def make_message(
    sender: AgentRole,
    receiver: AgentRole,
    message_type: MessageType,
    task: str,
    payload_model: BaseModel,
    confidence: float,
) -> AgentMessage:
    """Create a serialized inter-agent message from a Pydantic payload."""

    return AgentMessage(
        trace_id=new_trace_id("msg"),
        sender=sender,
        receiver=receiver,
        message_type=message_type,
        task=task,
        payload=payload_model.model_dump(),
        confidence=confidence,
    )
