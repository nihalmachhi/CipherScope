from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from cipherscope.features.tabular import extract_tabular
from cipherscope.flows.schema import FlowRecord

FEATURE_SCHEMA_VERSION = "1.0.0"
EXTRACTION_CONFIG = {
    "sequence_length": 64,
    "metadata_only": True,
    "excluded_model_features": ["ip", "port", "mac", "absolute_time"],
}
CONFIG_HASH = hashlib.sha256(json.dumps(EXTRACTION_CONFIG, sort_keys=True).encode()).hexdigest()


def serialize_flow(flow: FlowRecord) -> dict[str, Any]:
    return {
        "schema_version": FEATURE_SCHEMA_VERSION,
        "config_hash": CONFIG_HASH,
        **flow.metadata(),
        "features": extract_tabular(flow),
    }


def write_feature_jsonl(flows: list[FlowRecord], path: str | Path) -> int:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        for flow in flows:
            stream.write(json.dumps(serialize_flow(flow), sort_keys=True) + "\n")
    return len(flows)
