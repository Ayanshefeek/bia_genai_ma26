"""Send a simulated GitHub issue webhook to the FastAPI trigger service."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.security import build_signature  # noqa: E402

load_dotenv(PROJECT_ROOT / ".env")

SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8000")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "bia-demo-secret")
SIGN_EVENTS = os.getenv("SIGN_EVENTS", "true").lower() in {"1", "true", "yes", "y"}


def send_event() -> None:
    """Send the sample GitHub issue event, then poll the job status."""
    payload_path = PROJECT_ROOT / "data" / "github_issue_event.json"
    raw_body = payload_path.read_bytes()

    headers = {"Content-Type": "application/json"}
    if SIGN_EVENTS:
        headers["X-BIA-Signature"] = build_signature(raw_body, WEBHOOK_SECRET)

    response = requests.post(
        f"{SERVER_URL}/webhooks/github-issue",
        data=raw_body,
        headers=headers,
        timeout=30,
    )
    print("Webhook response:", response.status_code, response.text)
    response.raise_for_status()

    job_id = response.json()["job_id"]
    for attempt in range(10):
        status_response = requests.get(f"{SERVER_URL}/jobs/{job_id}", timeout=30)
        status_payload = status_response.json()
        print(f"Poll {attempt + 1}:", json.dumps(status_payload, indent=2))
        if status_payload["status"] in {"completed", "failed"}:
            break
        time.sleep(1)


if __name__ == "__main__":
    send_event()
