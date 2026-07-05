"""CLI entry point for the Team Research Bot practical."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from llm import MissingAPIKeyError, StructuredLLMClient
from orchestrator import ResearchBotOrchestrator
from source_loader import load_source_pack


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Run the Team Research Bot pipeline.")
    parser.add_argument(
        "--query",
        default="What should an organization consider before using AI agents in customer support?",
        help="Research question to send to the agent team.",
    )
    parser.add_argument(
        "--source-dir",
        default="data/source_pack",
        help="Directory containing markdown source documents.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run without OpenAI calls using deterministic mock outputs.",
    )
    parser.add_argument(
        "--max-revisions",
        type=int,
        default=1,
        help="Maximum Writer revision loops after fact-checking.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the full command-line demo."""

    load_dotenv()
    args = parse_args()

    if args.mock:
        os.environ["USE_MOCK_LLM"] = "true"

    try:
        llm_client = StructuredLLMClient()
    except MissingAPIKeyError as exc:
        print(f"\nFriendly setup message:\n{exc}\n")
        print("Tip: rerun with --mock for the no-cost classroom walkthrough.")
        return

    documents = load_source_pack(args.source_dir)
    orchestrator = ResearchBotOrchestrator(
        llm_client=llm_client,
        documents=documents,
        trace_dir=Path("traces"),
        max_revisions=args.max_revisions,
    )

    state = orchestrator.run(args.query)

    print(f"\nRun ID: {state.run_id}")
    print(f"Status: {state.status}")
    print(f"Messages passed: {len(state.messages)}")
    print(f"Trace saved to: traces/{state.run_id}.json\n")

    if state.final_report:
        print("=" * 80)
        print(state.final_report.title)
        print("=" * 80)
        print(state.final_report.final_answer)
        print("\nKey takeaways:")
        for takeaway in state.final_report.key_takeaways:
            print(f"- {takeaway}")
        print("\nReferences:", ", ".join(state.final_report.references))
    else:
        print("No final report produced. Errors:")
        for error in state.errors:
            print(f"- {error}")


if __name__ == "__main__":
    main()
