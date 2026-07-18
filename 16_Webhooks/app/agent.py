"""Summarisation agent used by the webhook trigger demo."""

from __future__ import annotations

import json
import re
from typing import Any


from app.schemas import AgentResult, TextSubmittedEvent
from app.settings import get_settings


def _mock_agent_result(event: TextSubmittedEvent) -> AgentResult:
    """Generate a deterministic fallback result without calling an LLM.

    Args:
        event: Validated text-submission event.

    Returns:
        Structured AgentResult suitable for demos without API keys.
    """
    text = event.text.strip()
    first_sentence = re.split(r"(?<=[.!?])\s+", text)[0]
    lower_text = text.lower()

    if any(word in lower_text for word in ["urgent", "broken", "error", "failed", "security"]):
        priority = "high"
    elif any(word in lower_text for word in ["confusing", "unclear", "question", "help"]):
        priority = "medium"
    else:
        priority = "low"

    if any(word in lower_text for word in ["api key", ".env", "install", "setup"]):
        category = "setup_support"
    elif any(word in lower_text for word in ["bug", "error", "failed", "traceback"]):
        category = "technical_issue"
    elif any(word in lower_text for word in ["invoice", "payment", "billing"]):
        category = "billing"
    else:
        category = "general_query"

    return AgentResult(
        summary=first_sentence[:220],
        category=category,
        priority=priority,
        recommended_action=(
            "Review the event details, respond with the most relevant help, "
            "and log the outcome for follow-up."
        ),
    )


def _parse_agent_json(raw_content: str) -> AgentResult:
    """Parse an LLM JSON response into an AgentResult.

    Args:
        raw_content: JSON text returned by the model.

    Returns:
        Validated AgentResult.

    Raises:
        ValueError: If the content is not valid JSON for AgentResult.
    """
    try:
        payload: dict[str, Any] = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON: {raw_content}") from exc
    return AgentResult(**payload)


def summarise_event(event: TextSubmittedEvent) -> AgentResult:
    """Summarise, classify, and prioritize an incoming event.

    Args:
        event: Validated webhook event.

    Returns:
        Structured agent result.

    Raises:
        RuntimeError: If OpenAI mode is enabled but no API key is configured.
        ValueError: If the model returns malformed JSON.
    """
    settings = get_settings()
    if settings.use_mock_llm:
        return _mock_agent_result(event)

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required when USE_MOCK_LLM=false.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The openai package is required when USE_MOCK_LLM=false. "
            "Install dependencies with: pip install -r requirements.txt"
        ) from exc

    client = OpenAI(api_key=settings.openai_api_key)

    # COST NOTE: With gpt-4o-mini, this short classification/summarisation call
    # is typically far below one cent for classroom-sized payloads.
    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a concise operations assistant. Return ONLY valid JSON with keys: "
                    "summary, category, priority, recommended_action. Priority must be one of "
                    "low, medium, high."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Event type: {event.event_type}\n"
                    f"Source: {event.source}\n"
                    f"Metadata: {json.dumps(event.metadata)}\n\n"
                    f"Text to analyse:\n{event.text}"
                ),
            },
        ],
    )

    raw_content = response.choices[0].message.content or "{}"
    return _parse_agent_json(raw_content)
