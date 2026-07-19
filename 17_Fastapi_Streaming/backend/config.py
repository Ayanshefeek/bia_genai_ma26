"""Application configuration loaded from environment variables.

The classroom default runs in mock LLM mode, so the full demo works even if
an API key is not configured yet. To use OpenAI streaming, set
APP_USE_MOCK_LLM=false and provide OPENAI_API_KEY in .env.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the backend application."""

    app_name: str = os.getenv("APP_NAME", "Streaming Productivity Assistant")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    use_mock_llm: bool = os.getenv("APP_USE_MOCK_LLM", "true").lower() in {
        "1",
        "true",
        "yes",
        "y",
    }
    database_path: Path = Path(
        os.getenv("DATABASE_PATH", "data/productivity_assistant.sqlite3")
    )
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    token_delay_seconds: float = float(os.getenv("MOCK_TOKEN_DELAY_SECONDS", "0.035"))


def get_settings() -> Settings:
    """Return application settings.

    Returns:
        Settings: Immutable settings object populated from environment variables.
    """

    settings = Settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
