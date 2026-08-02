"""Speech-to-text provider implementations.

The key teaching idea: every provider exposes the same simple contract,
so the rest of the voice agent does not care whether transcription is cloud,
local, or mocked for classroom setup.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from dotenv import load_dotenv


load_dotenv()


@dataclass
class STTResult:
    """Normalized transcription result returned by every STT provider."""

    text: str
    provider: str
    model: str
    latency_ms: float | None = None


class STTProvider(Protocol):
    """Protocol for speech-to-text providers."""

    provider_name: str

    def transcribe(self, audio_path: str | Path) -> STTResult:
        """Transcribe an audio file into text.

        Args:
            audio_path: Path to an audio file.

        Returns:
            Normalized STTResult.
        """
        ...


class MockSTTProvider:
    """Offline STT provider for demos without API keys."""

    provider_name = "mock-stt"

    def __init__(self, transcript: str | None = None) -> None:
        """Initialize the mock provider.

        Args:
            transcript: Fixed transcript to return.
        """
        self.transcript = transcript or os.getenv(
            "MOCK_TRANSCRIPT",
            "Can you explain in simple words how text to speech works for an AI assistant?",
        )

    def transcribe(self, audio_path: str | Path) -> STTResult:
        """Return a fixed transcript for a file.

        Args:
            audio_path: Path to an audio file. The mock provider does not inspect it.

        Returns:
            Normalized STTResult.
        """
        return STTResult(text=self.transcript, provider=self.provider_name, model="fixed-transcript")


class OpenAITranscriptionProvider:
    """Cloud STT provider using the OpenAI Audio Transcriptions API."""

    provider_name = "openai-stt"

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        """Initialize OpenAI transcription.

        Args:
            model: OpenAI transcription model name.
            api_key: Optional API key. Defaults to OPENAI_API_KEY.
        """
        self.model = model or os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def transcribe(self, audio_path: str | Path) -> STTResult:
        """Transcribe an audio file using OpenAI.

        Args:
            audio_path: Path to WAV/MP3/M4A audio.

        Returns:
            Normalized STTResult.

        Raises:
            RuntimeError: If OPENAI_API_KEY is missing or the SDK call fails.
        """
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Copy .env.sample to .env and add your key, "
                "or use MockSTTProvider for offline teaching."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install openai from requirements.txt to use OpenAI STT.") from exc

        client = OpenAI(api_key=self.api_key)
        path = Path(audio_path)
        if not path.exists():
            raise RuntimeError(f"Audio file not found: {path}")

        with path.open("rb") as audio_file:
            # COST NOTE: A short classroom clip should cost a small fraction of a cent.
            response = client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
            )

        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("OpenAI STT returned no transcript text.")
        return STTResult(text=text.strip(), provider=self.provider_name, model=self.model)


class LocalWhisperProvider:
    """Optional local Whisper STT provider.

    This is intentionally optional because local Whisper can be slow and may
    require ffmpeg/PyTorch setup that is not reliable on every learner laptop.
    """

    provider_name = "local-whisper"

    def __init__(self, model_name: str | None = None) -> None:
        """Initialize local Whisper.

        Args:
            model_name: Whisper model name such as tiny, base, small, medium, or turbo.
        """
        self.model_name = model_name or os.getenv("LOCAL_WHISPER_MODEL", "base")

    def transcribe(self, audio_path: str | Path) -> STTResult:
        """Transcribe audio locally with openai-whisper.

        Args:
            audio_path: Path to audio file.

        Returns:
            Normalized STTResult.

        Raises:
            RuntimeError: If optional local Whisper dependencies are missing.
        """
        try:
            import whisper
        except ImportError as exc:
            raise RuntimeError(
                "Local Whisper is optional. Install requirements_local_whisper_optional.txt "
                "and ensure ffmpeg is available, or use OpenAITranscriptionProvider."
            ) from exc

        model = whisper.load_model(self.model_name)
        result = model.transcribe(str(audio_path))
        text = str(result.get("text", "")).strip()
        if not text:
            raise RuntimeError("Local Whisper returned no transcript text.")
        return STTResult(text=text, provider=self.provider_name, model=self.model_name)


def get_stt_provider(name: str) -> STTProvider:
    """Factory for STT providers.

    Args:
        name: Provider name: mock, openai, or local-whisper.

    Returns:
        STT provider instance.

    Raises:
        ValueError: If the name is unknown.
    """
    normalized = name.strip().lower()
    if normalized == "mock":
        return MockSTTProvider()
    if normalized == "openai":
        return OpenAITranscriptionProvider()
    if normalized in {"local-whisper", "whisper-local", "whisper"}:
        return LocalWhisperProvider()
    raise ValueError(f"Unknown STT provider: {name}")
