from __future__ import annotations

import csv
from pathlib import Path

from cipherscope.flows.schema import FlowRecord
from cipherscope.ingest.assembler import FlowAssembler, PacketHeader

REQUIRED_COLUMNS = frozenset(
    {"timestamp", "src_ip", "dst_ip", "src_port", "dst_port", "protocol", "length"}
)


class CsvIngestError(ValueError):
    """Raised when a packet-level CSV does not match the documented schema."""


def read_packet_csv(
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
    """Read a packet-level CSV with the documented metadata columns only."""
    source = Path(path)
    if source.suffix.lower() != ".csv":
        raise CsvIngestError("Expected a .csv packet export")
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
        with source.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise CsvIngestError(
                    f"{source.name} is missing required columns: {sorted(missing)}"
                )
            for line_number, row in enumerate(reader, start=2):
                try:
                    header = PacketHeader(
                        timestamp=float(row["timestamp"]),
                        source=row["src_ip"].strip(),
                        target=row["dst_ip"].strip(),
                        source_port=int(row["src_port"]),
                        dest_port=int(row["dst_port"]),
                        protocol=row["protocol"].strip().lower(),
                        size=int(row["length"]),
                        tcp_flags=int(row.get("tcp_flags") or 0),
                    )
                except (TypeError, ValueError) as exc:
                    raise CsvIngestError(f"{source.name}:{line_number}: {exc}") from exc
                assembler.add(header)
    except OSError as exc:
        raise CsvIngestError(f"Could not read {source.name}: {exc}") from exc
    return assembler.finish()
