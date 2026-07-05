"""LLM wrapper for structured JSON generation.

The wrapper supports two teaching modes:
1. Real OpenAI calls when OPENAI_API_KEY is present and USE_MOCK_LLM=false.
2. Deterministic mock mode for no-cost classroom walkthroughs.
"""

from __future__ import annotations

import json
import os
from typing import Callable, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class MissingAPIKeyError(RuntimeError):
    """Raised when a real LLM call is requested without an API key."""


class StructuredLLMClient:
    """Small wrapper around the OpenAI SDK for Pydantic-validated JSON outputs."""

    def __init__(self, model_name: str | None = None, use_mock: bool | None = None) -> None:
        """Initialize the client.

        Args:
            model_name: Optional model override. Defaults to OPENAI_MODEL or gpt-4o-mini.
            use_mock: Optional mock-mode override. Defaults to USE_MOCK_LLM env setting.
        """

        load_dotenv()
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        env_mock = os.getenv("USE_MOCK_LLM", "false").strip().lower() in {"1", "true", "yes"}
        self.use_mock = env_mock if use_mock is None else use_mock
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None

        if not self.use_mock:
            if not self.api_key:
                raise MissingAPIKeyError(
                    "OPENAI_API_KEY is missing. Add it to .env or set USE_MOCK_LLM=true "
                    "for the no-cost classroom walkthrough."
                )
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
        fallback_factory: Callable[[], T],
        temperature: float = 0.2,
    ) -> T:
        """Generate JSON and validate it against a Pydantic schema.

        Args:
            system_prompt: Role and behavior instruction.
            user_prompt: Task-specific prompt.
            response_schema: Pydantic model class expected from the LLM.
            fallback_factory: Deterministic output used in mock mode.
            temperature: Sampling temperature for the model.

        Returns:
            A validated Pydantic model instance.
        """

        if self.use_mock:
            return fallback_factory()

        assert self.client is not None

        # COST NOTE: gpt-4o-mini text-only calls for this project are typically
        # well below $0.50 for a full demo run with the bundled source pack.
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw_content = response.choices[0].message.content or "{}"

        try:
            return response_schema.model_validate_json(raw_content)
        except ValidationError as original_error:
            repaired = self._repair_json(
                raw_content=raw_content,
                response_schema=response_schema,
                original_error=str(original_error),
            )
            return repaired

    def _repair_json(
        self,
        raw_content: str,
        response_schema: type[T],
        original_error: str,
    ) -> T:
        """Ask the model to repair malformed JSON once.

        Args:
            raw_content: Invalid JSON returned by the first model call.
            response_schema: Target Pydantic model class.
            original_error: Validation error message.

        Returns:
            Validated schema instance.
        """

        if self.use_mock:
            raise RuntimeError("JSON repair should not be called in mock mode.")

        assert self.client is not None
        repair_prompt = (
            "The previous output failed validation. Repair it to match the schema. "
            "Return only JSON.\n\n"
            f"Validation error:\n{original_error}\n\n"
            f"Target schema:\n{json.dumps(response_schema.model_json_schema(), indent=2)}\n\n"
            f"Invalid output:\n{raw_content}"
        )

        # COST NOTE: Repair is a second LLM call. It should be rare; validation
        # reduces downstream debugging time when a malformed handoff appears.
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You repair JSON to match schemas."},
                {"role": "user", "content": repair_prompt},
            ],
        )
        repaired_content = response.choices[0].message.content or "{}"
        return response_schema.model_validate_json(repaired_content)
