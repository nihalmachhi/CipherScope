from __future__ import annotations

from pathlib import Path
from typing import Any

from cipherscope.flows.schema import FlowRecord, PacketRecord
from cipherscope.privacy.hashing import hash_identifier


def _value(row: dict[str, str], key: str, default: str = "-") -> str:
    return row.get(key, default)


def read_zeek_conn_log(
    path: str | Path,
    *,
    capture_id: str,
    environment: str,
    label: str | None = None,
    salt: str | None = None,
) -> list[FlowRecord]:
    """Normalize a Zeek ``conn.log`` (TSV) into metadata-only flows."""
    source = Path(path)
    lines = source.read_text(encoding="utf-8").splitlines()
    fields: list[str] = []
    rows: list[dict[str, str]] = []
    for line in lines:
        if not line.strip():
            continue
        if line.startswith("#fields"):
            fields = line.split("\t")[1:]
            continue
        if line.startswith("#"):
            continue
        if not fields:
            raise ValueError(f"{source.name} has no #fields header")
        values = line.split("\t")
        rows.append(dict(zip(fields, values, strict=False)))

    flows: list[FlowRecord] = []
    for index, row in enumerate(rows):
        ts = float(_value(row, "ts", "0"))
        origin = _value(row, "id.orig_h")
        responder = _value(row, "id.resp_h")
        protocol = _value(row, "proto", "tcp").lower()
        duration = float(_value(row, "duration", "0") or 0)
        size = int(_value(row, "orig_ip_bytes", "0") or 0) + int(_value(row, "resp_ip_bytes", "0") or 0)
        flow = FlowRecord(
            flow_id=hash_identifier(f"{capture_id}:zeek:{index}:{ts:.6f}", salt),
            host_hash=hash_identifier(origin, salt),
            peer_hash=hash_identifier(responder, salt),
            capture_id=capture_id,
            environment=environment,
            label=label,
            started_at=ts,
            protocol=protocol,
            packets=[PacketRecord(timestamp=ts, size=max(0, min(size, 65535)), direction=1)],
            completed_at=ts + duration,
            dataset="zeek",
        )
        flows.append(flow)
    return flows