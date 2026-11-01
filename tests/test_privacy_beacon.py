from __future__ import annotations

import pytest

from cipherscope.features.beacon import detect_beacons, periodicity_score
from cipherscope.privacy.hashing import (
    InsecureSaltError,
    hash_identifier,
    salt_fingerprint,
)


def test_beacon_periodicity_rewards_regular_intervals() -> None:
    regular = periodicity_score([float(i * 30) for i in range(7)])
    irregular = periodicity_score([0, 3, 19, 24, 91, 99, 120])
    assert regular["period_s"] == 30
    assert regular["score"] > irregular["score"]


def test_identifiers_are_keyed_hashes() -> None:
    first = hash_identifier("192.0.2.14", "key-one-long-enough")
    second = hash_identifier("192.0.2.14", "key-two-long-enough")
    assert first.startswith("h:") and len(first) == 26
    assert first != second
    assert "192.0.2.14" not in first


def test_missing_salt_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """P0-2 regression: no silent default salt."""
    monkeypatch.delenv("CIPHERSCOPE_HASH_SALT", raising=False)
    with pytest.raises(InsecureSaltError):
        hash_identifier("192.0.2.15")


@pytest.mark.parametrize(
    "salt",
    ["short", "local-demo-salt-change-me", "replace-with-a-private-random-salt"],
)
def test_weak_or_placeholder_salt_is_rejected(salt: str) -> None:
    with pytest.raises(InsecureSaltError):
        hash_identifier("192.0.2.16", salt)


def test_salt_fingerprint_identifies_without_revealing() -> None:
    first = salt_fingerprint("a" * 24)
    second = salt_fingerprint("b" * 24)
    assert first != second
    assert "a" * 24 not in first
    assert first == salt_fingerprint("a" * 24)


def test_beacon_grouping_is_symmetric() -> None:
    flows = [
        {
            "host_hash": "h:alpha" if index % 2 else "h:beta",
            "peer_hash": "h:beta" if index % 2 else "h:alpha",
            "started_at": float(index * 30),
        }
        for index in range(6)
    ]
    alerts = detect_beacons(flows, min_connections=4)
    assert len(alerts) == 1
    assert alerts[0]["connections"] == 6
    assert alerts[0]["score"] >= 0.75


def test_beacon_threshold_can_suppress_alerts() -> None:
    jittery = [
        {
            "host_hash": "h:one",
            "peer_hash": "h:two",
            "started_at": float(index * 30 + (index % 3) * 12),
        }
        for index in range(8)
    ]
    assert detect_beacons(jittery, threshold=0.99) == []
