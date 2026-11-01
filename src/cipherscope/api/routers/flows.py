from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from cipherscope.api.deps import read_rows

router = APIRouter(tags=["flows"])


@router.get("/flows")
def list_flows(
    request: Request,
    label: str | None = Query(default=None, alias="class"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Return one page of stored flows, optionally filtered by label."""
    found = read_rows(request)
    if label:
        found = [row for row in found if row["label"] == label]
    return {"total": len(found), "flows": found[offset : offset + limit]}


@router.get("/flows/{flow_id}")
def flow_detail(flow_id: str, request: Request) -> dict[str, Any]:
    """Return a single stored flow by identifier."""
    found = next((row for row in read_rows(request) if row["flow_id"] == flow_id), None)
    if found is None:
        raise HTTPException(404, "Flow not found")
    return found
