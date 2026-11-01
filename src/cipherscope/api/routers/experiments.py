from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from cipherscope.api.deps import get_settings
from cipherscope.eval.runner import run_evaluation

router = APIRouter(tags=["experiments"])


@router.post("/experiments/run")
def experiments_run(
    request: Request, x_admin_token: str | None = Header(default=None)
) -> dict[str, Any]:
    """Re-run the evaluation after checking the local admin token."""
    config = get_settings(request)
    expected = os.getenv("CIPHERSCOPE_ADMIN_TOKEN", config.admin_token)
    if not x_admin_token or x_admin_token != expected:
        raise HTTPException(403, "A valid local admin token is required")
    report = run_evaluation(request.app.state.data_path, config.report_path)
    return {"status": "complete", "report": report}
