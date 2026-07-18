"""Thread-safe in-memory job store for classroom background-task demos.

This intentionally uses memory instead of a database so the trigger pattern is
easy to understand. In production, use a durable store such as PostgreSQL,
Redis, or a queue-backed worker system.
"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from app.schemas import (
    AgentResult,
    EventSource,
    JobRecord,
    JobStatus,
    JobStatusResponse,
    TextSubmittedEvent,
)


class JobStore:
    """Small thread-safe store for tracking background jobs."""

    def __init__(self) -> None:
        """Initialize an empty job dictionary and lock."""
        self._jobs: dict[str, JobRecord] = {}
        self._lock = Lock()

    def create_job(self, event: TextSubmittedEvent) -> JobRecord:
        """Create a queued job for an incoming event.

        Args:
            event: Validated webhook event.

        Returns:
            Newly created job record.
        """
        now = datetime.now(timezone.utc)
        job = JobRecord(
            job_id=f"job_{uuid4().hex[:12]}",
            status=JobStatus.QUEUED,
            event_id=event.event_id,
            event_type=event.event_type,
            source=event.source,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._jobs[job.job_id] = job
        return job

    def mark_running(self, job_id: str) -> None:
        """Mark a job as currently running.

        Args:
            job_id: Unique job identifier.
        """
        self._update_status(job_id, JobStatus.RUNNING)

    def mark_completed(self, job_id: str, result: AgentResult) -> None:
        """Mark a job as completed with an agent result.

        Args:
            job_id: Unique job identifier.
            result: Structured agent output.
        """
        with self._lock:
            job = self._require_job(job_id)
            self._jobs[job_id] = job.model_copy(
                update={
                    "status": JobStatus.COMPLETED,
                    "result": result,
                    "error": None,
                    "updated_at": datetime.now(timezone.utc),
                }
            )

    def mark_failed(self, job_id: str, error: str) -> None:
        """Mark a job as failed and store the error message.

        Args:
            job_id: Unique job identifier.
            error: Human-readable error description.
        """
        with self._lock:
            job = self._require_job(job_id)
            self._jobs[job_id] = job.model_copy(
                update={
                    "status": JobStatus.FAILED,
                    "error": error,
                    "updated_at": datetime.now(timezone.utc),
                }
            )

    def get_job(self, job_id: str) -> JobStatusResponse | None:
        """Return a job response by ID.

        Args:
            job_id: Unique job identifier.

        Returns:
            Job status response, or None when the job does not exist.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            return JobStatusResponse(**job.model_dump())

    def list_jobs(self) -> list[JobStatusResponse]:
        """List jobs in reverse creation order.

        Returns:
            Job status responses, newest first.
        """
        with self._lock:
            records = sorted(self._jobs.values(), key=lambda job: job.created_at, reverse=True)
            return [JobStatusResponse(**record.model_dump()) for record in records]

    def reset(self) -> None:
        """Delete all jobs from the in-memory store."""
        with self._lock:
            self._jobs.clear()

    def _update_status(self, job_id: str, status: JobStatus) -> None:
        """Update a job status.

        Args:
            job_id: Unique job identifier.
            status: New job status.
        """
        with self._lock:
            job = self._require_job(job_id)
            self._jobs[job_id] = job.model_copy(
                update={"status": status, "updated_at": datetime.now(timezone.utc)}
            )

    def _require_job(self, job_id: str) -> JobRecord:
        """Return a job record or raise KeyError.

        Args:
            job_id: Unique job identifier.

        Returns:
            JobRecord from the store.

        Raises:
            KeyError: When the job ID is unknown.
        """
        if job_id not in self._jobs:
            raise KeyError(f"Unknown job_id: {job_id}")
        return self._jobs[job_id]


job_store = JobStore()
