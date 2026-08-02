"""Reusable voice-agent pipeline for the practical.

Pipeline:
audio file -> STT provider -> LLM response -> TTS provider -> audio output
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from audio_utils import measure_call
from stt_providers import STTProvider, STTResult
from tts_providers import TTSProvider, TTSResult


load_dotenv()


@dataclass
class VoiceTurn:
    """A completed voice interaction turn."""

    transcript: STTResult
    response_text: str
    audio: TTSResult
    total_latency_ms: float


class VoiceAgent:
    """Small reusable voice agent that composes STT, LLM, and TTS providers."""

    def __init__(
        self,
        stt_provider: STTProvider,
        tts_provider: TTSProvider,
        model_name: str | None = None,
        system_prompt: str | None = None,
    ) -> None:
        """Create a voice agent.

        Args:
            stt_provider: Speech-to-text provider.
            tts_provider: Text-to-speech provider.
            model_name: Text LLM model name.
            system_prompt: Instruction for the LLM.
        """
        self.stt_provider = stt_provider
        self.tts_provider = tts_provider
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.system_prompt = system_prompt or (
            "You are a helpful AI voice assistant for a live classroom demo. "
            "Answer in two short spoken sentences. Avoid markdown, lists, URLs, and long clauses."
        )

    def generate_response(self, transcript: str, use_mock_llm: bool = False) -> str:
        """Generate a speech-friendly answer.

        Args:
            transcript: User's transcribed speech.
            use_mock_llm: If True, return a deterministic response without API calls.

        Returns:
            Speech-friendly answer text.

        Raises:
            RuntimeError: If OPENAI_API_KEY is missing and mock mode is disabled.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if use_mock_llm or not api_key:
            return (
                "Text to speech turns written words into audio. "
                "For a voice agent, it is the final step that makes the assistant feel present."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install openai from requirements.txt to generate LLM responses.") from exc

        client = OpenAI(api_key=api_key)

        # COST NOTE: This is a short text response using gpt-4o-mini by default.
        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": transcript},
            ],
            temperature=0.4,
        )
        answer = completion.choices[0].message.content or ""
        return self.make_speech_safe(answer)

    @staticmethod
    def make_speech_safe(text: str) -> str:
        """Clean LLM text so it sounds better when spoken.

        Args:
            text: Raw LLM output.

        Returns:
            Speech-safe text with markdown markers removed and length controlled.
        """
        cleaned = text.replace("**", "").replace("*", "").replace("#", "")
        cleaned = cleaned.replace("- ", "")
        cleaned = " ".join(cleaned.split())
        if len(cleaned) > 450:
            cleaned = cleaned[:447].rsplit(" ", 1)[0] + "..."
        return cleaned

    def run_turn(
        self,
        input_audio_path: str | Path,
        output_audio_path: str | Path,
        use_mock_llm: bool = False,
    ) -> VoiceTurn:
        """Run one full spoken interaction.

        Args:
            input_audio_path: User audio file.
            output_audio_path: Destination for assistant audio.
            use_mock_llm: Whether to use deterministic mock response.

        Returns:
            VoiceTurn with transcript, response text, generated audio, and total latency.
        """
        total_start = measure_call(lambda: None).elapsed_ms  # establishes the type; not used
        import time

        start = time.perf_counter()

        stt_timed = measure_call(self.stt_provider.transcribe, input_audio_path)
        stt_result = stt_timed.value
        if hasattr(stt_result, "latency_ms"):
            stt_result.latency_ms = stt_timed.elapsed_ms

        response_text = self.generate_response(stt_result.text, use_mock_llm=use_mock_llm)

        tts_timed = measure_call(self.tts_provider.synthesize, response_text, output_audio_path)
        tts_result = tts_timed.value
        if hasattr(tts_result, "latency_ms"):
            tts_result.latency_ms = tts_timed.elapsed_ms

        total_latency_ms = (time.perf_counter() - start) * 1000
        return VoiceTurn(
            transcript=stt_result,
            response_text=response_text,
            audio=tts_result,
            total_latency_ms=total_latency_ms,
        )
