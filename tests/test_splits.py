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
    leave_one_environment_out,
)


@pytest.fixture
def rows() -> list[dict[str, str | float]]:
    return [
        {
            "session_id": f"s{i}",
            "host_hash": f"h{i // 2}",
            "capture_id": f"cap{i // 4}",
            "dataset": "A" if i < 8 else "B",
            "environment": "A" if i < 8 else "B",
            "started_at": float(i),
        }
        for i in range(16)
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
        assert_group_disjoint(rows, [0, 1], [1, 2], "session_id")


def test_time_split_is_chronological(rows) -> None:
    train, test = by_time(rows)
    assert max(rows[int(i)]["started_at"] for i in train) < min(
        rows[int(i)]["started_at"] for i in test
    )


def test_dataset_and_environment_holdouts(rows) -> None:
    train, test = by_dataset(rows, "A", "B")
    assert {rows[int(i)]["dataset"] for i in train} == {"A"}
    assert {rows[int(i)]["dataset"] for i in test} == {"B"}
    train, test = leave_one_environment_out(rows, "B")
    assert {rows[int(i)]["environment"] for i in train} == {"A"}
    assert {rows[int(i)]["environment"] for i in test} == {"B"}
