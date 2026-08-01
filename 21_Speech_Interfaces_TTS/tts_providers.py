"""Text-to-speech provider implementations.

The same text can be sent to multiple providers so learners can compare
naturalness, speed, cost, privacy, and avatar-readiness.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from dotenv import load_dotenv

from audio_utils import create_tone_wav, ensure_parent_dir


load_dotenv()


@dataclass
class TTSResult:
    """Normalized result returned by every TTS provider."""

    output_path: Path
    provider: str
    model: str
    voice: str
    latency_ms: float | None = None


class TTSProvider(Protocol):
    """Protocol for text-to-speech providers."""

    provider_name: str

    def synthesize(self, text: str, output_path: str | Path) -> TTSResult:
        """Convert text into an audio file.

        Args:
            text: Text to speak.
            output_path: Destination audio file.

        Returns:
            Normalized TTSResult.
        """
        ...


class MockTTSProvider:
    """Offline TTS provider that writes a simple WAV tone."""

    provider_name = "mock-tts"

    def synthesize(self, text: str, output_path: str | Path) -> TTSResult:
        """Write a tone WAV file.

        Args:
            text: Text is ignored by the mock provider.
            output_path: Destination WAV path.

        Returns:
            Normalized TTSResult.
        """
        output = create_tone_wav(output_path)
        return TTSResult(output_path=output, provider=self.provider_name, model="tone-generator", voice="beep")


class OpenAITTSProvider:
    """Cloud TTS provider using OpenAI speech synthesis."""

    provider_name = "openai-tts"

    def __init__(
        self,
        model: str | None = None,
        voice: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize OpenAI TTS.

        Args:
            model: TTS model name.
            voice: Built-in voice name.
            api_key: Optional API key. Defaults to OPENAI_API_KEY.
        """
        self.model = model or os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
        self.voice = voice or os.getenv("OPENAI_TTS_VOICE", "marin")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def synthesize(self, text: str, output_path: str | Path) -> TTSResult:
        """Synthesize speech using OpenAI TTS.

        Args:
            text: Text to speak.
            output_path: Destination file, usually .mp3.

        Returns:
            Normalized TTSResult.

        Raises:
            RuntimeError: If OPENAI_API_KEY is missing or synthesis fails.
        """
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Copy .env.sample to .env and add your key, "
                "or use MockTTSProvider for offline teaching."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install openai from requirements.txt to use OpenAI TTS.") from exc

        output = ensure_parent_dir(output_path)
        client = OpenAI(api_key=self.api_key)

        # COST NOTE: Keep classroom TTS examples short. A few sentences should be low cost.
        response = client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
        )

        # The SDK exposes write_to_file in recent versions.
        if hasattr(response, "write_to_file"):
            response.write_to_file(output)
        else:
            output.write_bytes(response.content)

        return TTSResult(output_path=output, provider=self.provider_name, model=self.model, voice=self.voice)


class ElevenLabsTTSProvider:
    """Cloud expressive TTS provider using ElevenLabs."""

    provider_name = "elevenlabs-tts"

    def __init__(
        self,
        voice_id: str | None = None,
        model_id: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize ElevenLabs TTS.

        Args:
            voice_id: ElevenLabs voice ID.
            model_id: ElevenLabs model ID.
            api_key: Optional API key. Defaults to ELEVENLABS_API_KEY.
        """
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID")
        self.model_id = model_id or os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")

    def synthesize(self, text: str, output_path: str | Path) -> TTSResult:
        """Synthesize speech using ElevenLabs.

        Args:
            text: Text to speak.
            output_path: Destination MP3 path.

        Returns:
            Normalized TTSResult.

        Raises:
            RuntimeError: If credentials or voice ID are missing.
        """
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is missing. Add it to .env or skip this provider.")
        if not self.voice_id:
            raise RuntimeError("ELEVENLABS_VOICE_ID is missing. Pick a voice in the ElevenLabs dashboard.")

        try:
            from elevenlabs.client import ElevenLabs
        except ImportError as exc:
            raise RuntimeError("Install elevenlabs from requirements.txt to use ElevenLabs TTS.") from exc

        output = ensure_parent_dir(output_path)
        client = ElevenLabs(api_key=self.api_key)

        # COST NOTE: Use short prompts for class comparisons; expressive TTS can cost more than basic TTS.
        audio_stream = client.text_to_speech.convert(
            voice_id=self.voice_id,
            model_id=self.model_id,
            text=text,
            output_format="mp3_44100_128",
        )

        with output.open("wb") as file:
            for chunk in audio_stream:
                if chunk:
                    file.write(chunk)

        return TTSResult(output_path=output, provider=self.provider_name, model=self.model_id, voice=self.voice_id)


class PiperTTSProvider:
    """Optional local TTS provider using Piper."""

    provider_name = "piper-tts"

    def __init__(
        self,
        model_path: str | None = None,
        config_path: str | None = None,
    ) -> None:
        """Initialize Piper TTS.

        Args:
            model_path: Path to the .onnx voice model.
            config_path: Path to the matching .onnx.json config.
        """
        self.model_path = model_path or os.getenv("PIPER_MODEL_PATH")
        self.config_path = config_path or os.getenv("PIPER_CONFIG_PATH")

    def synthesize(self, text: str, output_path: str | Path) -> TTSResult:
        """Synthesize speech locally with Piper.

        Args:
            text: Text to speak.
            output_path: Destination WAV path.

        Returns:
            Normalized TTSResult.

        Raises:
            RuntimeError: If Piper or voice model files are missing.
        """
        if not self.model_path:
            raise RuntimeError("PIPER_MODEL_PATH is missing. Download a Piper voice model and set the path in .env.")

        model_path = Path(self.model_path)
        if not model_path.exists():
            raise RuntimeError(f"Piper model file not found: {model_path}")

        try:
            from piper.voice import PiperVoice
        except ImportError as exc:
            raise RuntimeError(
                "Piper is optional. Install requirements_piper_optional.txt and download a voice model."
            ) from exc

        output = ensure_parent_dir(output_path)
        voice = PiperVoice.load(str(model_path), config_path=self.config_path)

        import wave

        with wave.open(str(output), "wb") as wav_file:
            voice.synthesize(text, wav_file)

        return TTSResult(output_path=output, provider=self.provider_name, model=str(model_path), voice=model_path.stem)


def get_tts_provider(name: str) -> TTSProvider:
    """Factory for TTS providers.

    Args:
        name: Provider name: mock, openai, elevenlabs, or piper.

    Returns:
        TTS provider instance.

    Raises:
        ValueError: If provider name is unknown.
    """
    normalized = name.strip().lower()
    if normalized == "mock":
        return MockTTSProvider()
    if normalized == "openai":
        return OpenAITTSProvider()
    if normalized == "elevenlabs":
        return ElevenLabsTTSProvider()
    if normalized == "piper":
        return PiperTTSProvider()
    raise ValueError(f"Unknown TTS provider: {name}")
