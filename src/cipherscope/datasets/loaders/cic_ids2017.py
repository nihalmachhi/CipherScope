from __future__ import annotations

from pathlib import Path

from cipherscope.datasets.loaders.common import load_capture
from cipherscope.flows.schema import FlowRecord

DATASET = "cic-ids2017"


def load(
    path: str | Path,
    *,
    capture_id: str,
    environment: str,
    label: str | None = None,
    salt: str | None = None,
) -> list[FlowRecord]:
    """Load an authorized CIC-IDS2017 capture or packet CSV export."""
    return load_capture(
        path,
        dataset=DATASET,
        capture_id=capture_id,
        environment=environment,
        label=label,
        salt=salt,
    )
