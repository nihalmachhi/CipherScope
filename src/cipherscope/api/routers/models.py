from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request

from cipherscope.api.deps import get_settings

router = APIRouter(tags=["models"])


@router.get("/models")
def models(request: Request) -> dict[str, Any]:
    """Return the latest evaluation report, or a hint when none exists yet."""
    report = Path(get_settings(request).report_path)
    if not report.exists():
        return {
            "models": [],
            "status": "not_evaluated",
            "message": (
                "Run `uv run python -m cipherscope.eval.runner` to train and evaluate "
                "the baseline."
            ),
        }
    result = json.loads(report.read_text(encoding="utf-8"))
    return {
        "models": [
            {
                "name": "RandomForest tabular baseline",
                "family": "tabular",
                "results": result["splits"],
            }
        ],
        "data_kind": result["data_kind"],
        "limitations": result["limitations"],
    }
