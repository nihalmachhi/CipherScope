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

    @property
    def duration_s(self) -> float:
        end = self.completed_at if self.completed_at is not None else self.started_at
        return max(0.0, end - self.started_at)

    def metadata(self) -> dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "host_hash": self.host_hash,
            "peer_hash": self.peer_hash,
            "capture_id": self.capture_id,
            "environment": self.environment,
            "label": self.label,
            "started_at": self.started_at,
            "protocol": self.protocol,
            "packets": [packet.__dict__ for packet in self.packets],
            "duration_s": self.duration_s,
        }
