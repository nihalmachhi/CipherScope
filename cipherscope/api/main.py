from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict

from cipherscope.datasets.synthetic import generate_demo
from cipherscope.eval.runner import load_rows, run_evaluation
from cipherscope.features.beacon import detect_beacons
from cipherscope.features.graph import host_graph


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CIPHERSCOPE_", env_file=".env", extra="ignore")
    data_path: str = "data/demo_flows.jsonl"
    report_path: str = "output/reports/synthetic-evaluation.json"
    cors_origin: str = "http://127.0.0.1:5173"
    admin_token: str = "local-demo-admin-token"


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    data_path = Path(config.data_path)
    if not data_path.exists():
        generate_demo(data_path)
    app = FastAPI(title="CipherScope Encrypted Traffic Intelligence", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.cors_origin],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    def rows() -> list[dict[str, Any]]:
        return load_rows(data_path)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "synthetic-demo"}

    @app.get("/flows")
    def flows(
        label: str | None = Query(default=None, alias="class"),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> dict[str, Any]:
        found = rows()
        if label:
            found = [row for row in found if row["label"] == label]
        return {"total": len(found), "flows": found[offset : offset + limit]}

    @app.get("/flows/{flow_id}")
    def flow_detail(flow_id: str) -> dict[str, Any]:
        found = next((row for row in rows() if row["flow_id"] == flow_id), None)
        if found is None:
            raise HTTPException(404, "Flow not found")
        return found

    @app.get("/alerts")
    def alerts() -> dict[str, Any]:
        found = detect_beacons(rows())
        return {"alerts": found, "note": "Synthetic demo data only; alerts require analyst review."}

    @app.get("/hosts/{host_hash}/graph")
    def host_neighborhood(host_hash: str) -> dict[str, Any]:
        all_rows = rows()
        related = [
            row
            for row in all_rows
            if row["host_hash"] == host_hash or row["peer_hash"] == host_hash
        ]
        return host_graph(related)

    @app.get("/models")
    def models() -> dict[str, Any]:
        report = Path(config.report_path)
        if not report.exists():
            return {
                "models": [],
                "status": "not_evaluated",
                "message": "Run `uv run python -m cipherscope.eval.runner` to train and evaluate the baseline.",
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

    @app.get("/drift")
    def drift() -> dict[str, Any]:
        return {
            "status": "not_configured",
            "message": "Drift needs timestamped production or lab observations.",
            "privacy": "No raw identifiers are used as model features.",
        }

    @app.post("/experiments/run")
    def experiments_run(x_admin_token: str | None = Header(default=None)) -> dict[str, Any]:
        expected = os.getenv("CIPHERSCOPE_ADMIN_TOKEN", config.admin_token)
        if not x_admin_token or x_admin_token != expected:
            raise HTTPException(403, "A valid local admin token is required")
        report = run_evaluation(data_path, config.report_path)
        return {"status": "complete", "report": report}

    @app.websocket("/live")
    async def live(socket: WebSocket) -> None:
        await socket.accept()
        try:
            while True:
                await socket.send_json(
                    {"kind": "demo_heartbeat", "mode": "offline-replay", "flow_count": len(rows())}
                )
                await asyncio.sleep(5)
        except WebSocketDisconnect:
            return

    return app


app = create_app()
