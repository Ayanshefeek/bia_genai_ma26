"""Audio utilities for the Speech Interfaces & TTS practical.

These helpers keep the practical portable: the notebook can run with a sample file,
while trainers can optionally record microphone input during the live session.
"""

from __future__ import annotations

import math
import os
import struct
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar

import numpy as np


T = TypeVar("T")


@dataclass
class TimedResult:
    """Result wrapper that includes elapsed time in milliseconds."""

    value: object
    elapsed_ms: float


def ensure_parent_dir(path: str | Path) -> Path:
    """Create the parent directory for a file path if it does not exist.

    Args:
        path: File path whose parent should exist.

    Returns:
        The resolved Path object.
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def measure_call(func: Callable[..., T], *args, **kwargs) -> TimedResult:
    """Run a function and return its result with elapsed time.

    Args:
        func: Function to execute.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        TimedResult containing the original return value and elapsed milliseconds.
    """
    start = time.perf_counter()
    value = func(*args, **kwargs)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return TimedResult(value=value, elapsed_ms=elapsed_ms)


def audio_duration_seconds(path: str | Path) -> float:
    """Return the duration of a WAV file in seconds.

    Args:
        path: Path to a WAV file.

    Returns:
        Duration in seconds.

    Raises:
        ValueError: If the file is not a WAV file that Python can inspect.
    """
    with wave.open(str(path), "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        return frames / float(rate)


def create_tone_wav(
    output_path: str | Path,
    duration_seconds: float = 1.2,
    frequency_hz: float = 440.0,
    sample_rate: int = 16000,
) -> Path:
    """Create a simple tone WAV file.

    This is used by mock providers so the package can run end-to-end without
    API keys or a microphone. It is not meant to be transcribed by real STT.

    Args:
        output_path: Destination WAV path.
        duration_seconds: Tone duration.
        frequency_hz: Tone frequency.
        sample_rate: Sample rate.

    Returns:
        Path to the generated WAV file.
    """
    output = ensure_parent_dir(output_path)
    amplitude = 12000
    with wave.open(str(output), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(int(duration_seconds * sample_rate)):
            sample = int(amplitude * math.sin(2 * math.pi * frequency_hz * i / sample_rate))
            wav_file.writeframes(struct.pack("<h", sample))
    return output


def create_mock_speech_wav(output_path: str | Path, text: str | None = None) -> Path:
    """Create a sample WAV file for the practical.

    If the host has the `espeak` command installed, this creates a spoken WAV.
    Otherwise it creates a tone so the demo can still run.

    Args:
        output_path: Destination WAV path.
        text: Sentence to synthesize when eSpeak is available.

    Returns:
        Path to the sample audio.
    """
    output = ensure_parent_dir(output_path)
    sentence = text or "Can you explain in simple words how text to speech works for an AI assistant?"

    # Use eSpeak only when available. This keeps the repository lightweight.
    import shutil
    import subprocess

    if shutil.which("espeak"):
        subprocess.run(["espeak", "-w", str(output), sentence], check=True)
        return output

    return create_tone_wav(output)


def record_microphone_wav(
    output_path: str | Path,
    duration_seconds: float = 5.0,
    sample_rate: int = 16000,
) -> Path:
    """Record microphone audio into a WAV file.

    Args:
        output_path: Destination WAV path.
        duration_seconds: Number of seconds to record.
        sample_rate: Audio sample rate.

    Returns:
        Path to recorded audio.

    Raises:
        RuntimeError: If sounddevice or soundfile is not available, or no input device works.
    """
    output = ensure_parent_dir(output_path)

    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "Microphone recording requires sounddevice and soundfile. "
            "Install requirements.txt and check OS microphone permissions."
        ) from exc

    print(f"Recording for {duration_seconds:.1f} seconds. Speak now...")
    audio = sd.rec(int(duration_seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()
    sf.write(str(output), audio, sample_rate)
    print(f"Saved recording to {output}")
    return output


def play_audio_file(path: str | Path) -> None:
    """Play an audio file when sounddevice/soundfile are available.

    Args:
        path: Path to a WAV/MP3 file. WAV is most reliable with this helper.

    Raises:
        RuntimeError: If playback dependencies or output device are unavailable.
    """
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "Local playback requires sounddevice and soundfile. "
            "In notebooks, use IPython.display.Audio instead."
        ) from exc

    data, sample_rate = sf.read(str(path), dtype="float32")
    sd.play(data, sample_rate)
    sd.wait()
