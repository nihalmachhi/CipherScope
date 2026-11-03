from __future__ import annotations

from dataclasses import dataclass, field

from cipherscope.flows.schema import FlowRecord, PacketRecord
from cipherscope.privacy.hashing import hash_identifier

FIN = 0x01
RST = 0x04
FlowKey = tuple[str, str, int, int, str]


@dataclass(frozen=True)
class PacketHeader:
    """The only packet information CipherScope is allowed to keep."""

    timestamp: float
    source: str
    target: str
    source_port: int
    dest_port: int
    protocol: str
    size: int
    tcp_flags: int = 0


@dataclass
class _FlowState:
    flow: FlowRecord
    source: str
    keys: tuple[FlowKey, FlowKey]
    fin_directions: set[int] = field(default_factory=set)
    both_fin_at: float | None = None


class FlowAssembler:
    """Assemble bidirectional flows from metadata-only packet headers."""

    def __init__(
        self,
        *,
        capture_id: str,
        environment: str,
        dataset: str | None = None,
        label: str | None = None,
        salt: str | None = None,
        idle_timeout_s: float = 120.0,
        active_timeout_s: float = 1800.0,
        fin_linger_s: float = 5.0,
        max_active_flows: int = 100_000,
    ) -> None:
        self.capture_id = capture_id
        self.environment = environment
        self.dataset = dataset
        self.label = label
        self.salt = salt
        self.idle_timeout_s = idle_timeout_s
        self.active_timeout_s = active_timeout_s
        self.fin_linger_s = fin_linger_s
        self.max_active_flows = max(1, max_active_flows)
        self._active: dict[FlowKey, _FlowState] = {}
        self._states: dict[int, _FlowState] = {}
        self._completed: list[FlowRecord] = []

    def _pseudonym(self, value: str) -> str:
        return hash_identifier(value, self.salt)

    def _close(self, state: _FlowState) -> None:
        last = state.flow.packets[-1].timestamp if state.flow.packets else state.flow.started_at
        state.flow.completed_at = last
        for key in state.keys:
            self._active.pop(key, None)
        self._states.pop(id(state), None)

    def add(self, header: PacketHeader) -> None:
        """Append one packet header to its flow, creating or closing as needed."""
        forward: FlowKey = (
            header.source,
            header.target,
            header.source_port,
            header.dest_port,
            header.protocol,
        )
        reverse: FlowKey = (
            header.target,
            header.source,
            header.dest_port,
            header.source_port,
            header.protocol,
        )
        state = self._active.get(forward) or self._active.get(reverse)
        if state is not None:
            last_seen = state.flow.packets[-1].timestamp if state.flow.packets else header.timestamp
            expired = (
                header.timestamp - state.flow.started_at >= self.active_timeout_s
                or header.timestamp - last_seen >= self.idle_timeout_s
                or (
                    state.both_fin_at is not None
                    and header.timestamp - state.both_fin_at >= self.fin_linger_s
                )
            )
            if expired:
                self._close(state)
                self._completed.append(state.flow)
                state = None

        if state is None:
            if len(self._states) >= self.max_active_flows:
                oldest = min(self._states.values(), key=lambda item: item.flow.started_at)
                self._close(oldest)
                self._completed.append(oldest.flow)
            state = _FlowState(
                flow=FlowRecord(
                    flow_id=self._pseudonym(f"{self.capture_id}:{forward}:{header.timestamp:.6f}"),
                    host_hash=self._pseudonym(header.source),
                    peer_hash=self._pseudonym(header.target),
                    capture_id=self.capture_id,
                    environment=self.environment,
                    label=self.label,
                    started_at=header.timestamp,
                    protocol=header.protocol,
                    dataset=self.dataset,
                ),
                source=header.source,
                keys=(forward, reverse),
            )
            self._states[id(state)] = state
            self._active[forward] = state
            self._active[reverse] = state

        direction = 1 if header.source == state.source else -1
        state.flow.packets.append(
            PacketRecord(
                timestamp=header.timestamp,
                size=max(0, min(header.size, 65535)),
                direction=direction,
                tcp_flags=header.tcp_flags,
            )
        )

        if header.protocol != "tcp":
            return
        if header.tcp_flags & RST:
            self._close(state)
            self._completed.append(state.flow)
            return
        if header.tcp_flags & FIN:
            state.fin_directions.add(direction)
            if len(state.fin_directions) >= 2 and state.both_fin_at is None:
                state.both_fin_at = header.timestamp

    def finish(self) -> list[FlowRecord]:
        """Close every active flow and return the completed flows once each."""
        for state in {id(state): state for state in self._active.values()}.values():
            self._close(state)
            self._completed.append(state.flow)
        return self.drain_completed()

    def drain_completed(self) -> list[FlowRecord]:
        """Return finished flows and release their temporary output buffer."""
        unique = {flow.flow_id: flow for flow in self._completed}
        self._completed.clear()
        return list(unique.values())
