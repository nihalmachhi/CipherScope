from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PacketRecord:
    timestamp: float
    size: int
    direction: int
    tcp_flags: int = 0


@dataclass
class FlowRecord:
    flow_id: str
    host_hash: str
    peer_hash: str
    capture_id: str
    environment: str
    label: str | None
    started_at: float
    protocol: str
    packets: list[PacketRecord] = field(default_factory=list)
    completed_at: float | None = None
    session_id: str | None = None
    dataset: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> FlowRecord:
        """Rebuild a flow from a stored JSONL row so features can be re-extracted."""
        packets = [PacketRecord(**packet) for packet in row["packets"]]
        return cls(
            flow_id=str(row["flow_id"]),
            host_hash=str(row["host_hash"]),
            peer_hash=str(row["peer_hash"]),
            capture_id=str(row["capture_id"]),
            environment=str(row["environment"]),
            label=row.get("label"),
            started_at=float(row["started_at"]),
            protocol=str(row.get("protocol", "tcp")),
            packets=packets,
            completed_at=float(packets[-1].timestamp) if packets else None,
            session_id=row.get("session_id"),
            dataset=row.get("dataset"),
        )

    @property
    def duration_s(self) -> float:
        end = self.completed_at if self.completed_at is not None else self.started_at
        return max(0.0, end - self.started_at)

    @property
    def bytes_total(self) -> int:
        return sum(packet.size for packet in self.packets)

    def metadata(self) -> dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "host_hash": self.host_hash,
            "peer_hash": self.peer_hash,
            "capture_id": self.capture_id,
            "session_id": self.session_id,
            "dataset": self.dataset or self.environment,
            "environment": self.environment,
            "label": self.label,
            "started_at": self.started_at,
            "protocol": self.protocol,
            "packets": [packet.__dict__ for packet in self.packets],
            "duration_s": self.duration_s,
            "bytes_total": self.bytes_total,
        }
