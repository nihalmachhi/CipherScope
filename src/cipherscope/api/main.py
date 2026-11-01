from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from cipherscope.api.jobs import JobRegistry
from cipherscope.api.repository import FlowRepository
from cipherscope.api.routers import alerts, drift, experiments, flows, models
from cipherscope.core.settings import Settings
from cipherscope.datasets.synthetic import generate_demo
from cipherscope.features.beacon import detect_beacons

ROUTERS = (flows, alerts, models, drift, experiments)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Generate demo data once, then serve from an indexed in-memory repository."""
    settings: Settings = app.state.settings
    data_path = Path(settings.data_path)
    if not data_path.exists():
        generate_demo(data_path)
    app.state.repository = FlowRepository(data_path)
    app.state.jobs = JobRegistry()
    app.state.tasks = set()
    app.state.last_experiment_run = None
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application so tests and servers can inject settings."""
    config = settings or Settings()
    app = FastAPI(
        title="CipherScope Encrypted Traffic Intelligence",
        version="0.2.0",
        lifespan=lifespan,
    )
    app.state.settings = config
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.cors_origin],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    for module in ROUTERS:
        app.include_router(module.router)

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "mode": "synthetic-demo",
            "flows": app.state.repository.total(),
        }

    @app.websocket("/live")
    async def live(socket: WebSocket) -> None:
        await socket.accept()
        repository: FlowRepository = app.state.repository
        index = 0
        try:
            while True:
                found = detect_beacons(repository.rows())
                if found:
                    alert = found[index % len(found)]
                    index += 1
                    await socket.send_json({"kind": "alert", "replay": True, **alert})
                else:
                    await socket.send_json({"kind": "heartbeat", "alerts": 0})
                await asyncio.sleep(config.replay_interval_s)
        except WebSocketDisconnect:
            return

    return app
