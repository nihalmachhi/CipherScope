from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from cipherscope.api.routers import alerts, drift, experiments, flows, models
from cipherscope.core.settings import Settings
from cipherscope.datasets.synthetic import generate_demo
from cipherscope.eval.runner import load_rows

ROUTERS = (flows, alerts, models, drift, experiments)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application so tests and servers can inject settings."""
    config = settings or Settings()
    data_path = Path(config.data_path)
    if not data_path.exists():
        generate_demo(data_path)

    app = FastAPI(title="CipherScope Encrypted Traffic Intelligence", version="0.1.0")
    app.state.settings = config
    app.state.data_path = data_path
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.cors_origin],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    for module in ROUTERS:
        app.include_router(module.router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "synthetic-demo"}

    @app.websocket("/live")
    async def live(socket: WebSocket) -> None:
        await socket.accept()
        try:
            while True:
                await socket.send_json(
                    {
                        "kind": "demo_heartbeat",
                        "mode": "offline-replay",
                        "flow_count": len(load_rows(data_path)),
                    }
                )
                await asyncio.sleep(5)
        except WebSocketDisconnect:
            return

    return app


app = create_app()
