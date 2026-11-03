from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from cipherscope.datasets.registry import load_dataset
from cipherscope.features.graph import host_graph
from cipherscope.models.base import train
from cipherscope.models.calibration import calibrate
from cipherscope.models.cnn1d import TORCH_AVAILABLE, predict_sequence, train_sequence_model
from cipherscope.models.explain import top_permutation_importance
from cipherscope.store.parquet import PARQUET_AVAILABLE, write_parquet

FIXTURES = Path(__file__).parent / "fixtures"
SALT = "phase-two-test-salt-long-enough"


@pytest.mark.parametrize(
    ("dataset", "fixture", "expected"),
    [
        ("iscx_vpn_nonvpn", "iscx_tiny.csv", "iscx-vpn-nonvpn"),
        ("cic_ids2017", "cic_tiny.csv", "cic-ids2017"),
        ("ustc_tfc2016", "iscx_tiny.csv", "ustc-tfc2016"),
    ],
)
def test_registered_loaders_normalize_authorized_csv(
    dataset: str, fixture: str, expected: str
) -> None:
    flows = load_dataset(
        dataset,
        FIXTURES / fixture,
        accept_license=True,
        capture_id="loader-fixture",
        environment="lab-alpha",
        label="benign",
        salt=SALT,
    )
    assert flows
    assert all(flow.dataset == expected and flow.bytes_total > 0 for flow in flows)


def test_undirected_graph_uses_persisted_bytes_total() -> None:
    flows = [
        {"host_hash": "h:b", "peer_hash": "h:a", "bytes_total": 500, "duration_s": 2.0},
        {"host_hash": "h:a", "peer_hash": "h:b", "bytes_total": 700, "duration_s": 3.0},
    ]
    graph = host_graph(flows)
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["bytes_total"] == 1200
    assert graph["edges"][0]["flow_count"] == 2


def _model_rows() -> list[dict[str, object]]:
    return [
        {
            "host_hash": f"h:{index // 4}",
            "label": "beacon" if index % 2 else "web",
            "features": {"packet_count": float(index % 2), "iat_cv": float(index % 3)},
        }
        for index in range(32)
    ]


def test_grouped_isotonic_calibration_and_permutation_importance() -> None:
    rows = _model_rows()
    train_indices = np.arange(24)
    test_rows = rows[24:]
    calibrated = calibrate(rows, train_indices, ["packet_count", "iat_cv"], "logreg", 7)
    assert calibrated.predict_proba(test_rows).shape == (8, 2)

    baseline = train(rows, train_indices, ["packet_count", "iat_cv"], "logreg", 7)
    importance = top_permutation_importance(baseline, test_rows, repeats=2)
    assert {item["feature"] for item in importance} == {"packet_count", "iat_cv"}
    assert all(np.isfinite(item["importance_mean"]) for item in importance)


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="optional [deep] extra is not installed")
def test_optional_cnn_trains_and_predicts() -> None:
    tensors = [[[float(index % 3), float(index % 5), 0.0] for _ in range(64)] for index in range(6)]
    model = train_sequence_model(tensors, [0, 1, 0, 1, 0, 1], epochs=1)
    assert predict_sequence(model, tensors).shape == (6,)


def test_parquet_writer_has_clear_optional_dependency_behavior(tmp_path: Path) -> None:
    destination = tmp_path / "flows.parquet"
    rows = [{"flow_id": "h:one", "bytes_total": 12}]
    if PARQUET_AVAILABLE:
        assert write_parquet(rows, destination) == 1
        assert destination.exists()
    else:
        with pytest.raises(RuntimeError, match=r"Install the \[parquet\] extra"):
            write_parquet(rows, destination)
