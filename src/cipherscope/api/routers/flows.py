from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from cipherscope.api.deps import get_repository
from cipherscope.api.schemas import FlowDetail, FlowPage

router = APIRouter(tags=["flows"])


@router.get("/flows", response_model=FlowPage)
def list_flows(
    request: Request,
    label: str | None = Query(default=None, alias="class"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Return one page of stored flows, optionally filtered by label."""
    rows = get_repository(request).rows()
    if label:
        rows = [row for row in rows if row["label"] == label]
    return {
        "total": len(rows),
        "limit": limit,
        "offset": offset,
        "flows": rows[offset : offset + limit],
    }


@router.get("/flows/{flow_id}")
def flow_detail(flow_id: str, request: Request) -> dict[str, Any]:
    """Return a single stored flow by identifier."""
    found = get_repository(request).get(flow_id)
    if found is None:
        raise HTTPException(404, "Flow not found")
    return found
