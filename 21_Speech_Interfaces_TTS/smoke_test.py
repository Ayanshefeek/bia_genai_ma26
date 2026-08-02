"""Offline smoke test for the practical package.

Run:
    python smoke_test.py

This does not call paid APIs. It verifies that the provider abstraction and
end-to-end pipeline work with mock providers.
"""

from pathlib import Path

from audio_utils import create_mock_speech_wav
from stt_providers import MockSTTProvider
from tts_providers import MockTTSProvider
from voice_agent import VoiceAgent


def main() -> None:
    """Run offline smoke test."""
    input_audio = create_mock_speech_wav(Path("data/sample_voice_question.wav"))
    agent = VoiceAgent(MockSTTProvider(), MockTTSProvider())
    turn = agent.run_turn(input_audio, "outputs/smoke_test_response.wav", use_mock_llm=True)
    assert turn.transcript.text
    assert Path(turn.audio.output_path).exists()
    print("Smoke test passed.")
    print(f"Transcript: {turn.transcript.text}")
    print(f"Output audio: {turn.audio.output_path}")


if __name__ == "__main__":
    main()
