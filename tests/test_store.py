from __future__ import annotations

import json

import pytest

from cipherscope.flows.schema import FlowRecord, PacketRecord
from cipherscope.store.jsonl import (
    SchemaVersionError,
    load_rows,
    serialize_flow,
    validate_row,
    write_feature_jsonl,
)


def sample_flow() -> FlowRecord:
    packets = [
        PacketRecord(10.0, 300, 1, 2),
        PacketRecord(10.2, 900, -1, 16),
        PacketRecord(10.4, 200, 1, 24),
    ]
    return FlowRecord(
        flow_id="h:flow",
        host_hash="h:host",
        peer_hash="h:peer",
        capture_id="h:capture",
        environment="lab-alpha",
        label="web",
        started_at=10.0,
        protocol="tcp",
        packets=packets,
        completed_at=10.4,
        session_id="h:session",
        dataset="campaign-1",
    )


def test_round_trip_validates_schema(tmp_path) -> None:
    path = tmp_path / "flows.jsonl"
    write_feature_jsonl([sample_flow()], path)
    rows = load_rows(path)
    assert len(rows) == 1
    assert rows[0]["bytes_total"] == 1400
    assert rows[0]["session_id"] == "h:session"
    assert rows[0]["dataset"] == "campaign-1"


def test_unknown_schema_version_is_rejected(tmp_path) -> None:
    """P2-3 regression: a future schema must fail with a clear error."""
    row = serialize_flow(sample_flow())
    row["schema_version"] = "99.0.0"
    path = tmp_path / "flows.jsonl"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(SchemaVersionError, match="Unsupported schema_version"):
        load_rows(path)


def test_invalid_row_is_rejected() -> None:
    row = serialize_flow(sample_flow())
    row["packets"][0]["direction"] = 5
    with pytest.raises(SchemaVersionError, match="Invalid stored row"):
        validate_row(row)
