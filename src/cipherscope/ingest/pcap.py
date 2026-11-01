from __future__ import annotations

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
    """Stream packet headers and sizes only; payload bytes are never inspected.

    A TCP flow closes on RST, once both directions have sent FIN and the linger
    window has passed, or on the idle/active timeouts. Trailing ACKs stay in the
    same flow instead of starting a spurious one-packet flow.
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
    )
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
        reader.close()
    except (OSError, ValueError, EOFError) as exc:
        raise PcapIngestError(f"Could not read capture {source.name}: {exc}") from exc
    return assembler.finish()
