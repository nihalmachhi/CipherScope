from __future__ import annotations

from pathlib import Path

from cipherscope.flows.schema import FlowRecord
from cipherscope.ingest.csv_flows import read_packet_csv
from cipherscope.ingest.pcap import SUPPORTED_SUFFIXES, read_pcap


class DatasetFormatError(ValueError):
    """Raised when a dataset file is neither an offline capture nor a packet CSV."""


def load_capture(
    path: str | Path,
    *,
    dataset: str,
    capture_id: str,
    environment: str,
    label: str | None = None,
    salt: str | None = None,
) -> list[FlowRecord]:
    """Normalise a PCAP/PCAPNG or packet-level CSV into ``FlowRecord`` objects."""
    source = Path(path)
    if source.suffix.lower() in SUPPORTED_SUFFIXES:
        return read_pcap(
            source,
            capture_id=capture_id,
            environment=environment,
            dataset=dataset,
            label=label,
            salt=salt,
        )
    if source.suffix.lower() == ".csv":
        return read_packet_csv(
            source,
            capture_id=capture_id,
            environment=environment,
            dataset=dataset,
            label=label,
            salt=salt,
        )
    raise DatasetFormatError(
        f"Unsupported dataset file {source.name}; provide .pcap, .pcapng, .cap or .csv"
    )
