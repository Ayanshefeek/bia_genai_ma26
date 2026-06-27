"""Prompt builders for generator, critic, and refiner roles."""

from __future__ import annotations

from typing import Iterable


def _join_reflections(reflections: Iterable[str] | None) -> str:
    """Format reflection memory for prompt context.

    Params:
        reflections: Prior lessons from the critique loop.
    Returns:
        A clean bullet list for prompt insertion.
    """
    if not reflections:
        return "No prior reflections yet."
    return "\n".join(f"- {item}" for item in reflections if item.strip())


def build_generator_messages(brief: str) -> list[dict[str, str]]:
    """Create messages for the first-draft generator.

    Params:
        brief: Writing brief supplied by the user or trainer.
    Returns:
        Chat messages for the generator model call.
    """
    return [
        {
            "role": "system",
            "content": (
                "You are a concise professional copywriter. Produce the first draft only. "
                "Do not critique your own answer in this step."
            ),
        },
        {
            "role": "user",
            "content": f"Create a draft for this brief:\n\n{brief}",
        },
    ]


def build_critic_messages(
    brief: str,
    draft: str,
    rubric: str,
    constitution: str,
    reflections: Iterable[str] | None = None,
    pass_score: int = 8,
) -> list[dict[str, str]]:
    """Create messages for a rubric-based evaluator.

    Params:
        brief: Original task brief.
        draft: Draft being evaluated.
        rubric: Scoring criteria.
        constitution: Principles that guide the critique.
        reflections: Prior lessons from earlier attempts.
        pass_score: Score required to stop retrying.
    Returns:
        Chat messages that request strict JSON output.
    """
    schema_instructions = """
Return ONLY valid JSON with this exact shape:
{
  "score": 1,
  "passed": false,
  "summary": "short overall judgment",
  "strengths": ["what is working"],
  "issues": [
{
  "criterion": "rubric criterion name",
  "severity": "minor | major | blocking",
  "explanation": "what is wrong",
  "revision_instruction": "specific rewrite instruction"
}
  ],
  "reflection_memory": "one reusable lesson for the next attempt",
  "revised_strategy": "the next rewrite strategy"
}
"""
    return [
        {
            "role": "system",
            "content": (
                "You are a strict but constructive evaluator. Judge the draft against the brief, "
                "rubric, and principles. Do not praise vague text. Do not invent facts. "
                "A draft passes only when it earns at least the required score and has no blocking issue."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Original brief:\n{brief}\n\n"
                f"Rubric:\n{rubric}\n\n"
                f"Principles / constitution:\n{constitution}\n\n"
                f"Prior reflection memory:\n{_join_reflections(reflections)}\n\n"
                f"Passing score: {pass_score}/10\n\n"
                f"Draft to critique:\n{draft}\n\n"
                f"{schema_instructions}"
            ),
        },
    ]


def build_refiner_messages(
    brief: str,
    draft: str,
    critique_json: str,
    constitution: str,
    reflections: Iterable[str] | None = None,
) -> list[dict[str, str]]:
    """Create messages for the revision step.

    Params:
        brief: Original task brief.
        draft: Current draft.
        critique_json: Structured critique as JSON text.
        constitution: Principles to preserve during revision.
        reflections: Prior lessons from earlier attempts.
    Returns:
        Chat messages for the refiner model call.
    """
    return [
        {
            "role": "system",
            "content": (
                "You are a refinement editor. Rewrite the draft using the critique. "
                "Return only the revised draft, with no commentary."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Original brief:\n{brief}\n\n"
                f"Principles to preserve:\n{constitution}\n\n"
                f"Prior reflection memory:\n{_join_reflections(reflections)}\n\n"
                f"Current draft:\n{draft}\n\n"
                f"Structured critique:\n{critique_json}\n\n"
                "Rewrite the draft so it better satisfies the brief and rubric."
            ),
        },
    ]
