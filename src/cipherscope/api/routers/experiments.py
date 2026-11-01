from __future__ import annotations

import asyncio
import hmac
import time
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request, status

from cipherscope.api.deps import get_jobs, get_settings
from cipherscope.api.jobs import Job
from cipherscope.core.settings import PLACEHOLDER_TOKENS
from cipherscope.eval.runner import run_evaluation

router = APIRouter(tags=["experiments"])


def _authorize(token: str | None, expected: str | None) -> None:
    if not expected or expected.strip().lower() in PLACEHOLDER_TOKENS:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "CIPHERSCOPE_ADMIN_TOKEN is not configured; admin endpoints are disabled.",
        )
    if not token or not hmac.compare_digest(token, expected):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "A valid local admin token is required")


async def _run_job(request: Request, job: Job) -> None:
    settings = get_settings(request)
    jobs = get_jobs(request)
    job.status = "running"
    try:
        result = await asyncio.to_thread(run_evaluation, settings.data_path, settings.report_path)
        summary = {
            name: split["summary"]["macro_f1"]["mean"]
            for name, split in result["splits"].items()
            if "summary" in split
        }
        jobs.finish(job, summary)
    except Exception as exc:  # pragma: no cover - defensive boundary
        jobs.fail(job, str(exc))


@router.post("/experiments/run", status_code=status.HTTP_202_ACCEPTED)
async def experiments_run(
    request: Request, x_admin_token: str | None = Header(default=None)
) -> dict[str, Any]:
    """Queue a background evaluation run after checking the local admin token."""
    settings = get_settings(request)
    _authorize(x_admin_token, settings.admin_token)
    now = time.monotonic()
    last_run = getattr(request.app.state, "last_experiment_run", None)
    if last_run is not None and now - last_run < settings.experiment_rate_limit_s:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Evaluation rate limit reached")
    request.app.state.last_experiment_run = now

    job = get_jobs(request).create()
    task = asyncio.create_task(_run_job(request, job))
    request.app.state.tasks.add(task)
    task.add_done_callback(request.app.state.tasks.discard)
    return {
        "job_id": job.job_id,
        "status": job.status,
        "status_url": f"/experiments/jobs/{job.job_id}",
    }


@router.get("/experiments/jobs/{job_id}")
def experiment_job(job_id: str, request: Request) -> dict[str, Any]:
    """Return the status and summary of a queued evaluation run."""
    job = get_jobs(request).get(job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job.as_dict()
