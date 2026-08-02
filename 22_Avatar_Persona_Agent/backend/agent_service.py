"""LLM service for the avatar persona agent."""

from openai import OpenAI

from backend.config import Settings
from backend.persona import build_instructions, get_persona


def generate_mock_reply(message: str, persona_id: str) -> str:
    """Generate a deterministic response when no API key is available.

    Args:
        message: User message.
        persona_id: Selected persona identifier.

    Returns:
        Mock assistant response suitable for testing the avatar pipeline.
    """
    persona = get_persona(persona_id)
    return (
        f"I'm {persona.name}. I received: '{message}'. "
        "In a real run, this text would come from the language model. "
        "For the classroom test, use this mock reply to verify the avatar state, "
        "audio playback, and frontend-backend connection."
    )


def generate_reply(message: str, persona_id: str, settings: Settings) -> str:
    """Generate a persona-controlled assistant reply.

    Args:
        message: User message.
        persona_id: Persona selected by the frontend.
        settings: Application settings.

    Returns:
        Assistant response text.

    Raises:
        RuntimeError: If the OpenAI call fails.
    """
    if settings.mock_mode:
        return generate_mock_reply(message, persona_id)

    client = OpenAI(api_key=settings.openai_api_key)

    # COST NOTE: For short classroom turns with gpt-4o-mini, this is usually a fraction of one cent.
    try:
        response = client.responses.create(
            model=settings.openai_model,
            instructions=build_instructions(persona_id),
            input=message,
            temperature=0.4,
            max_output_tokens=320,
        )
    except Exception as exc:  # noqa: BLE001 - convert SDK errors into classroom-friendly errors
        raise RuntimeError(f"OpenAI text generation failed: {exc}") from exc

    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise RuntimeError("OpenAI returned an empty text response.")
    return output_text.strip()
