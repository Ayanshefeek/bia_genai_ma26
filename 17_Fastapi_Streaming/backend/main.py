"""FastAPI backend for the Streaming Productivity Assistant project."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.agent import stream_productivity_response
from backend.config import get_settings
from backend.connection_manager import ConnectionManager
from backend.database import (
    append_chunk,
    create_event,
    create_run,
    get_event,
    get_run,
    init_db,
    list_chunks,
    list_events,
    list_runs,
    reset_demo_data,
    update_event_status,
    update_run_status,
)
from backend.mock_events import get_sample_events
from backend.schemas import (
    ProductivityEventCreate,
    StartRunResponse,
    TriggerResponse,
)


settings = get_settings()
manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise resources when the FastAPI application starts."""

    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Event trigger → LLM stream → WebSocket → React dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def process_run(run_id: str) -> None:
    """Run the assistant for one event, persisting and broadcasting chunks.

    Args:
        run_id: Assistant run identifier.

    Returns:
        None
    """

    run = get_run(run_id)
    if run is None:
        return

    if run["status"] in {"running", "completed"}:
        return

    event = get_event(run["event_id"])
    if event is None:
        update_run_status(run_id, "failed", error_message="Event not found.")
        return

    full_output = ""
    sequence = len(list_chunks(run_id))

    try:
        update_run_status(run_id, "running")
        update_event_status(event["id"], "processing")
        await manager.broadcast(run_id, {"type": "status", "status": "running"})

        async for chunk in stream_productivity_response(event):
            if not chunk:
                continue
            sequence += 1
            stored_chunk = append_chunk(run_id, sequence, chunk)
            full_output += chunk
            await manager.broadcast(
                run_id,
                {
                    "type": "token",
                    "run_id": run_id,
                    "sequence": stored_chunk["sequence"],
                    "content": stored_chunk["content"],
                },
            )

        update_run_status(run_id, "completed", final_output=full_output)
        update_event_status(event["id"], "completed")
        await manager.broadcast(
            run_id,
            {"type": "done", "run_id": run_id, "status": "completed", "final_output": full_output},
        )
    except Exception as exc:  # noqa: BLE001 - broadcast readable failure for classroom debug.
        error_message = f"{type(exc).__name__}: {exc}"
        update_run_status(run_id, "failed", error_message=error_message)
        update_event_status(event["id"], "failed")
        await manager.broadcast(
            run_id,
            {"type": "error", "run_id": run_id, "status": "failed", "message": error_message},
        )


@app.get("/api/health")
async def health() -> dict[str, Any]:
    """Return backend health and mode information.

    Returns:
        dict[str, Any]: Health response for UI and troubleshooting.
    """

    return {
        "status": "ok",
        "app_name": settings.app_name,
        "llm_mode": "mock" if settings.use_mock_llm or not settings.openai_api_key else "openai",
        "model": settings.openai_model,
    }


@app.get("/api/sample-events")
async def sample_events() -> list[dict[str, Any]]:
    """Return ready-to-trigger Gmail, Calendar, and task examples.

    Returns:
        list[dict[str, Any]]: Sample event payloads.
    """

    return get_sample_events()


@app.get("/api/events")
async def get_events(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent productivity events.

    Args:
        limit: Maximum number of events to return.

    Returns:
        list[dict[str, Any]]: Recent events.
    """

    return list_events(limit=limit)


@app.get("/api/runs")
async def get_runs(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent assistant runs.

    Args:
        limit: Maximum number of runs to return.

    Returns:
        list[dict[str, Any]]: Recent runs.
    """

    return list_runs(limit=limit)


@app.get("/api/runs/{run_id}")
async def get_run_detail(run_id: str) -> dict[str, Any]:
    """Return one assistant run with its persisted chunks.

    Args:
        run_id: Assistant run identifier.

    Returns:
        dict[str, Any]: Run detail and chunks.
    """

    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return {"run": run, "chunks": list_chunks(run_id)}


@app.post("/api/events")
async def create_event_only(event: ProductivityEventCreate) -> dict[str, Any]:
    """Create an event and a queued run without starting the LLM.

    Args:
        event: Productivity event payload.

    Returns:
        dict[str, Any]: Stored event and queued run.
    """

    stored_event = create_event(event)
    run = create_run(stored_event["id"])
    return {"event": stored_event, "run": run}


@app.post("/api/runs/{run_id}/start", response_model=StartRunResponse)
async def start_run(run_id: str, background_tasks: BackgroundTasks) -> StartRunResponse:
    """Start a queued assistant run.

    Args:
        run_id: Assistant run identifier.
        background_tasks: FastAPI background task manager.

    Returns:
        StartRunResponse: Start acknowledgement.
    """

    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    if run["status"] == "completed":
        return StartRunResponse(
            run_id=run_id,
            status="completed",
            message="Run already completed. Open its WebSocket to replay stored chunks.",
        )
    if run["status"] == "running":
        return StartRunResponse(
            run_id=run_id,
            status="running",
            message="Run is already streaming.",
        )
    background_tasks.add_task(process_run, run_id)
    return StartRunResponse(run_id=run_id, status="running", message="Run started.")


@app.post("/api/trigger", response_model=TriggerResponse)
async def trigger_event(
    event: ProductivityEventCreate,
    background_tasks: BackgroundTasks,
) -> TriggerResponse:
    """Create a mock productivity event and immediately start the assistant run.

    Args:
        event: Productivity event payload.
        background_tasks: FastAPI background task manager.

    Returns:
        TriggerResponse: IDs and WebSocket URL for the frontend.
    """

    stored_event = create_event(event)
    run = create_run(stored_event["id"])
    background_tasks.add_task(process_run, run["id"])
    return TriggerResponse(
        event_id=stored_event["id"],
        run_id=run["id"],
        websocket_url=f"/ws/runs/{run['id']}",
        status="running",
    )


@app.post("/api/reset")
async def reset_data() -> dict[str, str]:
    """Clear demo data from SQLite.

    Returns:
        dict[str, str]: Reset acknowledgement.
    """

    reset_demo_data()
    return {"status": "ok", "message": "Demo data reset."}


@app.websocket("/ws/runs/{run_id}")
async def stream_run(websocket: WebSocket, run_id: str) -> None:
    """Stream existing and live chunks for one assistant run.

    Args:
        websocket: Browser WebSocket connection.
        run_id: Assistant run identifier.

    Returns:
        None
    """

    run = get_run(run_id)
    if run is None:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Run not found."})
        await websocket.close(code=1008)
        return

    await manager.connect(run_id, websocket)

    try:
        await websocket.send_json({"type": "status", "run_id": run_id, "status": run["status"]})

        for chunk in list_chunks(run_id):
            await websocket.send_json(
                {
                    "type": "token",
                    "run_id": run_id,
                    "sequence": chunk["sequence"],
                    "content": chunk["content"],
                    "replay": True,
                }
            )

        refreshed_run = get_run(run_id)
        if refreshed_run and refreshed_run["status"] == "completed":
            await websocket.send_json(
                {
                    "type": "done",
                    "run_id": run_id,
                    "status": "completed",
                    "final_output": refreshed_run["final_output"],
                    "replay": True,
                }
            )

        while True:
            message = await websocket.receive_text()
            if message == "ping":
                await websocket.send_json({"type": "pong", "run_id": run_id})
    except WebSocketDisconnect:
        await manager.disconnect(run_id, websocket)
