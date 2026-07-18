"""Run the complete webhook demo sequence against a running local server."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_script(script_name: str) -> None:
    """Run one simulation script and stream its output.

    Args:
        script_name: Filename inside the scripts directory.
    """
    print("\n" + "=" * 80)
    print(f"Running {script_name}")
    print("=" * 80)
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / script_name)],
        cwd=PROJECT_ROOT,
        check=True,
    )


if __name__ == "__main__":
    print("Make sure the API server is running first:")
    print("python -m uvicorn app.main:app --reload --port 8000")
    run_script("simulate_form_event.py")
    run_script("simulate_github_issue_event.py")
