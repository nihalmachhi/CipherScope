from __future__ import annotations

import pytest

from cipherscope.splits.strategies import (
    SplitLeakageError,
    assert_group_disjoint,
    by_capture,
    by_dataset,
    by_host,
    by_session,
    by_time,
    capture_kfold,
    leave_one_environment_out_folds,
)


@pytest.fixture
def rows() -> list[dict[str, str | float]]:
    environments = ("lab-alpha", "lab-beta", "lab-gamma")
    return [
        {
            "session_id": f"s{i}",
            "host_hash": f"h{i // 2}",
            "capture_id": f"cap{i // 4}",
            "dataset": "campaign-1" if i < 12 else "campaign-2",
            "environment": environments[i % 3],
            "started_at": float(i),
        }
        for i in range(24)
    ]


def test_group_splitters_are_disjoint(rows) -> None:
    for splitter, group in (
        (by_session, "session_id"),
        (by_host, "host_hash"),
        (by_capture, "capture_id"),
    ):
        train, test = splitter(rows)
        assert_group_disjoint(rows, train, test, group)


def test_group_leak_is_rejected(rows) -> None:
    with pytest.raises(SplitLeakageError):
        assert_group_disjoint(
            rows,
            train=[0, 1, 2, 3],
            test=[0, 4],
            group="session_id",
        )


def test_cross_dataset_split_differs_from_environment_folds(rows) -> None:
    """P0-3 regression: S4 and S5 must not be the same split."""
    _, dataset_test = by_dataset(rows, "campaign-1", "campaign-2")
    folds = leave_one_environment_out_folds(rows)
    assert len(folds) == 3
    dataset_test_indices = set(dataset_test.tolist())
    pooled_environment_test: set[int] = set()
    for _, fold_test in folds.values():
        fold_indices = set(fold_test.tolist())
        pooled_environment_test |= fold_indices
        assert fold_indices != dataset_test_indices
    assert pooled_environment_test != dataset_test_indices


def test_time_split_preserves_chronology(rows) -> None:
    train, test = by_time(rows)
    assert max(float(rows[int(index)]["started_at"]) for index in train) <= min(
        float(rows[int(index)]["started_at"]) for index in test
    )


def test_capture_kfold_keeps_every_capture_in_exactly_one_test_fold(rows) -> None:
    folds = capture_kfold(rows, n_splits=4)
    assert len(folds) == 4
    tested: list[str] = []
    for train, test in folds.values():
        assert_group_disjoint(rows, train, test, "capture_id")
        tested.extend(str(rows[int(index)]["capture_id"]) for index in test)
    assert sorted(tested) == sorted(str(row["capture_id"]) for row in rows)
