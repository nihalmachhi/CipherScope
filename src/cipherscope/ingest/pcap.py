from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from scapy.all import (  # type: ignore[attr-defined]
    IP,
    TCP,
    UDP,
    IPv6,
    PcapReader,
)

from cipherscope.flows.schema import FlowRecord, PacketRecord
from cipherscope.privacy.hashing import hash_identifier

FIN = 0x01
RST = 0x04
SUPPORTED_SUFFIXES = {".pcap", ".pcapng", ".cap"}


class PcapIngestError(ValueError):
    """Raised when the capture cannot be read as an offline packet trace."""


@dataclass
class _FlowState:
    """Assembler state for one bidirectional flow."""

    flow: FlowRecord
    source: str
    keys: tuple[tuple[str, str, int, int, str], ...]
    fin_directions: set[int] = field(default_factory=set)
    both_fin_at: float | None = None


def _close(state: _FlowState, active: dict[tuple[str, str, int, int, str], _FlowState]) -> None:
    last = state.flow.packets[-1].timestamp if state.flow.packets else state.flow.started_at
    state.flow.completed_at = last
    for key in state.keys:
        active.pop(key, None)


def read_pcap(
    path: str | Path,
    *,
    capture_id: str,
    environment: str,
    label: str | None = None,
    salt: str | None = None,
    idle_timeout_s: float = 120.0,
    active_timeout_s: float = 1800.0,
    fin_linger_s: float = 5.0,
) -> list[FlowRecord]:
    """Read packet headers and sizes only; payload bytes are never inspected.

    A TCP flow closes on RST, once both directions have sent FIN and the linger
    window has passed, or on the idle/active timeouts. Trailing ACKs stay in the
    same flow instead of starting a spurious one-packet flow.
    """
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise PcapIngestError("Only offline pcap/pcapng files are accepted")

    pseudonyms: dict[str, str] = {}

    def pseudonym(value: str) -> str:
        cached = pseudonyms.get(value)
        if cached is None:
            cached = pseudonyms[value] = hash_identifier(value, salt)
        return cached

    active: dict[tuple[str, str, int, int, str], _FlowState] = {}
    completed: list[FlowRecord] = []
    try:
        reader = PcapReader(str(path))
        for packet in reader:
            if not (packet.haslayer(IP) or packet.haslayer(IPv6)):
                continue
            network = packet[IP] if packet.haslayer(IP) else packet[IPv6]
            if packet.haslayer(TCP):
                transport = packet[TCP]
                protocol = "tcp"
                source_port, dest_port = int(transport.sport), int(transport.dport)
                flags = int(transport.flags)
            elif packet.haslayer(UDP):
                transport = packet[UDP]
                protocol = "udp"
                source_port, dest_port, flags = int(transport.sport), int(transport.dport), 0
            else:
                continue

            source, target = str(network.src), str(network.dst)
            forward = (source, target, source_port, dest_port, protocol)
            reverse = (target, source, dest_port, source_port, protocol)
            timestamp = float(packet.time)

            state = active.get(forward) or active.get(reverse)
            if state is not None:
                last_seen = state.flow.packets[-1].timestamp if state.flow.packets else timestamp
                expired = (
                    timestamp - state.flow.started_at >= active_timeout_s
                    or timestamp - last_seen >= idle_timeout_s
                    or (
                        state.both_fin_at is not None
                        and timestamp - state.both_fin_at >= fin_linger_s
                    )
                )
                if expired:
                    _close(state, active)
                    state = None

            if state is None:
                state = _FlowState(
                    flow=FlowRecord(
                        flow_id=pseudonym(f"{capture_id}:{forward}:{timestamp:.6f}"),
                        host_hash=pseudonym(source),
                        peer_hash=pseudonym(target),
                        capture_id=capture_id,
                        environment=environment,
                        label=label,
                        started_at=timestamp,
                        protocol=protocol,
                    ),
                    source=source,
                    keys=(forward, reverse),
                )
                active[forward] = state
                active[reverse] = state

            direction = 1 if source == state.source else -1
            state.flow.packets.append(
                PacketRecord(timestamp, min(int(len(packet)), 65535), direction, flags)
            )

            if protocol != "tcp":
                continue
            if flags & RST:
                _close(state, active)
                completed.append(state.flow)
                continue
            if flags & FIN:
                state.fin_directions.add(direction)
                if len(state.fin_directions) >= 2 and state.both_fin_at is None:
                    state.both_fin_at = timestamp
        reader.close()
    except (OSError, ValueError, EOFError) as exc:
        raise PcapIngestError(f"Could not read capture {path.name}: {exc}") from exc

    for state in {id(state): state for state in active.values()}.values():
        _close(state, active)
        completed.append(state.flow)

    unique = {flow.flow_id: flow for flow in completed}
    return list(unique.values())


def write_metadata_jsonl(flows: list[FlowRecord], output: str | Path) -> int:
    """Write metadata-only flow records to JSONL without payload bytes."""
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as stream:
        for flow in flows:
            stream.write(json.dumps(flow.metadata(), sort_keys=True) + "\n")
    return len(flows)
