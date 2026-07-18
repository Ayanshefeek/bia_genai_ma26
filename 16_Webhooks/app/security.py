"""Webhook signature helpers for classroom-safe request verification."""

from __future__ import annotations

import hashlib
import hmac

from fastapi import HTTPException, status

from app.settings import get_settings


SIGNATURE_HEADER_NAME = "X-BIA-Signature"


def build_signature(raw_body: bytes, secret: str) -> str:
    """Build a SHA-256 HMAC signature for a raw request body.

    Args:
        raw_body: Exact bytes sent as the HTTP request body.
        secret: Shared webhook secret.

    Returns:
        Signature string in the form `sha256=<hex_digest>`.
    """
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_signature_or_raise(raw_body: bytes, provided_signature: str | None) -> None:
    """Validate a webhook signature or raise a 401 HTTP error.

    Args:
        raw_body: Exact request body bytes.
        provided_signature: Value of the X-BIA-Signature request header.

    Raises:
        HTTPException: If signature verification is required and fails.
    """
    settings = get_settings()
    if settings.accept_unsigned_events and not provided_signature:
        return

    if not provided_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature header.",
        )

    expected_signature = build_signature(raw_body, settings.webhook_secret)
    if not hmac.compare_digest(provided_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature.",
        )
