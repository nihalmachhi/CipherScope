from cipherscope.features.beacon import periodicity_score
from cipherscope.privacy.hashing import hash_identifier


def test_beacon_periodicity_rewards_regular_intervals() -> None:
    regular = periodicity_score([float(i * 30) for i in range(7)])
    irregular = periodicity_score([0, 3, 19, 24, 91, 99, 120])
    assert regular["period_s"] == 30
    assert regular["score"] > irregular["score"]


def test_identifiers_are_keyed_hashes() -> None:
    first = hash_identifier("192.0.2.14", "key-one")
    second = hash_identifier("192.0.2.14", "key-two")
    assert first.startswith("h:") and len(first) == 26
    assert first != second
    assert "192.0.2.14" not in first
