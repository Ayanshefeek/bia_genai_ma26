"""Application configuration loaded from environment variables.

All secrets and model settings are read from `.env` so trainers can run the same
code in mock mode, OpenAI mode, or with a different model name.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    """Return a boolean from an environment variable.

    Args:
        name: Environment variable name.
        default: Value used when the variable is not set.

    Returns:
        Boolean value parsed from yes/no style strings.
    """
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the FastAPI webhook demo."""

    openai_api_key: str | None
    openai_model: str
    use_mock_llm: bool
    webhook_secret: str
    accept_unsigned_events: bool
    app_name: str
    app_version: str


def get_settings() -> Settings:
    """Load settings from environment variables.

    Returns:
        Settings object with API, model, and webhook configuration.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    return Settings(
        openai_api_key=api_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        # Default to mock mode when no API key exists so the demo still runs.
        use_mock_llm=_env_bool("USE_MOCK_LLM", default=api_key is None),
        webhook_secret=os.getenv("WEBHOOK_SECRET", "bia-demo-secret"),
        accept_unsigned_events=_env_bool("ACCEPT_UNSIGNED_EVENTS", default=True),
        app_name="BIA Webhook Trigger Agent",
        app_version="1.0.0",
    )
