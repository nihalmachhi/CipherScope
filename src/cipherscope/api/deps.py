from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Request

from cipherscope.core.settings import Settings
from cipherscope.eval.runner import load_rows


def get_settings(request: Request) -> Settings:
    """Return the settings instance attached to the running application."""
    return request.app.state.settings


def get_data_path(request: Request) -> Path:
    """Return the JSONL file the application reads flows from."""
    return request.app.state.data_path


def read_rows(request: Request) -> list[dict[str, Any]]:
    """Load every stored flow row for the current request."""
    return load_rows(get_data_path(request))
