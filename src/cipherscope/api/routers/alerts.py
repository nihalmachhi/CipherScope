from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from cipherscope.api.deps import read_rows
from cipherscope.features.beacon import detect_beacons

router = APIRouter(tags=["alerts"])


@router.get("/alerts")
def alerts(request: Request) -> dict[str, Any]:
    """Return beacon alerts that need analyst review."""
    return {
        "alerts": detect_beacons(read_rows(request)),
        "note": "Synthetic demo data only; alerts require analyst review.",
    }
