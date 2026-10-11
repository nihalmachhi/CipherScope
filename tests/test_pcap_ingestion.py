from __future__ import annotations

from scapy.all import IP, TCP, Raw, wrpcap

from cipherscope.ingest.pcap import read_pcap
from cipherscope.store.jsonl import serialize_flow


def test_offline_capture_keeps_only_hashed_metadata(tmp_path) -> None:
    capture = tmp_path / "authorized-lab.pcap"
    packet = (
        IP(src="192.0.2.11", dst="198.51.100.9")
        / TCP(sport=42000, dport=443, flags="PA")
        / Raw(b"demo payload must not be retained")
    )
    packet.time = 1000.0
    wrpcap(str(capture), [packet])
    flows = read_pcap(capture, capture_id="lab-capture", environment="lab", label="web")
    assert len(flows) == 1
    record = serialize_flow(flows[0])
    rendered = str(record)
    assert "192.0.2.11" not in rendered
    assert "198.51.100.9" not in rendered
    assert "42000" not in rendered
    assert "demo payload" not in rendered
    assert record["host_hash"].startswith("h:")
    assert "features" in record and "config_hash" in record
