from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, cast

import numpy as np
import yaml
from sklearn.metrics import f1_score

from cipherscope.eval.bootstrap import bootstrap_ci
from cipherscope.eval.metrics import evaluate_predictions, pooled_predictions
from cipherscope.eval.report import build_metadata
from cipherscope.features.tabular import extract_tabular
from cipherscope.flows.schema import FlowRecord
from cipherscope.models.base import feature_names, train
from cipherscope.privacy.hashing import InsecureSaltError, salt_fingerprint
from cipherscope.robustness.perturb import perturb_padding, perturb_timing, truncate_packets
from cipherscope.splits.strategies import (
    by_capture,
    by_dataset,
    by_host,
    by_time,
    leave_one_environment_out_folds,
)
from cipherscope.store.jsonl import load_rows

DEFAULT_CONFIG = Path("configs/synthetic-baseline.yaml")
SUMMARY_METRICS = (
    "macro_f1",
    "accuracy",
    "beacon_pr_auc",
    "beacon_fpr_at_90_recall",
    "calibration_ece",
)
SYNTHETIC_PREFIXES = ("lab-", "campaign-")


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict[str, Any]:
    """Load the YAML experiment configuration that drives the runner."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Experiment config not found: {source}")
    return cast(dict[str, Any], yaml.safe_load(source.read_text(encoding="utf-8")))


def _random_split(rows: list[dict[str, Any]], seed: int) -> tuple[np.ndarray, np.ndarray]:
    indices = list(range(len(rows)))
    random.Random(seed).shuffle(indices)
    cut = round(len(indices) * 0.75)
    return np.asarray(indices[:cut]), np.asarray(indices[cut:])


def _bootstrap_macro_f1(
    truth: np.ndarray, prediction: np.ndarray, seed: int, resamples: int = 1000
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    scores = np.array(
        [
            f1_score(
                truth[index],
                prediction[index],
                average="macro",
                zero_division=0,
            )
            for index in (rng.integers(0, len(truth), len(truth)) for _ in range(resamples))
        ]
    )
    return {
        "low": float(np.quantile(scores, 0.025)),
        "high": float(np.quantile(scores, 0.975)),
        "confidence": 0.95,
        "resamples": resamples,
    }


def _summarize(per_seed: dict[int, dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for metric in SUMMARY_METRICS:
        values = [result[metric] for result in per_seed.values() if result.get(metric) is not None]
        if not values:
            continue
        array = np.asarray(values, dtype=float)
        summary[metric] = {
            "mean": float(array.mean()),
            "std": float(array.std(ddof=1)) if array.size > 1 else 0.0,
            "values": array.tolist(),
            "seed_bootstrap_ci": bootstrap_ci(array),
        }
    return summary


def _score_pair(
    rows: list[dict[str, Any]],
    names: list[str],
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    family: str,
    seeds: list[int],
) -> tuple[dict[str, Any], list[tuple[np.ndarray, np.ndarray, np.ndarray]]]:
    per_seed: dict[int, dict[str, Any]] = {}
    parts: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    classes: list[str] = []
    for seed in seeds:
        trained = train(rows, train_idx, names, family, seed)
        test_rows = [rows[int(index)] for index in test_idx]
        truth = trained.encoder.transform([str(row["label"]) for row in test_rows])
        probabilities = trained.predict_proba(test_rows)
        prediction = trained.predict(test_rows)
        classes = trained.encoder.classes_.tolist()
        per_seed[seed] = evaluate_predictions(truth, prediction, probabilities, classes)
        parts.append((truth, prediction, probabilities))
    result: dict[str, Any] = {
        "train_rows": int(len(train_idx)),
        "test_rows": int(len(test_idx)),
        "per_seed": {str(seed): metrics for seed, metrics in per_seed.items()},
        "summary": _summarize(per_seed),
    }
    first = parts[0]
    result["bootstrap_macro_f1"] = _bootstrap_macro_f1(first[0], first[1], seeds[0])
    return result, parts


def _evaluate_pair(
    rows: list[dict[str, Any]],
    names: list[str],
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    family: str,
    seeds: list[int],
) -> dict[str, Any]:
    result, _ = _score_pair(rows, names, train_idx, test_idx, family, seeds)
    return result


def _evaluate_folds(
    rows: list[dict[str, Any]],
    names: list[str],
    folds: dict[str, tuple[np.ndarray, np.ndarray]],
    family: str,
    seeds: list[int],
) -> dict[str, Any]:
    fold_results: dict[str, Any] = {}
    pooled_parts: list[list[tuple[np.ndarray, np.ndarray, np.ndarray]]] = [[] for _ in seeds]
    for environment, (train_idx, test_idx) in folds.items():
        result, parts = _score_pair(rows, names, train_idx, test_idx, family, seeds)
        fold_results[environment] = result
        for seed_index, part in enumerate(parts):
            pooled_parts[seed_index].append(part)
    per_seed: dict[int, dict[str, Any]] = {}
    classes: list[str] = []
    for seed, parts in zip(seeds, pooled_parts, strict=True):
        truth, prediction, probabilities = pooled_predictions(parts)
        classes = sorted({str(row["label"]) for row in rows})
        per_seed[seed] = evaluate_predictions(truth, prediction, probabilities, classes)
    first = pooled_predictions(pooled_parts[0])
    return {
        "folds": fold_results,
        "pooled": {
            "per_seed": {str(seed): metrics for seed, metrics in per_seed.items()},
            "summary": _summarize(per_seed),
            "bootstrap_macro_f1": _bootstrap_macro_f1(first[0], first[1], seeds[0]),
        },
    }


def _robustness(
    rows: list[dict[str, Any]],
    names: list[str],
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    family: str,
    seed: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    trained = train(rows, train_idx, names, family, seed)
    test_rows = [rows[int(index)] for index in test_idx]
    truth = trained.encoder.transform([str(row["label"]) for row in test_rows])
    transforms: list[tuple[str, Any]] = [("clean", lambda row: row)]
    for level in config["robustness"]["padding"]:
        transforms.append(
            (
                f"padding_{int(level * 100)}pct",
                lambda row, level=level: perturb_padding(row, level, seed),
            )
        )
    for level in config["robustness"]["jitter_s"]:
        transforms.append(
            (
                f"jitter_{int(level * 1000)}ms",
                lambda row, level=level: perturb_timing(row, level, seed),
            )
        )
    for limit in config["robustness"]["truncation"]:
        transforms.append(
            (
                f"first_{limit}_packets",
                lambda row, limit=limit: truncate_packets(row, limit),
            )
        )
    results: dict[str, Any] = {}
    for name, transform in transforms:
        copies = [
            {**row, "features": extract_tabular(FlowRecord.from_row(transform(row)))}
            for row in test_rows
        ]
        prediction = trained.predict(copies)
        results[name] = {
            "macro_f1": float(f1_score(truth, prediction, average="macro", zero_division=0)),
            "accuracy": float(np.mean(prediction == truth)),
        }
    return results


def _model_comparison(
    rows: list[dict[str, Any]],
    names: list[str],
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    families: list[str],
    seed: int,
) -> dict[str, Any]:
    comparison: dict[str, Any] = {}
    for family in families:
        result = _evaluate_pair(rows, names, train_idx, test_idx, family, [seed])
        comparison[family] = {
            "macro_f1": result["summary"]["macro_f1"]["mean"],
            "accuracy": result["summary"]["accuracy"]["mean"],
            "calibration_ece": result["summary"]["calibration_ece"]["mean"],
        }
    return comparison


def _data_kind(rows: list[dict[str, Any]]) -> str:
    synthetic = all(
        str(row.get("environment", "")).startswith(SYNTHETIC_PREFIXES)
        or str(row.get("dataset", "")).startswith(SYNTHETIC_PREFIXES)
        for row in rows
    )
    return "synthetic" if synthetic else "external dataset"


def run_evaluation(
    dataset_path: str | Path,
    report_path: str | Path,
    config_path: str | Path | None = None,
    seeds: list[int] | None = None,
) -> dict[str, Any]:
    """Train every configured model and split, then write a reproducible report."""
    config = load_config(config_path or DEFAULT_CONFIG)
    seed_list = seeds or [int(value) for value in config["seeds"]]
    rows = load_rows(dataset_path)
    if not rows or any(not row.get("features") or not row.get("label") for row in rows):
        raise ValueError("Evaluation expects labeled rows with precomputed metadata features")
    names = feature_names(rows)
    family = str(config["models"]["primary"])
    data_config = config["data"]
    primary_split = by_dataset(
        rows, str(data_config["train_dataset"]), str(data_config["test_dataset"])
    )

    splits: dict[str, Any] = {
        "S1_random_caution_only": _evaluate_pair(
            rows, names, *_random_split(rows, seed_list[0]), family, seed_list
        ),
        "S2_grouped_host": _evaluate_pair(rows, names, *by_host(rows), family, seed_list),
        "S3_time_forward": _evaluate_pair(rows, names, *by_time(rows), family, seed_list),
        "S4_cross_dataset": _evaluate_pair(rows, names, *primary_split, family, seed_list),
        "S5_leave_one_environment_out": _evaluate_folds(
            rows, names, leave_one_environment_out_folds(rows), family, seed_list
        ),
        "S6_capture_holdout": _evaluate_pair(rows, names, *by_capture(rows), family, seed_list),
    }

    try:
        fingerprint = salt_fingerprint()
    except InsecureSaltError:
        fingerprint = None

    results: dict[str, Any] = {
        "report_schema_version": "2.0.0",
        "experiment": config["experiment"],
        "data_kind": _data_kind(rows),
        "data": {
            "rows": len(rows),
            "labels": {
                label: sum(1 for row in rows if row["label"] == label)
                for label in sorted({str(row["label"]) for row in rows})
            },
            "environments": sorted({str(row["environment"]) for row in rows}),
            "datasets": sorted({str(row["dataset"]) for row in rows}),
            "captures": len({str(row["capture_id"]) for row in rows}),
            "sessions": len({str(row["session_id"]) for row in rows}),
        },
        "features": len(names),
        "feature_names": names,
        "metadata": build_metadata(config, seed_list, fingerprint),
        "model_comparison": _model_comparison(
            rows,
            names,
            *primary_split,
            [str(item) for item in config["models"]["compare"]],
            seed_list[0],
        ),
        "splits": splits,
        "robustness": _robustness(rows, names, *primary_split, family, seed_list[0], config),
        "limitations": [
            "Synthetic data is labelled synthetic and only shows the pipeline runs.",
            "Scores come from generated traffic, not from real encrypted captures.",
            "No real-world detection or generalization claim is made.",
            "Real datasets require explicit licence acceptance and are never committed.",
        ],
    }
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def main() -> int:
    from cipherscope.datasets.synthetic import generate_demo

    config = load_config()
    data_path = Path(config["data"]["input"])
    if not data_path.exists():
        generate_demo(data_path)
    result = run_evaluation(data_path, "output/reports/synthetic-evaluation.json")
    summary = {
        name: split["summary"]["macro_f1"]["mean"]
        for name, split in result["splits"].items()
        if "summary" in split
    }
    summary["S5_leave_one_environment_out"] = result["splits"]["S5_leave_one_environment_out"][
        "pooled"
    ]["summary"]["macro_f1"]["mean"]
    print(json.dumps({"data_kind": result["data_kind"], "macro_f1": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
