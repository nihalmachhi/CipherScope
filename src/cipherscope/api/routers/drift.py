from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from cipherscope.api.deps import get_repository
from cipherscope.api.schemas import DriftReport
from cipherscope.drift.psi import chronological_drift

router = APIRouter(tags=["drift"])


@router.get("/drift", response_model=DriftReport)
def drift(
    request: Request,
    bins: int = Query(10, ge=2, le=50),
    limit: int = Query(10, ge=1, le=50),
) -> dict[str, Any]:
    """Compare early and late stored flows and report feature drift."""
    rows = get_repository(request).rows()
    if len(rows) < 4:
        raise HTTPException(409, "At least four stored flows are needed to compare two windows.")
    report = chronological_drift(rows, bins=bins, limit=limit)
    return {
        **report,
        "method": "PSI over baseline quantile bins plus two-sample KS",
        "privacy": "Only numeric metadata features are compared; no raw identifiers.",
        "note": "Demo data is synthetic, so drift here tests the detector, not a real shift.",
    }
