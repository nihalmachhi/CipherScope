from __future__ import annotations

from typing import Any

import numpy as np


class SplitLeakageError(ValueError):
    """Raised when a supposedly held-out split shares a group across partitions."""


def assert_group_disjoint(
    rows: list[dict[str, Any]], train: np.ndarray, test: np.ndarray, group: str
) -> None:
    left = {rows[int(index)][group] for index in train}
    right = {rows[int(index)][group] for index in test}
    overlap = left & right
    if overlap:
        raise SplitLeakageError(f"Split leaks {len(overlap)} {group} identifier(s)")


def by_session(
    rows: list[dict[str, Any]], test_fraction: float = 0.25, group: str = "session_id"
) -> tuple[np.ndarray, np.ndarray]:
    return _group_holdout(rows, test_fraction, group)


def by_host(
    rows: list[dict[str, Any]], test_fraction: float = 0.25
) -> tuple[np.ndarray, np.ndarray]:
    return _group_holdout(rows, test_fraction, "host_hash")


def by_capture(
    rows: list[dict[str, Any]], test_fraction: float = 0.25
) -> tuple[np.ndarray, np.ndarray]:
    return _group_holdout(rows, test_fraction, "capture_id")


def _group_holdout(
    rows: list[dict[str, Any]], test_fraction: float, group: str
) -> tuple[np.ndarray, np.ndarray]:
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1")
    groups = sorted({str(row[group]) for row in rows})
    if len(groups) < 2:
        raise ValueError(f"At least two {group} groups are required")
    test_groups = set(groups[-max(1, round(len(groups) * test_fraction)) :])
    train = np.array([i for i, row in enumerate(rows) if str(row[group]) not in test_groups])
    test = np.array([i for i, row in enumerate(rows) if str(row[group]) in test_groups])
    assert_group_disjoint(rows, train, test, group)
    return train, test


def by_time(
    rows: list[dict[str, Any]], test_fraction: float = 0.25
) -> tuple[np.ndarray, np.ndarray]:
    ordered = sorted(range(len(rows)), key=lambda i: float(rows[i]["started_at"]))
    cut = max(1, min(len(rows) - 1, round(len(rows) * (1 - test_fraction))))
    train, test = np.array(ordered[:cut]), np.array(ordered[cut:])
    if max(float(rows[int(i)]["started_at"]) for i in train) > min(
        float(rows[int(i)]["started_at"]) for i in test
    ):
        raise SplitLeakageError("Time split does not preserve chronology")
    return train, test


def by_dataset(
    rows: list[dict[str, Any]], train_dataset: str, test_dataset: str
) -> tuple[np.ndarray, np.ndarray]:
    train = np.array([i for i, row in enumerate(rows) if row["dataset"] == train_dataset])
    test = np.array([i for i, row in enumerate(rows) if row["dataset"] == test_dataset])
    if not len(train) or not len(test):
        raise ValueError("Both requested datasets must be present")
    return train, test


def leave_one_environment_out(
    rows: list[dict[str, Any]], environment: str
) -> tuple[np.ndarray, np.ndarray]:
    train = np.array([i for i, row in enumerate(rows) if row["environment"] != environment])
    test = np.array([i for i, row in enumerate(rows) if row["environment"] == environment])
    if not len(train) or not len(test):
        raise ValueError("Held-out environment and training environments must both be non-empty")
    return train, test
