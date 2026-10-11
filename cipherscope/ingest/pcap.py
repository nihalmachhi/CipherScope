from __future__ import annotations

import json
from pathlib import Path

from scapy.all import IP, TCP, UDP, IPv6, PcapReader

from cipherscope.flows.schema import FlowRecord, PacketRecord
from cipherscope.privacy.hashing import hash_identifier


class PcapIngestError(ValueError):
    """Raised when the capture cannot be read as an offline packet trace."""


def read_pcap(
    path: str | Path,
    *,
    capture_id: str,
    environment: str,
    label: str | None = None,
    idle_timeout_s: float = 120.0,
    active_timeout_s: float = 1800.0,
) -> list[FlowRecord]:
    """Read packet headers and sizes only; payload bytes are never persisted or inspected."""
    path = Path(path)
    if path.suffix.lower() not in {".pcap", ".pcapng", ".cap"}:
        raise PcapIngestError("Only offline pcap/pcapng files are accepted")
    active: dict[tuple[str, str, int, int, str], FlowRecord] = {}
    completed: list[FlowRecord] = []
    try:
        reader = PcapReader(str(path))
        for packet in reader:
            if not (packet.haslayer(IP) or packet.haslayer(IPv6)):
                continue
            network = packet[IP] if packet.haslayer(IP) else packet[IPv6]
            if packet.haslayer(TCP):
                transport, protocol = packet[TCP], "tcp"
                source_port, dest_port = int(transport.sport), int(transport.dport)
                flags = int(transport.flags)
            elif packet.haslayer(UDP):
                transport, protocol = packet[UDP], "udp"
                source_port, dest_port, flags = int(transport.sport), int(transport.dport), 0
            else:
                continue
            source, target = str(network.src), str(network.dst)
            forward = (source, target, source_port, dest_port, protocol)
            reverse = (target, source, dest_port, source_port, protocol)
            timestamp = float(packet.time)
            flow = active.get(forward) or active.get(reverse)
            if (
                flow is None
                or timestamp - flow.started_at >= active_timeout_s
                or (flow.packets and timestamp - flow.packets[-1].timestamp >= idle_timeout_s)
            ):
                if flow:
                    flow.completed_at = flow.packets[-1].timestamp
                    active.pop(forward, None)
                    active.pop(reverse, None)
                    completed.append(flow)
                flow_id = hash_identifier(
                    f"{capture_id}:{source}:{source_port}:{target}:{dest_port}:{timestamp}"
                )
                flow = FlowRecord(
                    flow_id,
                    hash_identifier(source),
                    hash_identifier(target),
                    capture_id,
                    environment,
                    label,
                    timestamp,
                    protocol,
                )
                active[forward] = flow
                active[reverse] = flow
            direction = 1 if flow.host_hash == hash_identifier(source) else -1
            flow.packets.append(
                PacketRecord(timestamp, min(int(len(packet)), 65535), direction, flags)
            )
            if protocol == "tcp" and (flags & 0x05):
                flow.completed_at = timestamp
                active.pop(forward, None)
                active.pop(reverse, None)
                completed.append(flow)
        reader.close()
    except (OSError, ValueError, EOFError) as exc:
        raise PcapIngestError(f"Could not read capture {path.name}: {exc}") from exc
    for flow in active.values():
        flow.completed_at = flow.packets[-1].timestamp if flow.packets else flow.started_at
        completed.append(flow)
    unique = {flow.flow_id: flow for flow in completed}
    return list(unique.values())


def write_metadata_jsonl(flows: list[FlowRecord], output: str | Path) -> int:
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as stream:
        for flow in flows:
            stream.write(json.dumps(flow.metadata(), sort_keys=True) + "\n")
    return len(flows)
