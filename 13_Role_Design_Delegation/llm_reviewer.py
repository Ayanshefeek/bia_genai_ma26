"""Optional LLM critique for role-design blueprints.

The practical runs fully offline without this file. Use it only when a trainer wants
to show how an LLM can critique a team design after the deterministic validators run.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def critique_blueprint_with_llm(
    blueprint_path: str | Path,
    model_name: Optional[str] = None,
    max_chars: int = 12000,
) -> str:
    """Ask an LLM to critique a role-design blueprint.

    Args:
        blueprint_path: Path to the blueprint JSON.
        model_name: Optional model override. Defaults to OPENAI_MODEL or gpt-4o-mini.
        max_chars: Safety limit on blueprint text sent to the model.

    Returns:
        Critique text. If no API key is configured, returns a friendly skip message.
    """
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "Optional LLM critique skipped: OPENAI_API_KEY is not set. "
            "The deterministic validators still work offline."
        )

    # COST NOTE: For the bundled sample blueprint, this usually costs only a few cents
    # or less with gpt-4o-mini, depending on current provider pricing and token counts.
    from openai import OpenAI

    model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    blueprint_text = Path(blueprint_path).read_text(encoding="utf-8")[:max_chars]

    prompt = f"""
You are reviewing a multi-agent role-design blueprint for a classroom exercise.

Evaluate the design on:
1. Role clarity
2. RACI ownership
3. Handoff contract completeness
4. Incentive alignment
5. Conflict and loop risks
6. Readiness for implementation in a research bot

Give concise, actionable feedback. Do not rewrite the whole blueprint.

Blueprint JSON:
{blueprint_text}
"""

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        instructions="You are a senior agentic AI architect reviewing classroom design artifacts.",
        input=prompt,
    )
    return response.output_text
