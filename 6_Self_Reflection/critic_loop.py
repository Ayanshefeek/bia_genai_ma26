"""Generate-critique-refine loop for the practical session."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from llm_client import call_chat_model, parse_json_object
from prompts import build_critic_messages, build_generator_messages, build_refiner_messages
from schemas import CritiqueResult, IterationRecord


def read_text(path: str | Path) -> str:
    """Read a UTF-8 text file.

    Params:
        path: File path.
    Returns:
        File contents as text.
    """
    return Path(path).read_text(encoding="utf-8").strip()


def generate_first_draft(brief: str) -> str:
    """Generate an initial draft from a brief.

    Params:
        brief: Task brief.
    Returns:
        Draft text.
    """
    messages = build_generator_messages(brief)
    return call_chat_model(messages, temperature=0.4, max_tokens=700).strip()


def critique_draft(
    brief: str,
    draft: str,
    rubric: str,
    constitution: str,
    reflections: Iterable[str] | None = None,
    pass_score: int = 8,
) -> CritiqueResult:
    """Evaluate a draft against a rubric and constitution.

    Params:
        brief: Original task brief.
        draft: Draft to evaluate.
        rubric: Scoring rubric.
        constitution: Principles for critique.
        reflections: Prior reflection memory.
        pass_score: Score required to pass.
    Returns:
        Structured critique result.
    """
    messages = build_critic_messages(
        brief=brief,
        draft=draft,
        rubric=rubric,
        constitution=constitution,
        reflections=reflections,
        pass_score=pass_score,
    )
    raw = call_chat_model(messages, temperature=0.0, max_tokens=900, json_mode=True)
    parsed = parse_json_object(raw)
    critique = CritiqueResult.model_validate(parsed)

    # The application owns the stopping rule. The model can recommend, but code enforces.
    has_blocking_issue = any(issue.severity == "blocking" for issue in critique.issues)
    critique.passed = critique.score >= pass_score and not has_blocking_issue
    return critique


def refine_draft(
    brief: str,
    draft: str,
    critique: CritiqueResult,
    constitution: str,
    reflections: Iterable[str] | None = None,
) -> str:
    """Rewrite a draft using structured critique.

    Params:
        brief: Original task brief.
        draft: Current draft.
        critique: Structured critique object.
        constitution: Principles to preserve during rewrite.
        reflections: Prior reflection memory.
    Returns:
        Revised draft text.
    """
    critique_json = critique.model_dump_json(indent=2)
    messages = build_refiner_messages(
        brief=brief,
        draft=draft,
        critique_json=critique_json,
        constitution=constitution,
        reflections=reflections,
    )
    return call_chat_model(messages, temperature=0.3, max_tokens=800).strip()


def run_refinement_loop(
    brief: str,
    initial_draft: str | None,
    rubric: str,
    constitution: str,
    pass_score: int = 8,
    max_iterations: int = 3,
) -> tuple[str, list[IterationRecord]]:
    """Run a generate-critique-refine loop until the draft passes or retries end.

    Params:
        brief: Original writing brief.
        initial_draft: Optional starting draft; if None, one is generated.
        rubric: Evaluation rubric.
        constitution: Principles for evaluation and revision.
        pass_score: Minimum accepted score.
        max_iterations: Maximum critique attempts.
    Returns:
        Final draft and list of iteration records.
    """
    draft = initial_draft.strip() if initial_draft else generate_first_draft(brief)
    trace: list[IterationRecord] = []
    reflections: list[str] = []

    for iteration in range(1, max_iterations + 1):
        critique = critique_draft(
            brief=brief,
            draft=draft,
            rubric=rubric,
            constitution=constitution,
            reflections=reflections,
            pass_score=pass_score,
        )
        record = IterationRecord(iteration=iteration, draft=draft, critique=critique)
        trace.append(record)

        reflections.append(critique.reflection_memory)

        if critique.passed:
            break

        draft = refine_draft(
            brief=brief,
            draft=draft,
            critique=critique,
            constitution=constitution,
            reflections=reflections,
        )

    return draft, trace


def print_iteration_trace(trace: list[IterationRecord]) -> None:
    """Print a compact trace of scores and reflection memory.

    Params:
        trace: Iteration records from the loop.
    Returns:
        None.
    """
    for record in trace:
        print(f"Iteration {record.iteration}: score={record.score}/10 | passed={record.passed}")
        print(f"Summary: {record.critique.summary}")
        print(f"Reflection memory: {record.critique.reflection_memory}")
        if record.critique.issues:
            print("Top issues:")
            for issue in record.critique.issues:
                print(f"  - [{issue.severity}] {issue.criterion}: {issue.revision_instruction}")
        print("-" * 80)


def save_demo_outputs(final_draft: str, trace: list[IterationRecord], output_dir: str | Path = "demo_outputs") -> None:
    """Save final draft and trace for trainer review.

    Params:
        final_draft: Final generated draft.
        trace: Iteration records.
        output_dir: Directory to write outputs.
    Returns:
        None.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    (output_path / "final_draft.txt").write_text(final_draft, encoding="utf-8")
    trace_payload = [record.model_dump(mode="json") for record in trace]
    (output_path / "iteration_trace.json").write_text(json.dumps(trace_payload, indent=2), encoding="utf-8")
