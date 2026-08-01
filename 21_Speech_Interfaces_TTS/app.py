"""Command-line demo for the Speech Interfaces & TTS practical.

Examples:
    python app.py --stt mock --tts mock
    python app.py --stt openai --tts openai --input data/sample_voice_question.wav
    python app.py --stt openai --tts elevenlabs
"""

from __future__ import annotations

import argparse
from pathlib import Path

from audio_utils import create_mock_speech_wav
from stt_providers import get_stt_provider
from tts_providers import get_tts_provider
from voice_agent import VoiceAgent


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed argparse namespace.
    """
    parser = argparse.ArgumentParser(description="Run one voice-agent turn.")
    parser.add_argument("--stt", default="mock", choices=["mock", "openai", "local-whisper"], help="STT provider")
    parser.add_argument("--tts", default="mock", choices=["mock", "openai", "elevenlabs", "piper"], help="TTS provider")
    parser.add_argument("--input", default="data/sample_voice_question.wav", help="Input audio file")
    parser.add_argument("--output", default=None, help="Output audio path")
    parser.add_argument("--mock-llm", action="store_true", help="Use deterministic response instead of OpenAI LLM")
    return parser.parse_args()


def main() -> None:
    """Run the CLI demo."""
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        create_mock_speech_wav(input_path)

    output_suffix = "wav" if args.tts in {"mock", "piper"} else "mp3"
    output_path = Path(args.output or f"outputs/{args.tts}_assistant_response.{output_suffix}")

    stt_provider = get_stt_provider(args.stt)
    tts_provider = get_tts_provider(args.tts)

    agent = VoiceAgent(stt_provider=stt_provider, tts_provider=tts_provider)
    turn = agent.run_turn(
        input_audio_path=input_path,
        output_audio_path=output_path,
        use_mock_llm=args.mock_llm or args.stt == "mock" or args.tts == "mock",
    )

    print("\n--- Voice Agent Turn ---")
    print(f"Transcript ({turn.transcript.provider}/{turn.transcript.model}): {turn.transcript.text}")
    print(f"Response: {turn.response_text}")
    print(f"Audio ({turn.audio.provider}/{turn.audio.model}): {turn.audio.output_path}")
    print(f"STT latency: {turn.transcript.latency_ms:.0f} ms")
    print(f"TTS latency: {turn.audio.latency_ms:.0f} ms")
    print(f"Total latency: {turn.total_latency_ms:.0f} ms")


if __name__ == "__main__":
    main()
