from __future__ import annotations

from cipherscope.features.tabular import extract_sequence, extract_tabular
from cipherscope.flows.schema import FlowRecord, PacketRecord


def sample_flow() -> FlowRecord:
    packets = [
        PacketRecord(1.0, 400, 1, 2),
        PacketRecord(1.2, 700, -1, 16),
        PacketRecord(1.7, 220, 1, 24),
    ]
    return FlowRecord("flow-x", "h:a", "h:b", "cap-a", "lab", "web", 1.0, "tcp", packets, 1.7)


def test_features_exclude_identifiers_and_absolute_time() -> None:
    features = extract_tabular(sample_flow())
    assert features["packet_count"] == 3
    assert features["forward_bytes"] == 620
    assert features["reverse_bytes"] == 700
    assert not any(
        token in name.lower()
        for name in features
        for token in ("ip", "port", "mac", "timestamp", "absolute_time")
    )


def test_sequence_is_bounded_and_masked() -> None:
    tensor, mask = extract_sequence(sample_flow(), length=5)
    assert len(tensor) == len(mask) == 5
    assert sum(mask) == 3
    assert tensor[1][0] < 0
    assert mask[-1] is False
