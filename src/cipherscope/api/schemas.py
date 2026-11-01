from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FlowPage(BaseModel):
    total: int
    limit: int
    offset: int
    flows: list[dict[str, Any]]


class FlowDetail(BaseModel):
    flow: dict[str, Any]


class AlertList(BaseModel):
    alerts: list[dict[str, Any]]


class ModelStatus(BaseModel):
    status: str
    metrics: dict[str, Any] = Field(default_factory=dict)


class JobStatus(BaseModel):
    job_id: str
    status: str
    summary: dict[str, Any] = Field(default_factory=dict)


class DriftReport(BaseModel):
    baseline_rows: int
    current_rows: int
    features_compared: int
    drifted_features: int
    status: str
    features: list[dict[str, Any]]
    method: str | None = None
    privacy: str | None = None
    note: str | None = None