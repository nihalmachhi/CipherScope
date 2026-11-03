from __future__ import annotations

from pathlib import Path

import pytest

from cipherscope.ingest.zeek import read_zeek_conn_log

FIXTURES = Path(__file__).parent / "fixtures"


def test_zeek_conn_log_normalizes_metadata_without_raw_addresses() -> None:
    flows = read_zeek_conn_log(
        FIXTURES / "zeek_conn.log",
        capture_id="zeek-fixture",
        environment="lab-alpha",
        label="benign",
        salt="zeek-test-salt-long-enough",
    )
    assert len(flows) == 1
    flow = flows[0]
    assert flow.dataset == "zeek"
    assert flow.bytes_total == 3600
    assert flow.duration_s == 1.25
    assert flow.host_hash.startswith("h:")
    assert "192.0.2.10" not in flow.host_hash


def test_zeek_conn_log_requires_fields_header(tmp_path: Path) -> None:
    source = tmp_path / "bad.log"
    source.write_text("1700000000\t192.0.2.1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no #fields header"):
        read_zeek_conn_log(
            source,
            capture_id="bad",
            environment="lab",
            salt="zeek-test-salt-long-enough",
        )
