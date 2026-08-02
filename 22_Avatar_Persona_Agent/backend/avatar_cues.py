"""Avatar cue generation for frontend animation."""

from backend.schemas import AvatarCue
from backend.utils import estimate_speech_duration_ms


def build_avatar_cues(text: str) -> list[AvatarCue]:
    """Build simple avatar animation cues from assistant text.

    Args:
        text: Assistant response text.

    Returns:
        Ordered avatar cues used by the frontend.
    """
    speech_duration = estimate_speech_duration_ms(text)
    return [
        AvatarCue(state="thinking", duration_ms=800, expression="focused", intensity=0.45),
        AvatarCue(state="speaking", duration_ms=speech_duration, expression="engaged", intensity=0.85),
        AvatarCue(state="idle", duration_ms=1200, expression="neutral", intensity=0.35),
    ]
