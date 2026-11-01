from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

JobStatus = Literal["queued", "running", "complete", "failed"]


@dataclass
class Job:
    """State for one background evaluation run."""

    job_id: str
    status: JobStatus = "queued"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str | None = None
    summary: dict[str, Any] | None = None
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "summary": self.summary,
            "error": self.error,
        }


class JobRegistry:
    """Thread-safe registry of background evaluation jobs."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self) -> Job:
        job = Job(job_id=uuid.uuid4().hex[:12])
        with self._lock:
            self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def finish(self, job: Job, summary: dict[str, Any]) -> None:
        job.status = "complete"
        job.summary = summary
        job.finished_at = datetime.now(UTC).isoformat()

    def fail(self, job: Job, error: str) -> None:
        job.status = "failed"
        job.error = error
        job.finished_at = datetime.now(UTC).isoformat()
