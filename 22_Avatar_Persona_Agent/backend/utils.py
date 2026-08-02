"""General helper functions for the avatar persona agent backend."""

import math
import wave
from pathlib import Path
from time import perf_counter
from typing import Callable, TypeVar
from uuid import uuid4


T = TypeVar("T")


def timed_ms(fn: Callable[[], T]) -> tuple[T, int]:
    """Run a synchronous function and measure elapsed time.

    Args:
        fn: Function with no arguments.

    Returns:
        Tuple of function result and elapsed milliseconds.
    """
    start = perf_counter()
    result = fn()
    elapsed_ms = int((perf_counter() - start) * 1000)
    return result, elapsed_ms


def safe_filename(suffix: str = ".wav") -> str:
    """Create a collision-resistant filename for generated audio.

    Args:
        suffix: File extension, including the dot.

    Returns:
        Random filename string.
    """
    clean_suffix = suffix if suffix.startswith(".") else f".{suffix}"
    return f"avatar_response_{uuid4().hex}{clean_suffix}"


def estimate_speech_duration_ms(text: str) -> int:
    """Estimate spoken duration from text length.

    Args:
        text: Assistant text.

    Returns:
        Approximate duration in milliseconds.
    """
    words = max(1, len(text.split()))
    words_per_minute = 145
    minutes = words / words_per_minute
    return int(max(1200, minutes * 60_000))


def create_mock_wav(output_path: Path, duration_seconds: float = 2.2) -> Path:
    """Create a small synthetic WAV file for no-key classroom demos.

    Args:
        output_path: Destination WAV path.
        duration_seconds: Duration of the generated tone.

    Returns:
        Path to the generated WAV file.
    """
    sample_rate = 16_000
    frequency = 440.0
    amplitude = 0.18
    total_samples = int(sample_rate * duration_seconds)

    with wave.open(str(output_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for index in range(total_samples):
            envelope = 0.5 + 0.5 * math.sin(2 * math.pi * index / sample_rate * 1.7)
            sample = int(32767 * amplitude * envelope * math.sin(2 * math.pi * frequency * index / sample_rate))
            wav_file.writeframes(sample.to_bytes(2, byteorder="little", signed=True))

    return output_path
