"""FastAPI app that receives webhook events and triggers an agent in the background."""

from __future__ import annotations

from typing import Annotated

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from app.agent import summarise_event
from app.jobs import job_store
from app.schemas import (
    GitHubIssueEvent,
    HealthResponse,
    JobAcceptedResponse,
    JobListResponse,
    JobStatus,
    JobStatusResponse,
    TextSubmittedEvent,
)
from app.security import SIGNATURE_HEADER_NAME, verify_signature_or_raise
from app.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Classroom demo: receive simulated webhook events, acknowledge quickly, "
        "and trigger a summarisation agent in the background."
    ),
)

# CORS is included as a preview for the next session where a frontend dashboard
# consumes backend responses.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_text_event_job(job_id: str, event: TextSubmittedEvent) -> None:
    """Run the summarisation agent and update the job store.

    Args:
        job_id: Job created when the webhook was accepted.
        event: Validated webhook payload.
    """
    job_store.mark_running(job_id)
    try:
        result = summarise_event(event)
        job_store.mark_completed(job_id, result)
    except Exception as exc:  # noqa: BLE001 - trainer demo should capture any agent failure.
        job_store.mark_failed(job_id, str(exc))


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service health and whether mock LLM mode is enabled.

    Returns:
        HealthResponse for smoke testing and frontend checks.
    """
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        mock_llm_enabled=settings.use_mock_llm,
    )


@app.post(
    "/webhooks/text-submitted",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def receive_text_submitted_event(
    event: TextSubmittedEvent,
    background_tasks: BackgroundTasks,
    request: Request,
    x_bia_signature: Annotated[str | None, Header(alias=SIGNATURE_HEADER_NAME)] = None,
) -> JobAcceptedResponse:
    """Receive a generic text event and trigger the agent asynchronously.

    Args:
        event: Validated JSON request body.
        background_tasks: FastAPI background task manager.
        request: Raw request object used for signature verification.
        x_bia_signature: Optional HMAC signature header.

    Returns:
        Immediate acknowledgement with a job ID.
    """
    raw_body = await request.body()
    verify_signature_or_raise(raw_body, x_bia_signature)

    job = job_store.create_job(event)
    background_tasks.add_task(process_text_event_job, job.job_id, event)

    return JobAcceptedResponse(
        job_id=job.job_id,
        status=JobStatus.QUEUED,
        message="Event accepted. Agent processing started in the background.",
    )


@app.post(
    "/webhooks/github-issue",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def receive_github_issue_event(
    event: GitHubIssueEvent,
    background_tasks: BackgroundTasks,
    request: Request,
    x_bia_signature: Annotated[str | None, Header(alias=SIGNATURE_HEADER_NAME)] = None,
) -> JobAcceptedResponse:
    """Receive a simulated GitHub issue event and trigger the generic text agent.

    Args:
        event: Simplified GitHub issue webhook payload.
        background_tasks: FastAPI background task manager.
        request: Raw request object used for signature verification.
        x_bia_signature: Optional HMAC signature header.

    Returns:
        Immediate acknowledgement with a job ID.
    """
    raw_body = await request.body()
    verify_signature_or_raise(raw_body, x_bia_signature)

    text_event = event.to_text_event()
    job = job_store.create_job(text_event)
    background_tasks.add_task(process_text_event_job, job.job_id, text_event)

    return JobAcceptedResponse(
        job_id=job.job_id,
        status=JobStatus.QUEUED,
        message="GitHub issue event accepted. Agent processing started in the background.",
    )


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    """Return the current status and result for one job.

    Args:
        job_id: Job identifier returned by a webhook endpoint.

    Returns:
        Job status response.

    Raises:
        HTTPException: If the job ID is unknown.
    """
    job = job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job


@app.get("/jobs", response_model=JobListResponse)
def list_jobs() -> JobListResponse:
    """Return all in-memory jobs.

    Returns:
        List of job status responses.
    """
    return JobListResponse(jobs=job_store.list_jobs())


@app.post("/admin/reset-jobs", status_code=status.HTTP_204_NO_CONTENT)
def reset_jobs() -> None:
    """Clear the in-memory job store.

    Returns:
        None.
    """
    job_store.reset()
