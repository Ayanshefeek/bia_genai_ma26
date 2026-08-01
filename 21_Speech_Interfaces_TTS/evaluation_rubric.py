"""TTS evaluation rubric helpers for the classroom lab."""

from __future__ import annotations

import csv
from pathlib import Path


RUBRIC_COLUMNS = [
    "provider",
    "file",
    "clarity_1_5",
    "naturalness_1_5",
    "latency_1_5",
    "pronunciation_1_5",
    "avatar_readiness_1_5",
    "notes",
]


def create_rubric_csv(path: str | Path) -> Path:
    """Create a blank TTS evaluation rubric CSV.

    Args:
        path: Destination CSV path.

    Returns:
        Path to the created CSV.
    """
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        RUBRIC_COLUMNS,
        ["openai", "outputs/openai_response.mp3", "", "", "", "", "", ""],
        ["elevenlabs", "outputs/elevenlabs_response.mp3", "", "", "", "", "", ""],
        ["piper", "outputs/piper_response.wav", "", "", "", "", "", ""],
    ]
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    return output


def explain_scoring() -> str:
    """Return a short explanation of the evaluation scoring scale.

    Returns:
        Human-readable scoring guide.
    """
    return (
        "Score each dimension from 1 to 5. "
        "1 means unacceptable for a user-facing assistant; 3 means usable for a prototype; "
        "5 means strong enough for a polished product demo."
    )
