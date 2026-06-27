"""Small OpenAI client wrapper used by the practical notebook.

The wrapper keeps model choice, API key loading, JSON-mode calls, and offline
fallback behavior in one place so the classroom demo remains easy to follow.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv


@dataclass(frozen=True)
class LLMSettings:
    """Runtime settings for model calls.

    Params:
        api_key: OpenAI API key.
        model: Model name.
        offline_demo: Whether to use deterministic simulated responses.
    Returns:
        Immutable settings object.
    """

    api_key: str | None
    model: str
    offline_demo: bool


def load_settings() -> LLMSettings:
    """Load settings from environment variables.

    Params:
        None.
    Returns:
        LLMSettings with API and model configuration.
    """
    load_dotenv()
    offline_demo = os.getenv("BIA_OFFLINE_DEMO", "false").strip().lower() in {"1", "true", "yes"}
    return LLMSettings(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        offline_demo=offline_demo,
    )


def check_api_ready(settings: LLMSettings | None = None) -> None:
    """Raise a friendly error if no API key is available.

    Params:
        settings: Optional preloaded settings.
    Returns:
        None. Raises RuntimeError when configuration is missing.
    """
    settings = settings or load_settings()
    if settings.offline_demo:
        return
    if not settings.api_key:
        raise RuntimeError(
            "OPENAI_API_KEY was not found. Copy .env.sample to .env and add your key, "
            "or set BIA_OFFLINE_DEMO=true for a deterministic offline classroom fallback."
        )


def _offline_response(messages: list[dict[str, str]], json_mode: bool = False) -> str:
    """Return deterministic demo output when the API is unavailable.

    Params:
        messages: Chat messages from the caller.
        json_mode: Whether the caller expects JSON.
    Returns:
        Simulated text or JSON string.
    """
    combined = "\n".join(m.get("content", "") for m in messages).lower()

    if json_mode or "return only valid json" in combined:
        improved_markers = [
            "agent workflows",
            "portfolio of practical demos",
            "live information session",
            "without unrealistic promises",
        ]
        if any(marker in combined for marker in improved_markers):
            return json.dumps(
                {
                    "score": 9,
                    "passed": True,
                    "summary": "The revised draft is specific, credible, and well matched to working professionals.",
                    "strengths": [
                        "Explains concrete program benefits",
                        "Avoids unrealistic career promises",
                        "Ends with a specific call to action"
                    ],
                    "issues": [
                        {
                            "criterion": "Constraint following",
                            "severity": "minor",
                            "explanation": "The draft should still be checked against the requested word count before publishing.",
                            "revision_instruction": "Keep the final version within the requested 140–180 word range."
                        }
                    ],
                    "reflection_memory": "Specific, credible benefits outperform generic AI enthusiasm for this audience.",
                    "revised_strategy": "Preserve the concrete benefits and concise professional tone."
                },
                indent=2,
            )

        return json.dumps(
            {
                "score": 6,
                "passed": False,
                "summary": "The draft is clear but too generic for a skeptical working-professional audience.",
                "strengths": [
                    "Mentions Generative AI and Agentic AI",
                    "Keeps the tone reasonably professional"
                ],
                "issues": [
                    {
                        "criterion": "Specificity",
                        "severity": "major",
                        "explanation": "The draft uses broad claims like 'future ready' without explaining what the program actually builds.",
                        "revision_instruction": "Mention live expert-led classes, hands-on projects, and practical agent-building outcomes."
                    },
                    {
                        "criterion": "Evidence quality",
                        "severity": "major",
                        "explanation": "The line about better opportunities is vague and could sound like an unsupported career promise.",
                        "revision_instruction": "Frame career relevance as portfolio and skill development, not guaranteed outcomes."
                    },
                    {
                        "criterion": "Call to action",
                        "severity": "minor",
                        "explanation": "The call to action is present but generic.",
                        "revision_instruction": "End with a specific action such as joining a live information session or reviewing the curriculum."
                    }
                ],
                "reflection_memory": "Avoid generic AI hype; tie every claim to a concrete program feature or learner outcome.",
                "revised_strategy": "Rewrite for busy professionals using specific benefits, credible language, and a single practical call to action."
            },
            indent=2,
        )

    if "refinement editor" in combined or "rewrite the draft" in combined:
        return (
            "Subject: Build practical GenAI and agentic AI skills without pausing your career\n\n"
            "Hi,\n\n"
            "If you are already working in software, data, DevOps, or technology management, "
            "the next step is not just learning AI terms — it is learning how to build useful AI systems. "
            "This live weekend program in Generative AI and Agentic AI Development is designed around expert-led "
            "classes, guided coding practice, and hands-on projects that mirror real workplace use cases.\n\n"
            "You will work with prompting patterns, agent workflows, retrieval systems, evaluation loops, and "
            "deployment considerations while building a portfolio of practical demos. The focus is career relevance, "
            "not hype or unrealistic promises.\n\n"
            "Review the curriculum and join the next live information session to see whether the program fits your goals."
        )

    return (
        "Subject: Learn practical GenAI and agentic AI with live expert guidance\n\n"
        "Hi,\n\n"
        "Generative AI is moving quickly, but working professionals need more than tool demos. "
        "This live weekend program helps you build practical skills in Generative AI and Agentic AI Development "
        "through expert-led classes, structured practice, and hands-on projects.\n\n"
        "You will explore prompting, agent workflows, retrieval, evaluation, and deployment patterns that connect "
        "directly to modern AI work. The program is designed for busy professionals who want credible, classroom-led "
        "learning without unrealistic promises.\n\n"
        "Explore the curriculum and join an information session to decide your next step."
    )


def call_chat_model(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 900,
    json_mode: bool = False,
) -> str:
    """Call the configured chat model and return text.

    Params:
        messages: List of role/content chat messages.
        temperature: Sampling temperature.
        max_tokens: Output token budget.
        json_mode: Whether to request JSON object output.
    Returns:
        Model response text.
    """
    settings = load_settings()
    if settings.offline_demo:
        return _offline_response(messages, json_mode=json_mode)

    check_api_ready(settings)

    # Import lazily so offline demos do not require the package at import time.
    from openai import OpenAI

    client = OpenAI(api_key=settings.api_key)

    kwargs: dict[str, Any] = {
        "model": settings.model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    # COST NOTE: With gpt-4o-mini and these small prompts, a full classroom demo
    # usually costs only a few cents. Token use grows with draft length and iterations.
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


def parse_json_object(raw_text: str) -> dict[str, Any]:
    """Parse a JSON object from model output.

    Params:
        raw_text: Raw model response.
    Returns:
        Parsed JSON dictionary.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).replace("JSON\n", "", 1)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Evaluator did not return valid JSON. Raw output:\n{raw_text}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object, received: {type(value).__name__}")
    return value
