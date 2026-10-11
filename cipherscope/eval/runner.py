from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import f1_score

from cipherscope.features.tabular import extract_tabular
from cipherscope.models.tabular import evaluate, train_baseline
from cipherscope.robustness.perturb import perturb_padding, perturb_timing, truncate_packets
from cipherscope.splits.strategies import by_dataset, leave_one_environment_out


def load_rows(path: str | Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line
    ]


def run_evaluation(dataset_path: str | Path, report_path: str | Path) -> dict[str, Any]:
    rows = load_rows(dataset_path)
    if not rows or any(not row.get("features") or not row.get("label") for row in rows):
        raise ValueError("Evaluation expects labeled rows with precomputed metadata features")
    feature_names = sorted(rows[0]["features"])
    forbidden = ("ip", "port", "mac", "timestamp", "absolute_time")
    if any(any(token in name.lower() for token in forbidden) for name in feature_names):
        raise ValueError("Identifier or absolute-time feature found in model input")
    results: dict[str, Any] = {
        "data_kind": "synthetic demo"
        if all(row["dataset"].startswith("lab-") for row in rows)
        else "external dataset",
        "features": len(feature_names),
        "seeds": [7],
        "splits": {},
    }
    for split_name, split in (
        ("S1_random_caution_only", _random_split(rows, 7)),
        ("S4_cross_environment", by_dataset(rows, "lab-alpha", "lab-beta")),
        ("S5_leave_one_environment_out", leave_one_environment_out(rows, "lab-beta")),
    ):
        train_idx, test_idx = split
        model, encoder = train_baseline(rows, train_idx, feature_names, seed=7)
        results["splits"][split_name] = evaluate(model, encoder, rows, test_idx, feature_names)
    # Measure a single trained model under controlled metadata transformations.
    train_idx, test_idx = by_dataset(rows, "lab-alpha", "lab-beta")
    model, encoder = train_baseline(rows, train_idx, feature_names, seed=7)
    test_rows = [rows[int(index)] for index in test_idx]
    robustness = {}
    for name, transformed in (
        ("padding_30pct", [perturb_padding(row, 0.30) for row in test_rows]),
        ("timing_jitter_200ms", [perturb_timing(row, 0.20) for row in test_rows]),
        ("first_8_packets", [truncate_packets(row, 8) for row in test_rows]),
    ):
        copies = [
            {**row, "features": extract_tabular_from_dict(flow)}
            for row, flow in zip(test_rows, transformed, strict=True)
        ]
        truth = encoder.transform([row["label"] for row in copies])
        from cipherscope.models.tabular import _matrix

        prediction = model.predict(_matrix(copies, feature_names))
        robustness[name] = {
            "macro_f1": float(f1_score(truth, prediction, average="macro", zero_division=0))
        }
    results["robustness"] = robustness
    results["limitations"] = [
        "Synthetic labels are deliberately distinct; perfect scores only show the smoke-test pipeline works.",
        "Synthetic generated traffic is for pipeline validation only.",
        "No real-world generalization claim is made.",
        "Run at least three fixed seeds and licensed cross-dataset captures.",
    ]
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def extract_tabular_from_dict(flow: dict[str, Any]) -> dict[str, float]:
    from cipherscope.flows.schema import FlowRecord, PacketRecord

    packets = [PacketRecord(**packet) for packet in flow["packets"]]
    record = FlowRecord(
        flow["flow_id"],
        flow["host_hash"],
        flow["peer_hash"],
        flow["capture_id"],
        flow["environment"],
        flow["label"],
        flow["started_at"],
        "tcp",
        packets,
        packets[-1].timestamp if packets else flow["started_at"],
    )
    return extract_tabular(record)


def _random_split(rows: list[dict[str, Any]], seed: int) -> tuple[np.ndarray, np.ndarray]:
    indices = list(range(len(rows)))
    random.Random(seed).shuffle(indices)
    cut = round(len(indices) * 0.75)
    return np.asarray(indices[:cut]), np.asarray(indices[cut:])


if __name__ == "__main__":
    from cipherscope.datasets.synthetic import generate_demo

    data = Path("data/demo_flows.jsonl")
    if not data.exists():
        generate_demo(data)
    result = run_evaluation(data, "output/reports/synthetic-evaluation.json")
    print(json.dumps(result, indent=2))
