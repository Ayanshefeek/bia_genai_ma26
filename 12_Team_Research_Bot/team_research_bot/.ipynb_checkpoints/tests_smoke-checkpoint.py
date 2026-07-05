"""Smoke tests for the Team Research Bot package.

These are intentionally lightweight so trainers can run them before class.
"""

from __future__ import annotations

import os

from llm import StructuredLLMClient
from orchestrator import ResearchBotOrchestrator
from schemas import AgentMessage, AgentRole, MessageType
from source_loader import load_source_pack


def test_message_schema_rejects_bad_confidence() -> None:
    """Pydantic should reject invalid confidence values."""

    try:
        AgentMessage(
            trace_id="test",
            sender=AgentRole.RESEARCHER,
            receiver=AgentRole.WRITER,
            message_type=MessageType.RESULT,
            task="bad confidence demo",
            payload={},
            confidence=1.5,
        )
    except Exception:
        return
    raise AssertionError("Invalid confidence should have failed validation.")


def test_mock_pipeline_runs_end_to_end() -> None:
    """Mock mode should complete without OpenAI credentials."""

    os.environ["USE_MOCK_LLM"] = "true"
    client = StructuredLLMClient(use_mock=True)
    documents = load_source_pack("data/source_pack")
    orchestrator = ResearchBotOrchestrator(client, documents)
    state = orchestrator.run(
        "What should an organization consider before using AI agents in customer support?"
    )
    assert state.status == "completed"
    assert state.final_report is not None
    assert len(state.messages) >= 4


if __name__ == "__main__":
    test_message_schema_rejects_bad_confidence()
    test_mock_pipeline_runs_end_to_end()
    print("Smoke tests passed.")
