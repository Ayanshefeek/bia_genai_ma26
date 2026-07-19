"""Sample Gmail, Calendar, and task events used by the practical."""

from __future__ import annotations

from backend.schemas import ProductivityEventCreate


SAMPLE_EVENTS: list[ProductivityEventCreate] = [
    ProductivityEventCreate(
        event_type="email",
        title="Client asks for a project status summary",
        priority="high",
        payload={
            "from": "maya@northstar-retail.example",
            "subject": "Can you send a status update before 4 PM?",
            "body": (
                "Hi, we have a leadership sync today. Please send a short update "
                "on completed work, open risks, and what you need from us."
            ),
            "received_at": "2026-07-01T09:30:00+05:30",
        },
    ),
    ProductivityEventCreate(
        event_type="calendar",
        title="Upcoming design review in 45 minutes",
        priority="normal",
        payload={
            "calendar": "Work",
            "meeting_title": "Streaming assistant design review",
            "attendees": ["Product Lead", "Engineering Lead", "Trainer"],
            "starts_at": "2026-07-01T15:00:00+05:30",
            "agenda": [
                "Review event-driven architecture",
                "Discuss streaming UX",
                "Assign next build tasks",
            ],
        },
    ),
    ProductivityEventCreate(
        event_type="task",
        title="Prepare handoff checklist for a delayed integration",
        priority="urgent",
        payload={
            "task_id": "TASK-418",
            "owner": "AI Engineering Team",
            "due": "2026-07-01T18:00:00+05:30",
            "notes": (
                "The webhook integration is delayed. Prepare a concise handoff "
                "with blockers, next actions, and escalation path."
            ),
        },
    ),
]


def get_sample_events() -> list[dict]:
    """Return sample events as dictionaries.

    Returns:
        list[dict]: JSON-serialisable sample event dictionaries.
    """

    return [event.model_dump() for event in SAMPLE_EVENTS]
