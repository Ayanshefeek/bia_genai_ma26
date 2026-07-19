"""LLM and mock streaming logic for the productivity assistant."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI

from backend.config import get_settings


SYSTEM_PROMPT = """
You are a productivity assistant inside a real-time dashboard.

Your job:
1. Understand the incoming productivity event.
2. Produce a concise and actionable response.
3. Include a suggested next action.
4. Keep the output practical enough for a busy professional.

Output structure:
- Quick read
- Suggested response or preparation notes
- Next action
""".strip()


def build_event_prompt(event: dict[str, Any]) -> str:
    """Build a user prompt from a stored productivity event.

    Args:
        event: Stored event dictionary.

    Returns:
        str: Prompt text for the LLM.
    """

    safe_event = {
        "event_type": event.get("event_type"),
        "title": event.get("title"),
        "priority": event.get("priority"),
        "source": event.get("source"),
        "payload": event.get("payload", {}),
    }
    return (
        "A new productivity event arrived. Analyse it and draft the live assistant "
        "response that should stream into the dashboard.\n\n"
        f"EVENT:\n{json.dumps(safe_event, indent=2)}"
    )


def build_mock_response(event: dict[str, Any]) -> str:
    """Create a deterministic response used when mock mode is enabled.

    Args:
        event: Stored productivity event.

    Returns:
        str: Assistant response text.
    """

    event_type = event.get("event_type", "event")
    title = event.get("title", "Untitled event")
    priority = event.get("priority", "normal")
    payload = event.get("payload", {})

    if event_type == "email":
        sender = payload.get("from", "the sender")
        return (
            f"Quick read: A {priority}-priority email from {sender} needs a timely reply about "
            f"'{title}'.\n\n"
            "Suggested response:\n"
            "Thanks for the note. Here is a concise status update: completed work is ready, "
            "the main open risk is the pending integration check, and the next dependency is "
            "confirmation from the stakeholder team.\n\n"
            "Next action: Send the update now, then add a follow-up reminder for any missing input."
        )

    if event_type == "calendar":
        meeting_title = payload.get("meeting_title", title)
        agenda = payload.get("agenda", [])
        agenda_text = "; ".join(agenda) if agenda else "confirm agenda and owners"
        return (
            f"Quick read: The upcoming meeting '{meeting_title}' needs preparation.\n\n"
            f"Preparation notes: Review these agenda points: {agenda_text}. Prepare one decision "
            "question, one risk update, and one owner for the next action.\n\n"
            "Next action: Open the meeting notes document and add a three-bullet briefing before joining."
        )

    return (
        f"Quick read: The task '{title}' is marked {priority} and needs a clear handoff.\n\n"
        "Handoff checklist: write the current blocker, the latest known status, the next owner, "
        "the due time, and the escalation path. Keep it short enough to paste into the task tracker.\n\n"
        "Next action: Create the checklist and notify the owner before the due time."
    )


def split_for_streaming(text: str, target_size: int = 18) -> list[str]:
    """Split text into small readable chunks for classroom streaming.

    Args:
        text: Full text to stream.
        target_size: Approximate character count per chunk.

    Returns:
        list[str]: Ordered text chunks.
    """

    chunks: list[str] = []
    current = ""
    for token in text.split(" "):
        candidate = f"{current} {token}".strip()
        if len(candidate) >= target_size:
            chunks.append(candidate + " ")
            current = ""
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


async def stream_mock_response(event: dict[str, Any]) -> AsyncIterator[str]:
    """Stream deterministic chunks without using a paid API.

    Args:
        event: Stored productivity event.

    Yields:
        str: Next mock response chunk.
    """

    settings = get_settings()
    for chunk in split_for_streaming(build_mock_response(event)):
        await asyncio.sleep(settings.token_delay_seconds)
        yield chunk


async def stream_openai_response(event: dict[str, Any]) -> AsyncIterator[str]:
    """Stream text deltas from the OpenAI Responses API.

    Args:
        event: Stored productivity event.

    Yields:
        str: Next streamed text delta from OpenAI.
    """

    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # COST NOTE: With gpt-4o-mini and these short prompts, one full classroom demo
    # should usually cost well below ₹5 / US$0.10, depending on current pricing.
    async with client.responses.stream(
        model=settings.openai_model,
        instructions=SYSTEM_PROMPT,
        input=build_event_prompt(event),
        temperature=0.2,
    ) as stream:
        async for stream_event in stream:
            event_type = getattr(stream_event, "type", "")
            if event_type == "response.output_text.delta":
                delta = getattr(stream_event, "delta", "")
                if delta:
                    yield delta
            elif event_type == "response.completed":
                break
            # TRAINER NOTE: Unknown stream events are intentionally ignored.
            # Production systems should log them for observability.


async def stream_productivity_response(event: dict[str, Any]) -> AsyncIterator[str]:
    """Stream an assistant response using OpenAI or mock mode.

    Args:
        event: Stored productivity event.

    Yields:
        str: Next response chunk to persist and broadcast.
    """

    settings = get_settings()
    if settings.use_mock_llm or not settings.openai_api_key:
        async for chunk in stream_mock_response(event):
            yield chunk
        return

    try:
        async for chunk in stream_openai_response(event):
            yield chunk
    except Exception as exc:  # noqa: BLE001 - classroom fallback should be explicit.
        fallback = (
            "\n\n[OpenAI streaming failed during the demo. Falling back to a local "
            f"mock response. Error summary: {type(exc).__name__}: {exc}]\n\n"
        )
        yield fallback
        async for chunk in stream_mock_response(event):
            yield chunk
