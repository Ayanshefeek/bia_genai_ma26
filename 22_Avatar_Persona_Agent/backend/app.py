"""FastAPI app for the 3-D Avatar & Persona Agent practical.

Run from the project root:

    uvicorn backend.app:app --reload --port 8000
"""

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.agent_service import generate_reply
from backend.audio_service import synthesize_speech, transcribe_upload
from backend.avatar_cues import build_avatar_cues
from backend.config import get_settings
from backend.persona import list_personas
from backend.schemas import ChatRequest, ChatResponse, PersonaSummary, TranscriptionResponse
from backend.utils import timed_ms


settings = get_settings()

app = FastAPI(
    title="Avatar Persona Agent",
    description="Backend for a browser-based voice and avatar persona agent practical.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, object]:
    """Return service health and current execution mode.

    Returns:
        Dictionary containing health status and mock mode.
    """
    return {
        "status": "ok",
        "mock_mode": settings.mock_mode,
        "audio_dir": str(settings.audio_output_dir),
    }


@app.get("/api/personas", response_model=list[PersonaSummary])
def personas() -> list[dict[str, object]]:
    """Return persona options available to the frontend.

    Returns:
        List of persona metadata dictionaries.
    """
    return list_personas()


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Generate a persona response and optional TTS audio.

    Args:
        request: User message and selected persona.

    Returns:
        ChatResponse with assistant text, audio URL, and animation cues.
    """
    try:
        def run_generation() -> tuple[str, str | None]:
            reply = generate_reply(request.message, request.persona_id, settings)
            audio_url = None
            if request.include_audio:
                _, audio_url = synthesize_speech(reply, settings)
            return reply, audio_url

        (assistant_text, audio_url), latency_ms = timed_ms(run_generation)
        return ChatResponse(
            user_text=request.message,
            assistant_text=assistant_text,
            persona_id=request.persona_id,
            audio_url=audio_url,
            avatar_cues=build_avatar_cues(assistant_text),
            latency_ms=latency_ms,
            cost_note=(
                "Mock mode: no API cost."
                if settings.mock_mode
                else "Approximate demo cost: usually a few cents for a short LLM + TTS turn."
            ),
            mock_mode=settings.mock_mode,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/transcribe", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile = File(...)) -> TranscriptionResponse:
    """Transcribe a browser-recorded audio clip.

    Args:
        file: Uploaded audio file.

    Returns:
        TranscriptionResponse containing recognized text.
    """
    try:
        text = await transcribe_upload(file, settings)
        return TranscriptionResponse(
            text=text,
            mock_mode=settings.mock_mode,
            cost_note=(
                "Mock mode: no API cost."
                if settings.mock_mode
                else "STT cost depends on audio length; keep clips short for classroom demos."
            ),
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/audio/{filename}")
def audio_file(filename: str) -> FileResponse:
    """Serve generated audio files to the browser.

    Args:
        filename: Generated file name.

    Returns:
        FileResponse containing WAV or MP3 audio.
    """
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    path = settings.audio_output_dir / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")

    media_type = "audio/mpeg" if Path(filename).suffix.lower() == ".mp3" else "audio/wav"
    return FileResponse(path, media_type=media_type)
