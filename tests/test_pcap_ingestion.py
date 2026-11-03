from __future__ import annotations

from scapy.all import IP, TCP, Raw, wrpcap

from cipherscope.ingest.assembler import FlowAssembler, PacketHeader
from cipherscope.ingest.pcap import iter_pcap, read_pcap
from cipherscope.store.jsonl import serialize_flow

SALT = "unit-test-salt-long-enough"


def _packet(source: str, target: str, sport: int, dport: int, flags: str, when: float):
    packet = IP(src=source, dst=target) / TCP(sport=sport, dport=dport, flags=flags)
    packet.time = when
    return packet


def test_offline_capture_keeps_only_hashed_metadata(tmp_path) -> None:
    capture = tmp_path / "authorized-lab.pcap"
    packet = (
        IP(src="192.0.2.11", dst="198.51.100.9")
        / TCP(sport=42000, dport=443, flags="PA")
        / Raw(b"demo payload must not be retained")
    )
    packet.time = 1000.0
    wrpcap(str(capture), [packet])
    flows = read_pcap(capture, capture_id="lab-capture", environment="lab", label="web", salt=SALT)
    assert len(flows) == 1
    record = serialize_flow(flows[0])
    rendered = str(record)
    assert "192.0.2.11" not in rendered
    assert "198.51.100.9" not in rendered
    assert "42000" not in rendered
    assert "demo payload" not in rendered
    assert record["host_hash"].startswith("h:")
    assert "features" in record and "config_hash" in record


def test_tcp_close_handshake_stays_one_flow(tmp_path) -> None:
    """P0-1 regression: the peer FIN and trailing ACK must not start new flows."""
    capture = tmp_path / "fin-handshake.pcap"
    client, server = "192.0.2.20", "198.51.100.20"
    exchange = [
        _packet(client, server, 51000, 443, "S", 1000.0),
        _packet(server, client, 443, 51000, "SA", 1000.1),
        _packet(client, server, 51000, 443, "A", 1000.2),
        _packet(client, server, 51000, 443, "PA", 1000.3),
        _packet(server, client, 443, 51000, "A", 1000.4),
        _packet(client, server, 51000, 443, "FA", 1000.5),
        _packet(server, client, 443, 51000, "A", 1000.6),
        _packet(server, client, 443, 51000, "FA", 1000.7),
        _packet(client, server, 51000, 443, "A", 1000.8),
    ]
    wrpcap(str(capture), exchange)
    flows = read_pcap(capture, capture_id="fin-lab", environment="lab", salt=SALT)
    assert len(flows) == 1
    assert len(flows[0].packets) == len(exchange)


def test_rst_closes_flow_immediately(tmp_path) -> None:
    capture = tmp_path / "rst.pcap"
    client, server = "192.0.2.21", "198.51.100.21"
    exchange = [
        _packet(client, server, 51001, 443, "S", 2000.0),
        _packet(server, client, 443, 51001, "RA", 2000.1),
        _packet(client, server, 51002, 443, "S", 2001.0),
        _packet(server, client, 443, 51002, "SA", 2001.1),
    ]
    wrpcap(str(capture), exchange)
    flows = read_pcap(capture, capture_id="rst-lab", environment="lab", salt=SALT)
    assert len(flows) == 2
    assert len(flows[0].packets) == 2


def test_pcap_iterator_yields_closed_flows_before_capture_ends(tmp_path) -> None:
    capture = tmp_path / "stream.pcap"
    a, b = "192.0.2.31", "198.51.100.31"
    wrpcap(
        str(capture),
        [
            _packet(a, b, 52000, 443, "S", 100.0),
            _packet(b, a, 443, 52000, "RA", 100.1),
            _packet(a, b, 52001, 443, "S", 101.0),
        ],
    )
    iterator = iter_pcap(capture, capture_id="stream", environment="lab", salt=SALT)
    first = next(iterator)
    assert len(first.packets) == 2
    assert len(list(iterator)) == 1


def test_assembler_caps_active_flows_and_emits_evictions() -> None:
    assembler = FlowAssembler(
        capture_id="bounded", environment="lab", salt=SALT, max_active_flows=1
    )
    assembler.add(PacketHeader(1.0, "192.0.2.40", "198.51.100.40", 53000, 443, "tcp", 60))
    assembler.add(PacketHeader(2.0, "192.0.2.41", "198.51.100.41", 53001, 443, "tcp", 60))
    assert len(assembler._states) == 1
    completed = assembler.drain_completed()
    assert len(completed) == 1
    assert len(completed[0].packets) == 1
