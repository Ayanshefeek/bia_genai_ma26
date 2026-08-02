"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    """Configuration values shared across backend modules."""

    openai_api_key: str | None
    openai_model: str
    openai_tts_model: str
    openai_tts_voice: str
    openai_stt_model: str
    mock_mode: bool
    cors_origins: list[str]
    audio_output_dir: Path

    @property
    def use_real_openai(self) -> bool:
        """Return True when real OpenAI API calls should be made."""
        return bool(self.openai_api_key) and not self.mock_mode


def parse_bool(value: str | None, default: bool = False) -> bool:
    """Parse common string booleans from environment variables.

    Args:
        value: Raw environment variable value.
        default: Value returned when the variable is missing.

    Returns:
        Parsed boolean value.
    """
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def get_settings() -> Settings:
    """Load application settings from the environment.

    Returns:
        Settings object with typed configuration.
    """
    audio_dir = PROJECT_ROOT / "backend" / "generated_audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    cors_origins = [origin.strip() for origin in origins.split(",") if origin.strip()]

    api_key = os.getenv("OPENAI_API_KEY")
    explicit_mock = parse_bool(os.getenv("MOCK_MODE"), default=False)

    return Settings(
        openai_api_key=api_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_tts_model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
        openai_tts_voice=os.getenv("OPENAI_TTS_VOICE", "alloy"),
        openai_stt_model=os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe"),
        mock_mode=explicit_mock or not bool(api_key),
        cors_origins=cors_origins,
        audio_output_dir=audio_dir,
    )
