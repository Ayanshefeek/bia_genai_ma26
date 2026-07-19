"""SQLite persistence layer for productivity events, runs, and streamed chunks."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import get_settings
from backend.schemas import ProductivityEventCreate


def utc_now() -> str:
    """Return the current UTC timestamp in ISO-8601 format.

    Returns:
        str: Timezone-aware UTC timestamp.
    """

    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection configured for dictionary-like rows.

    Returns:
        sqlite3.Connection: SQLite connection with Row factory enabled.
    """

    db_path = get_settings().database_path
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create required SQLite tables if they do not already exist.

    Returns:
        None
    """

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                priority TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                status TEXT NOT NULL,
                final_output TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY(event_id) REFERENCES events(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            )
            """
        )
        connection.commit()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """Convert a SQLite row to a plain dictionary and decode JSON payloads.

    Args:
        row: SQLite row or None.

    Returns:
        dict[str, Any] | None: Plain dictionary representation.
    """

    if row is None:
        return None
    item = dict(row)
    if "payload" in item and isinstance(item["payload"], str):
        item["payload"] = json.loads(item["payload"])
    return item


def create_event(event: ProductivityEventCreate) -> dict[str, Any]:
    """Persist a productivity event.

    Args:
        event: Validated event creation payload.

    Returns:
        dict[str, Any]: Stored event record.
    """

    event_id = f"evt_{uuid.uuid4().hex[:10]}"
    created_at = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO events
            (id, event_type, title, source, priority, payload, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                event.event_type,
                event.title,
                event.source,
                event.priority,
                json.dumps(event.payload),
                "received",
                created_at,
            ),
        )
        connection.commit()
    stored = get_event(event_id)
    if stored is None:
        raise RuntimeError("Event was not persisted correctly.")
    return stored


def get_event(event_id: str) -> dict[str, Any] | None:
    """Fetch an event by ID.

    Args:
        event_id: Event identifier.

    Returns:
        dict[str, Any] | None: Event record if found.
    """

    with get_connection() as connection:
        row = connection.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    return row_to_dict(row)


def list_events(limit: int = 20) -> list[dict[str, Any]]:
    """List recent events.

    Args:
        limit: Maximum number of rows to return.

    Returns:
        list[dict[str, Any]]: Recent event records.
    """

    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM events ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [row_to_dict(row) for row in rows if row is not None]


def update_event_status(event_id: str, status: str) -> None:
    """Update the status of an event.

    Args:
        event_id: Event identifier.
        status: New event status.

    Returns:
        None
    """

    with get_connection() as connection:
        connection.execute("UPDATE events SET status = ? WHERE id = ?", (status, event_id))
        connection.commit()


def create_run(event_id: str) -> dict[str, Any]:
    """Create a queued assistant run for an event.

    Args:
        event_id: Event identifier.

    Returns:
        dict[str, Any]: Stored run record.
    """

    run_id = f"run_{uuid.uuid4().hex[:10]}"
    created_at = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO runs
            (id, event_id, status, final_output, error_message, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, event_id, "queued", None, None, created_at, None),
        )
        connection.commit()
    stored = get_run(run_id)
    if stored is None:
        raise RuntimeError("Run was not persisted correctly.")
    return stored


def get_run(run_id: str) -> dict[str, Any] | None:
    """Fetch an assistant run by ID.

    Args:
        run_id: Run identifier.

    Returns:
        dict[str, Any] | None: Run record if found.
    """

    with get_connection() as connection:
        row = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    return row_to_dict(row)


def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    """List recent assistant runs joined with event details.

    Args:
        limit: Maximum number of rows to return.

    Returns:
        list[dict[str, Any]]: Recent run records enriched with event metadata.
    """

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                runs.*,
                events.event_type,
                events.title,
                events.priority,
                events.source
            FROM runs
            JOIN events ON runs.event_id = events.id
            ORDER BY runs.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [row_to_dict(row) for row in rows if row is not None]


def update_run_status(
    run_id: str,
    status: str,
    final_output: str | None = None,
    error_message: str | None = None,
) -> None:
    """Update run status and optional final/error fields.

    Args:
        run_id: Run identifier.
        status: New status.
        final_output: Final assistant output when completed.
        error_message: Error details when failed.

    Returns:
        None
    """

    completed_at = utc_now() if status in {"completed", "failed"} else None
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE runs
            SET status = ?,
                final_output = COALESCE(?, final_output),
                error_message = ?,
                completed_at = COALESCE(?, completed_at)
            WHERE id = ?
            """,
            (status, final_output, error_message, completed_at, run_id),
        )
        connection.commit()


def append_chunk(run_id: str, sequence: int, content: str) -> dict[str, Any]:
    """Persist one streamed chunk.

    Args:
        run_id: Run identifier.
        sequence: Monotonic chunk number for the run.
        content: Text delta emitted by the assistant.

    Returns:
        dict[str, Any]: Persisted chunk record.
    """

    created_at = utc_now()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO chunks (run_id, sequence, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (run_id, sequence, content, created_at),
        )
        connection.commit()
        chunk_id = cursor.lastrowid
        row = connection.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,)).fetchone()
    stored = row_to_dict(row)
    if stored is None:
        raise RuntimeError("Chunk was not persisted correctly.")
    return stored


def list_chunks(run_id: str) -> list[dict[str, Any]]:
    """List persisted chunks for a run in streaming order.

    Args:
        run_id: Run identifier.

    Returns:
        list[dict[str, Any]]: Stream chunks sorted by sequence.
    """

    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM chunks WHERE run_id = ? ORDER BY sequence ASC", (run_id,)
        ).fetchall()
    return [row_to_dict(row) for row in rows if row is not None]


def reset_demo_data() -> None:
    """Delete all demo data while preserving the schema.

    Returns:
        None
    """

    with get_connection() as connection:
        connection.execute("DELETE FROM chunks")
        connection.execute("DELETE FROM runs")
        connection.execute("DELETE FROM events")
        connection.commit()
