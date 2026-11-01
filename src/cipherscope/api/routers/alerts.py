from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Request

from cipherscope.api.deps import get_repository
from cipherscope.api.schemas import AlertList
from cipherscope.features.beacon import DEFAULT_THRESHOLD, detect_beacons

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=AlertList)
def alerts(
    request: Request,
    threshold: float = Query(DEFAULT_THRESHOLD, ge=0.0, le=1.0),
) -> dict[str, Any]:
    """Return beacon alerts that need analyst review."""
    return {
        "alerts": detect_beacons(get_repository(request).rows(), threshold=threshold),
        "note": "Synthetic demo data only; alerts require analyst review.",
    }
