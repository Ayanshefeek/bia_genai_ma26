"""Optional AutoGen evaluator-agent preview.

This file is intentionally small. The full AutoGen deep-dive comes later in the
course, so this preview only shows how the same evaluator role can be wrapped
as an AutoGen AssistantAgent.
"""

from __future__ import annotations

import os


async def run_autogen_evaluator_preview(brief: str, draft: str, rubric: str, constitution: str) -> str:
    """Run a minimal AutoGen AssistantAgent as a critique agent.

    Params:
        brief: Original task brief.
        draft: Draft to evaluate.
        rubric: Scoring rubric.
        constitution: Principles for critique.
    Returns:
        Final message content from the AutoGen evaluator.
    """
    try:
        from autogen_agentchat.agents import AssistantAgent
        from autogen_ext.models.openai import OpenAIChatCompletionClient
    except ImportError as exc:
        raise ImportError(
            "AutoGen preview dependencies are not installed. Run: "
            "pip install -r requirements_autogen.txt"
        ) from exc

    model_client = OpenAIChatCompletionClient(
        model=os.getenv("AUTOGEN_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini")),
        temperature=0,
        response_format={"type": "json_object"},
    )

    evaluator = AssistantAgent(
        name="writing_critic",
        model_client=model_client,
        system_message=(
            "You are an evaluator agent. Return only JSON with score, summary, issues, "
            "and revision_instructions. Be strict, practical, and concise."
        ),
    )

    task = (
        f"Brief:\n{brief}\n\n"
        f"Rubric:\n{rubric}\n\n"
        f"Principles:\n{constitution}\n\n"
        f"Draft:\n{draft}"
    )

    # COST NOTE: This is one extra LLM call beyond the main practical loop.
    result = await evaluator.run(task=task)
    await model_client.close()

    return str(result.messages[-1].content)
