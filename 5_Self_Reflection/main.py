"""Command-line runner for the writing critic practical."""

from __future__ import annotations

from critic_loop import (
    print_iteration_trace,
    read_text,
    run_refinement_loop,
    save_demo_outputs,
)


def main() -> None:
    """Run the full practical from sample files.

    Params:
        None.
    Returns:
        None.
    """
    brief = read_text("data/writing_brief.txt")
    weak_draft = read_text("data/weak_draft.txt")
    rubric = read_text("data/rubric.md")
    constitution = read_text("data/constitution.md")

    final_draft, trace = run_refinement_loop(
        brief=brief,
        initial_draft=weak_draft,
        rubric=rubric,
        constitution=constitution,
        pass_score=8,
        max_iterations=3,
    )

    print_iteration_trace(trace)
    print("\nFINAL DRAFT\n")
    print(final_draft)

    save_demo_outputs(final_draft, trace)


if __name__ == "__main__":
    main()
