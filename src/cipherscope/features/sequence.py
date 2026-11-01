from __future__ import annotations

import math

from cipherscope.flows.schema import FlowRecord


def extract_sequence(flow: FlowRecord, length: int = 64) -> tuple[list[list[float]], list[bool]]:
    """Return a fixed-length ``[size, log interval, flags]`` tensor and its mask."""
    tensor = [[0.0, 0.0, 0.0] for _ in range(length)]
    mask = [False] * length
    previous = flow.packets[0].timestamp if flow.packets else 0.0
    for index, packet in enumerate(flow.packets[:length]):
        interval_ms = max(0.0, packet.timestamp - previous) * 1000
        tensor[index] = [
            packet.direction * min(packet.size, 1500) / 1500,
            math.log1p(interval_ms),
            packet.tcp_flags / 255,
        ]
        mask[index] = True
        previous = packet.timestamp
    return tensor, mask
