"""Speech-to-text and text-to-speech services for the avatar persona agent."""

from pathlib import Path
import tempfile

from fastapi import UploadFile
from openai import OpenAI

from backend.config import Settings
from backend.utils import create_mock_wav, estimate_speech_duration_ms, safe_filename


def synthesize_speech(text: str, settings: Settings) -> tuple[Path, str]:
    """Convert assistant text into an audio file.

    Args:
        text: Text to speak.
        settings: Application settings.

    Returns:
        Tuple of generated file path and public URL path.

    Raises:
        RuntimeError: If the OpenAI TTS call fails.
    """
    if settings.mock_mode:
        filename = safe_filename(".wav")
        output_path = settings.audio_output_dir / filename
        duration = min(4.0, max(1.6, estimate_speech_duration_ms(text) / 1000))
        create_mock_wav(output_path, duration_seconds=duration)
        return output_path, f"/api/audio/{filename}"

    filename = safe_filename(".mp3")
    output_path = settings.audio_output_dir / filename
    client = OpenAI(api_key=settings.openai_api_key)

    # COST NOTE: TTS cost depends on the model and character count; this demo keeps replies short.
    try:
        with client.audio.speech.with_streaming_response.create(
            model=settings.openai_tts_model,
            voice=settings.openai_tts_voice,
            input=text,
            response_format="mp3",
        ) as response:
            response.stream_to_file(output_path)
    except Exception as exc:  # noqa: BLE001 - convert SDK errors into classroom-friendly errors
        raise RuntimeError(f"OpenAI TTS failed: {exc}") from exc

    return output_path, f"/api/audio/{filename}"


async def transcribe_upload(file: UploadFile, settings: Settings) -> str:
    """Transcribe an uploaded browser audio recording.

    Args:
        file: Uploaded audio file from the frontend.
        settings: Application settings.

    Returns:
        Transcribed text, or a mock text in mock mode.

    Raises:
        RuntimeError: If transcription fails.
    """
    if settings.mock_mode:
        return "Mock transcription: explain how this avatar agent works."

    suffix = Path(file.filename or "audio.webm").suffix or ".webm"
    audio_bytes = await file.read()
    if not audio_bytes:
        raise RuntimeError("Uploaded audio file is empty.")

    client = OpenAI(api_key=settings.openai_api_key)

    # COST NOTE: Classroom clips should stay under 10 seconds to keep STT cost low.
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file.flush()

            with open(temp_file.name, "rb") as audio_handle:
                transcript = client.audio.transcriptions.create(
                    model=settings.openai_stt_model,
                    file=audio_handle,
                )
    except Exception as exc:  # noqa: BLE001 - convert SDK errors into classroom-friendly errors
        raise RuntimeError(f"OpenAI transcription failed: {exc}") from exc

    text = getattr(transcript, "text", "")
    if not text:
        raise RuntimeError("Transcription returned empty text.")
    return text.strip()
