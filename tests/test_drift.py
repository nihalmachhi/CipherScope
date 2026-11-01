from __future__ import annotations

import pytest

from cipherscope.drift.psi import (
    chronological_drift,
    feature_drift,
    ks_two_sample,
    population_stability_index,
    psi_severity,
)


def _rows(values: list[float], start: float = 0.0) -> list[dict]:
    return [
        {"features": {"x": v, "y": v * 2}, "started_at": start + i} for i, v in enumerate(values)
    ]


def test_psi_severity_bands() -> None:
    assert psi_severity(0.0) == "stable"
    assert psi_severity(0.09) == "stable"
    assert psi_severity(0.1) == "moderate"
    assert psi_severity(0.2) == "moderate"
    assert psi_severity(0.25) == "significant"
    assert psi_severity(1.0) == "significant"


def test_population_stability_index_rejects_empty() -> None:
    with pytest.raises(ValueError):
        population_stability_index([], [1.0])
    with pytest.raises(ValueError):
        population_stability_index([1.0], [])


def test_population_stability_index_zero_for_identical() -> None:
    sample = [1.0, 2.0, 3.0, 4.0, 5.0]
    report = population_stability_index(sample, sample, bins=5)
    assert report["psi"] == pytest.approx(0.0, abs=1e-9)
    assert len(report["bins"]) == len(report["bins"])


def test_ks_two_sample_identical_is_zero() -> None:
    sample = [1.0, 2.0, 3.0, 4.0]
    result = ks_two_sample(sample, sample)
    assert result["statistic"] == 0.0
    assert result["p_value"] == pytest.approx(1.0, abs=1e-9)


def test_ks_two_sample_rejects_empty() -> None:
    with pytest.raises(ValueError):
        ks_two_sample([], [1.0])


def test_feature_drift_requires_both_windows() -> None:
    with pytest.raises(ValueError):
        feature_drift([], _rows([1.0, 2.0, 3.0]))
    with pytest.raises(ValueError):
        feature_drift(_rows([1.0, 2.0, 3.0]), [])


def test_feature_drift_detects_shift() -> None:
    baseline = _rows([1.0, 1.1, 0.9, 1.05, 1.0])
    current = _rows([5.0, 5.1, 4.9, 5.05, 5.0])
    report = feature_drift(baseline, current, bins=4, limit=5)
    assert report["status"] == "drift-detected"
    assert report["drifted_features"] >= 1
    assert report["features_compared"] >= 1
    assert report["features"][0]["psi"] > 0
    assert "severity" in report["features"][0]


def test_feature_drift_stable_identical() -> None:
    data = _rows([1.0, 2.0, 3.0, 4.0, 5.0])
    report = feature_drift(data, data, bins=4)
    assert report["status"] == "stable"
    assert report["drifted_features"] == 0


def test_feature_drift_limit_truncates() -> None:
    baseline = _rows([1.0, 1.1, 0.9, 1.05, 1.0])
    current = _rows([5.0, 5.1, 4.9, 5.05, 5.0])
    report = feature_drift(baseline, current, bins=4, limit=1)
    assert len(report["features"]) <= 1


def test_chronological_drift_requires_four_rows() -> None:
    with pytest.raises(ValueError):
        chronological_drift(_rows([1.0, 2.0, 3.0]), bins=4)


def test_chronological_drift_splits_by_start_time() -> None:
    rows = []
    for i, v in enumerate([1.0, 1.1, 5.0, 5.1]):
        rows.append({"features": {"x": v}, "started_at": float(i)})
    report = chronological_drift(rows, bins=4, limit=10)
    assert report["baseline_rows"] == 2
    assert report["current_rows"] == 2
    assert "split_at" in report
    assert report["status"] == "drift-detected"


def test_chronological_drift_api_endpoint(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from cipherscope.api.main import create_app
    from cipherscope.core.settings import Settings

    def settings() -> Settings:
        return Settings(
            data_path=str(tmp_path / "flows.jsonl"),
            report_path=str(tmp_path / "report.json"),
            admin_token="unit-test-admin-token",  # noqa: S106
        )

    with TestClient(create_app(settings())) as client:
        response = client.get("/drift?bins=4&limit=5")
        assert response.status_code == 200
        payload = response.json()
        assert payload["method"].startswith("PSI")
        assert "features" in payload
        assert payload["baseline_rows"] + payload["current_rows"] == 450
