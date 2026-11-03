from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from scapy.all import (  # type: ignore[attr-defined]
    IP,
    TCP,
    UDP,
    IPv6,
    PcapReader,
)

from cipherscope.flows.schema import FlowRecord
from cipherscope.ingest.assembler import FlowAssembler, PacketHeader

SUPPORTED_SUFFIXES = {".pcap", ".pcapng", ".cap"}


class PcapIngestError(ValueError):
    """Raised when the capture cannot be read as an offline packet trace."""


def read_pcap(
    path: str | Path,
    *,
    capture_id: str,
    environment: str,
    dataset: str | None = None,
    label: str | None = None,
    salt: str | None = None,
    idle_timeout_s: float = 120.0,
    active_timeout_s: float = 1800.0,
    fin_linger_s: float = 5.0,
) -> list[FlowRecord]:
    """Read an offline capture into memory for callers that need a list."""
    return list(
        iter_pcap(
            path,
            capture_id=capture_id,
            environment=environment,
            dataset=dataset,
            label=label,
            salt=salt,
            idle_timeout_s=idle_timeout_s,
            active_timeout_s=active_timeout_s,
            fin_linger_s=fin_linger_s,
        )
    )


def iter_pcap(
    path: str | Path,
    *,
    capture_id: str,
    environment: str,
    dataset: str | None = None,
    label: str | None = None,
    salt: str | None = None,
    idle_timeout_s: float = 120.0,
    active_timeout_s: float = 1800.0,
    fin_linger_s: float = 5.0,
    max_active_flows: int = 100_000,
) -> Iterator[FlowRecord]:
    """Yield completed flows while reading packet headers one at a time.

    A TCP flow closes on RST, once both directions have sent FIN and the linger
    window has passed, or on the idle/active timeouts. Trailing ACKs stay in the
    same flow instead of starting a spurious one-packet flow. The active-flow
    limit and drained completion buffer bound working memory independently of
    the total capture size.
    """
    source = Path(path)
    if source.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise PcapIngestError("Only offline pcap/pcapng files are accepted")

    assembler = FlowAssembler(
        capture_id=capture_id,
        environment=environment,
        dataset=dataset,
        label=label,
        salt=salt,
        idle_timeout_s=idle_timeout_s,
        active_timeout_s=active_timeout_s,
        fin_linger_s=fin_linger_s,
        max_active_flows=max_active_flows,
    )
    reader = None
    try:
        reader = PcapReader(str(source))
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
            assembler.add(
                PacketHeader(
                    timestamp=float(packet.time),
                    source=str(network.src),
                    target=str(network.dst),
                    source_port=source_port,
                    dest_port=dest_port,
                    protocol=protocol,
                    size=int(len(packet)),
                    tcp_flags=flags,
                )
            )
            yield from assembler.drain_completed()
    except (OSError, ValueError, EOFError) as exc:
        raise PcapIngestError(f"Could not read capture {source.name}: {exc}") from exc
    finally:
        if reader is not None:
            reader.close()
    yield from assembler.finish()
