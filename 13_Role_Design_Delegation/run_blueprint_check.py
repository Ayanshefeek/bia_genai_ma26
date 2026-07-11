"""CLI utility to validate a role-design blueprint.

Usage:
    python run_blueprint_check.py data/sample_research_bot_blueprint.json
    python run_blueprint_check.py data/flawed_research_bot_blueprint.json --save outputs/report.txt
"""

from __future__ import annotations

import argparse
from pathlib import Path

from validators import load_blueprint, render_report, save_report, validate_blueprint


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Validate a multi-agent role-design blueprint.")
    parser.add_argument("blueprint", help="Path to a blueprint JSON file.")
    parser.add_argument("--save", help="Optional path to save the text report.")
    return parser.parse_args()


def main() -> None:
    """Run the blueprint validator and print a report."""
    args = parse_args()
    blueprint = load_blueprint(args.blueprint)
    findings = validate_blueprint(blueprint)
    report = render_report(findings)
    print(report)

    if args.save:
        save_report(report, args.save)
        print(f"\nSaved report to: {Path(args.save).resolve()}")


if __name__ == "__main__":
    main()
