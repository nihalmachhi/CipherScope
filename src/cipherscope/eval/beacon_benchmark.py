from __future__ import annotations

from typing import Any

import numpy as np

from cipherscope.features.beacon import detect_beacons

JITTER_LEVELS = (0.0, 0.15, 0.30, 0.50)


def evaluate_synthetic_beacons(seed: int = 21) -> dict[str, Any]:
    """Measure the beacon heuristic on seeded callbacks and polling hard negatives."""
    results: dict[str, Any] = {}
    for jitter in JITTER_LEVELS:
        rng = np.random.default_rng(seed)
        flows: list[dict[str, Any]] = []
        truth: dict[tuple[str, str], bool] = {}
        for label, count in (("beacon", 8), ("polling", 8), ("irregular", 8)):
            for group_index in range(count):
                host = f"h:{label}-{group_index}"
                peer = f"h:peer-{group_index}"
                key = (min(host, peer), max(host, peer))
                truth[key] = label == "beacon"
                started = float(group_index * 10_000)
                clock = started
                for _ in range(8):
                    flows.append({"host_hash": host, "peer_hash": peer, "started_at": clock})
                    if label == "beacon":
                        clock += float(30 * (1 + rng.uniform(-jitter, jitter)))
                    elif label == "polling":
                        clock += float(30 * (1 + rng.uniform(-0.2, 0.2)))
                    else:
                        clock += float(rng.uniform(4, 90))

        predictions = {
            (
                min(str(alert["host_hash"]), str(alert["peer_hash"])),
                max(str(alert["host_hash"]), str(alert["peer_hash"])),
            )
            for alert in detect_beacons(flows)
        }
        true_positive = sum(truth.get(key, False) for key in predictions)
        false_positive = sum(not truth.get(key, False) for key in predictions)
        false_negative = sum(label and key not in predictions for key, label in truth.items())
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        results[f"jitter_{int(jitter * 100)}pct"] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "true_positive": true_positive,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "groups": len(truth),
        }
    return {
        "data_kind": "synthetic scripted callbacks and polling hard negatives",
        "seed": seed,
        "results": results,
        "limitation": (
            "Generated timing traces are a detector smoke benchmark, not real-world evidence."
        ),
    }
