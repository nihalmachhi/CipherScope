from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["drift"])


@router.get("/drift")
def drift() -> dict[str, Any]:
    """Report drift availability; a real implementation lands in a later phase."""
    return {
        "status": "not_configured",
        "message": "Drift needs timestamped production or lab observations.",
        "privacy": "No raw identifiers are used as model features.",
    }
