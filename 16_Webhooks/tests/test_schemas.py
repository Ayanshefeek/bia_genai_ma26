"""Lightweight tests for schema validation and mock agent behavior."""

from __future__ import annotations

from app.agent import _mock_agent_result
from app.schemas import GitHubIssueEvent, TextSubmittedEvent


def test_text_event_validation() -> None:
    """A valid text event should parse cleanly."""
    event = TextSubmittedEvent(
        event_id="evt_test_1",
        event_type="support.form_submitted",
        source="form",
        text="The setup guide is confusing and I need help with the API key.",
        user_email="learner@example.com",
    )
    assert event.source == "form"


def test_github_event_conversion() -> None:
    """A GitHub issue event should convert into the generic text-event shape."""
    event = GitHubIssueEvent(
        event_id="evt_gh_test",
        action="opened",
        repository="demo/repo",
        issue_number=7,
        issue_title="API key setup fails",
        issue_body="The application fails when the .env file is missing.",
        sender="tester",
    )
    text_event = event.to_text_event()
    assert text_event.source == "github"
    assert "Issue #7" in text_event.text


def test_mock_agent_result() -> None:
    """Mock mode should produce a valid structured result without an API call."""
    event = TextSubmittedEvent(
        event_id="evt_test_2",
        event_type="support.form_submitted",
        source="form",
        text="Urgent: The setup guide fails when the API key is missing.",
    )
    result = _mock_agent_result(event)
    assert result.priority == "high"
    assert result.category == "setup_support"
