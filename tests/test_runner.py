from __future__ import annotations

from pathlib import Path

import yaml

from cipherscope.datasets.synthetic import ENVIRONMENTS, generate_demo
from cipherscope.eval.runner import run_evaluation

SALT = "runner-test-salt-long-enough"


def test_report_covers_seeds_splits_and_metadata(tmp_path: Path) -> None:
    data_path = tmp_path / "flows.jsonl"
    generate_demo(data_path, seed=13, flows_per_environment=36, salt=SALT)
    config = {
        "experiment": "test-baseline",
        "seed": 7,
        "seeds": [7, 13],
        "data": {
            "input": str(data_path),
            "train_dataset": "campaign-1",
            "test_dataset": "campaign-2",
        },
        "models": {"primary": "random_forest", "compare": ["random_forest", "logreg"]},
        "robustness": {"padding": [0.3], "jitter_s": [0.2], "truncation": [8]},
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    report_path = tmp_path / "report.json"

    report = run_evaluation(data_path, report_path, config_path=config_path, seeds=[7, 13])

    assert report_path.exists()
    assert report["data_kind"] == "synthetic"
    assert report["metadata"]["seeds"] == [7, 13]
    assert report["metadata"]["config_hash"]
    assert "git_sha" in report["metadata"]
    assert "python" in report["metadata"]["library_versions"]
    assert set(report["splits"]) == {
        "S1_random_caution_only",
        "S2_grouped_host",
        "S3_time_forward",
        "S4_cross_dataset",
        "S5_leave_one_environment_out",
        "S6_capture_holdout",
    }
    folds = report["splits"]["S5_leave_one_environment_out"]["folds"]
    assert set(folds) == set(ENVIRONMENTS)
    summary = report["splits"]["S4_cross_dataset"]["summary"]["macro_f1"]
    assert set(summary) == {"mean", "std", "values", "seed_bootstrap_ci"}
    assert len(summary["values"]) == 2
    assert "bootstrap_macro_f1" in report["splits"]["S4_cross_dataset"]
    assert report["robustness"]["clean"]["macro_f1"] >= 0.0
    assert "clean" in report["robustness"]


def test_cross_dataset_and_environment_splits_differ(tmp_path: Path) -> None:
    data_path = tmp_path / "flows.jsonl"
    generate_demo(data_path, seed=13, flows_per_environment=36, salt=SALT)
    config = {
        "experiment": "test-baseline",
        "seed": 7,
        "seeds": [7],
        "data": {
            "input": str(data_path),
            "train_dataset": "campaign-1",
            "test_dataset": "campaign-2",
        },
        "models": {"primary": "random_forest", "compare": ["random_forest"]},
        "robustness": {"padding": [0.3], "jitter_s": [0.2], "truncation": [8]},
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    report = run_evaluation(data_path, tmp_path / "report.json", config_path=config_path, seeds=[7])
    cross_dataset = report["splits"]["S4_cross_dataset"]
    leave_one_out = report["splits"]["S5_leave_one_environment_out"]
    assert cross_dataset["test_rows"] < leave_one_out["pooled"]["per_seed"]["7"]["rows"]
