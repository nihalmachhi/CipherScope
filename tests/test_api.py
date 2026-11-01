from __future__ import annotations

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cipherscope.api.main import create_app
from cipherscope.core.settings import Settings

ADMIN_TOKEN = "unit-test-admin-token"


def settings(tmp_path: Path, **overrides: object) -> Settings:
    values: dict[str, object] = {
        "data_path": str(tmp_path / "flows.jsonl"),
        "report_path": str(tmp_path / "report.json"),
        "admin_token": ADMIN_TOKEN,
        "experiment_rate_limit_s": 0.0,
        "replay_interval_s": 0.01,
    }
    values.update(overrides)
    return Settings(**values)


def test_dashboard_api_offline_demo(tmp_path) -> None:
    with TestClient(create_app(settings(tmp_path))) as client:
        health = client.get("/health").json()
        assert health["mode"] == "synthetic-demo"
        assert health["flows"] == 450
        response = client.get("/flows?limit=3")
        assert response.status_code == 200
        assert response.json()["total"] == 450
        assert len(response.json()["flows"]) == 3
        flow_id = response.json()["flows"][0]["flow_id"]
        assert client.get(f"/flows/{flow_id}").status_code == 200
        assert client.get("/flows/unknown-flow").status_code == 404
        assert client.get("/models").json()["status"] == "not_evaluated"
        assert len(client.get("/alerts").json()["alerts"]) >= 1


def test_websocket_replays_real_alerts(tmp_path) -> None:
    with (
        TestClient(create_app(settings(tmp_path))) as client,
        client.websocket_connect("/live") as socket,
    ):
        message = socket.receive_json()
        assert message["kind"] == "alert"
        assert message["replay"] is True
        assert message["host_hash"].startswith("h:")


def test_admin_endpoint_fails_closed_without_token(tmp_path) -> None:
    with TestClient(create_app(settings(tmp_path, admin_token=""))) as client:
        assert client.post("/experiments/run").status_code == 503


def test_admin_endpoint_rejects_wrong_token(tmp_path) -> None:
    with TestClient(create_app(settings(tmp_path))) as client:
        assert client.post("/experiments/run").status_code == 403
        response = client.post("/experiments/run", headers={"X-Admin-Token": "wrong-token"})
        assert response.status_code == 403


def test_admin_endpoint_queues_background_job(tmp_path, monkeypatch) -> None:
    def fake_evaluation(dataset_path, report_path):
        return {"splits": {"S1_random_caution_only": {"summary": {"macro_f1": {"mean": 0.5}}}}}

    monkeypatch.setattr("cipherscope.api.routers.experiments.run_evaluation", fake_evaluation)
    with TestClient(create_app(settings(tmp_path))) as client:
        response = client.post("/experiments/run", headers={"X-Admin-Token": ADMIN_TOKEN})
        assert response.status_code == 202
        payload = response.json()
        assert payload["status"] in {"queued", "running"}
        job_id = payload["job_id"]
        for _ in range(100):
            status = client.get(f"/experiments/jobs/{job_id}").json()
            if status["status"] in {"complete", "failed"}:
                break
            time.sleep(0.02)
        assert status["status"] == "complete"
        assert status["summary"]["S1_random_caution_only"] == 0.5
        assert client.get("/experiments/jobs/missing").status_code == 404


def test_admin_endpoint_rate_limits(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "cipherscope.api.routers.experiments.run_evaluation",
        lambda dataset_path, report_path: {"splits": {}},
    )
    with TestClient(create_app(settings(tmp_path, experiment_rate_limit_s=60.0))) as client:
        headers = {"X-Admin-Token": ADMIN_TOKEN}
        assert client.post("/experiments/run", headers=headers).status_code == 202
        assert client.post("/experiments/run", headers=headers).status_code == 429


@pytest.mark.parametrize("placeholder", ["", "change-me"])
def test_placeholder_admin_token_disables_endpoint(tmp_path, placeholder) -> None:
    with TestClient(create_app(settings(tmp_path, admin_token=placeholder))) as client:
        assert client.post("/experiments/run").status_code == 503
