from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    import pyarrow as pa
    import pyarrow.parquet as pq

    PARQUET_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when the extra is absent
    pa = None
    pq = None
    PARQUET_AVAILABLE = False


def write_parquet(rows: list[dict[str, Any]], path: str | Path) -> int:
    """Write normalized flow rows to a Parquet file. Requires the [parquet] extra."""
    if not PARQUET_AVAILABLE:
        raise RuntimeError("Install the [parquet] extra to write Parquet files")
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, str(path))
    return len(rows)