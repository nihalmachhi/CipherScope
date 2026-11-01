from __future__ import annotations

from typing import cast

from fastapi import Request

from cipherscope.api.jobs import JobRegistry
from cipherscope.api.repository import FlowRepository
from cipherscope.core.settings import Settings


def get_settings(request: Request) -> Settings:
    """Return the settings instance attached to the running application."""
    return cast(Settings, request.app.state.settings)


def get_repository(request: Request) -> FlowRepository:
    """Return the application's in-memory flow repository."""
    return cast(FlowRepository, request.app.state.repository)


def get_jobs(request: Request) -> JobRegistry:
    """Return the application's background job registry."""
    return cast(JobRegistry, request.app.state.jobs)
