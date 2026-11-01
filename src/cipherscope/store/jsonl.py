from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from cipherscope.features.tabular import extract_tabular
from cipherscope.flows.schema import FlowRecord

FEATURE_SCHEMA_VERSION = "1.0.0"
SUPPORTED_SCHEMA_VERSIONS = frozenset({"1.0.0"})
EXTRACTION_CONFIG = {
    "sequence_length": 64,
    "metadata_only": True,
    "excluded_model_features": ["ip", "port", "mac", "absolute_time"],
}
CONFIG_HASH = hashlib.sha256(json.dumps(EXTRACTION_CONFIG, sort_keys=True).encode()).hexdigest()


class SchemaVersionError(ValueError):
    """Raised when stored rows use a schema version this build cannot read."""


class StoredPacket(BaseModel):
    """One packet header as stored on disk. Payload bytes are never present."""

    model_config = ConfigDict(extra="forbid")

    timestamp: float
    size: int = Field(ge=0, le=65535)
    direction: int = Field(ge=-1, le=1)
    tcp_flags: int = Field(default=0, ge=0, le=255)


class StoredFlow(BaseModel):
    """A validated, metadata-only flow row."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    config_hash: str
    flow_id: str
    host_hash: str
    peer_hash: str
    capture_id: str
    session_id: str | None = None
    dataset: str | None = None
    environment: str
    label: str | None = None
    started_at: float
    protocol: str = "tcp"
    packets: list[StoredPacket]
    duration_s: float = Field(ge=0.0)
    bytes_total: int = Field(ge=0)
    features: dict[str, float]


def serialize_flow(flow: FlowRecord) -> dict[str, Any]:
    """Return the on-disk JSONL row for one flow."""
    return {
        "schema_version": FEATURE_SCHEMA_VERSION,
        "config_hash": CONFIG_HASH,
        **flow.metadata(),
        "features": extract_tabular(flow),
    }


def validate_row(row: dict[str, Any]) -> dict[str, Any]:
    """Validate one stored row and return it as a plain dictionary."""
    version = row.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise SchemaVersionError(
            f"Unsupported schema_version {version!r}; this build reads "
            f"{sorted(SUPPORTED_SCHEMA_VERSIONS)}. Regenerate the dataset."
        )
    try:
        return StoredFlow.model_validate(row).model_dump()
    except ValidationError as exc:
        flow_id = row.get("flow_id", "<unknown>")
        raise SchemaVersionError(f"Invalid stored row {flow_id}: {exc}") from exc


def load_rows(path: str | Path, *, validate: bool = True) -> list[dict[str, Any]]:
    """Read JSONL rows, validating the schema version and field types by default."""
    source = Path(path)
    rows: list[dict[str, Any]] = []
    with source.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SchemaVersionError(f"{source.name}:{line_number} is not valid JSON") from exc
            rows.append(validate_row(row) if validate else row)
    return rows


def write_feature_jsonl(flows: list[FlowRecord], path: str | Path) -> int:
    """Write validated, metadata-only flow rows to JSONL."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        for flow in flows:
            stream.write(json.dumps(serialize_flow(flow), sort_keys=True) + "\n")
    return len(flows)
