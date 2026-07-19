"""In-memory WebSocket connection manager.

The manager tracks browser clients by assistant run ID. It is intentionally
simple for classroom use: production systems should move fan-out state to
Redis, a message broker, or a managed realtime layer.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket clients grouped by run ID."""

    def __init__(self) -> None:
        """Initialise the manager with no active connections."""

        self._active_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def connect(self, run_id: str, websocket: WebSocket) -> None:
        """Accept and store a WebSocket connection.

        Args:
            run_id: Assistant run identifier.
            websocket: FastAPI WebSocket instance.

        Returns:
            None
        """

        await websocket.accept()
        async with self._lock:
            self._active_connections[run_id].append(websocket)

    async def disconnect(self, run_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket connection.

        Args:
            run_id: Assistant run identifier.
            websocket: FastAPI WebSocket instance.

        Returns:
            None
        """

        async with self._lock:
            connections = self._active_connections.get(run_id, [])
            if websocket in connections:
                connections.remove(websocket)
            if not connections and run_id in self._active_connections:
                del self._active_connections[run_id]

    async def broadcast(self, run_id: str, message: dict[str, Any]) -> None:
        """Send a JSON message to every client watching a run.

        Args:
            run_id: Assistant run identifier.
            message: JSON-serialisable message payload.

        Returns:
            None
        """

        async with self._lock:
            connections = list(self._active_connections.get(run_id, []))

        failed_connections: list[WebSocket] = []
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except RuntimeError:
                failed_connections.append(websocket)

        for websocket in failed_connections:
            await self.disconnect(run_id, websocket)

    async def active_count(self, run_id: str) -> int:
        """Return the number of clients watching a run.

        Args:
            run_id: Assistant run identifier.

        Returns:
            int: Active connection count.
        """

        async with self._lock:
            return len(self._active_connections.get(run_id, []))
