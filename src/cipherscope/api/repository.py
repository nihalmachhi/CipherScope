from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from cipherscope.store.jsonl import load_rows


class FlowRepository:
    """In-memory flow store with a flow-id index and mtime-based reload."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._lock = threading.Lock()
        self._rows: list[dict[str, Any]] = []
        self._index: dict[str, dict[str, Any]] = {}
        self._mtime: float | None = None
        self.refresh()

    @property
    def path(self) -> Path:
        return self._path

    def refresh(self) -> None:
        """Reload rows when the backing file changed on disk."""
        with self._lock:
            if not self._path.exists():
                self._rows, self._index, self._mtime = [], {}, None
                return
            mtime = self._path.stat().st_mtime
            if mtime == self._mtime:
                return
            rows = load_rows(self._path)
            self._rows = rows
            self._index = {str(row["flow_id"]): row for row in rows}
            self._mtime = mtime

    def rows(self) -> list[dict[str, Any]]:
        """Return every stored row, reloading first if the file changed."""
        self.refresh()
        return list(self._rows)

    def get(self, flow_id: str) -> dict[str, Any] | None:
        """Return one row by flow id in constant time."""
        self.refresh()
        return self._index.get(flow_id)

    def total(self) -> int:
        self.refresh()
        return len(self._rows)
