from __future__ import annotations

from fastapi.testclient import TestClient

from cipherscope.api.main import Settings, create_app


def test_dashboard_api_offline_demo(tmp_path) -> None:
    data_path = tmp_path / "flows.jsonl"
    report_path = tmp_path / "report.json"
    client = TestClient(
        create_app(Settings(data_path=str(data_path), report_path=str(report_path)))
    )
    assert client.get("/health").json()["mode"] == "synthetic-demo"
    response = client.get("/flows?limit=3")
    assert response.status_code == 200
    assert response.json()["total"] == 240
    flow_id = response.json()["flows"][0]["flow_id"]
    assert client.get(f"/flows/{flow_id}").status_code == 200
    assert client.get("/models").json()["status"] == "not_evaluated"
    assert len(client.get("/alerts").json()["alerts"]) >= 1


def test_experiment_endpoint_needs_admin_token(tmp_path) -> None:
    client = TestClient(
        create_app(
            Settings(
                data_path=str(tmp_path / "flows.jsonl"),
                report_path=str(tmp_path / "report.json"),
                admin_token="test-only",
            )
        )
    )
    assert client.post("/experiments/run").status_code == 403
    response = client.post("/experiments/run", headers={"x-admin-token": "test-only"})
    assert response.status_code == 200
    assert response.json()["report"]["data_kind"] == "synthetic demo"
