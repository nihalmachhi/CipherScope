from __future__ import annotations

import math
from collections import Counter
from statistics import mean, pstdev

from cipherscope.flows.schema import FlowRecord


def _entropy(values: list[int], bins: int = 16) -> float:
    if not values:
        return 0.0
    counts = Counter(min(bins - 1, value * bins // 1501) for value in values)
    total = len(values)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def extract_tabular(flow: FlowRecord) -> dict[str, float]:
    packets = flow.packets
    forward = [packet.size for packet in packets if packet.direction > 0]
    reverse = [packet.size for packet in packets if packet.direction < 0]
    times = [packet.timestamp for packet in packets]
    intervals = [max(0.0, times[i] - times[i - 1]) for i in range(1, len(times))]
    result: dict[str, float] = {
        "duration_s": flow.duration_s,
        "packet_count": float(len(packets)),
        "forward_packet_count": float(len(forward)),
        "reverse_packet_count": float(len(reverse)),
        "forward_bytes": float(sum(forward)),
        "reverse_bytes": float(sum(reverse)),
        "byte_ratio": sum(forward) / max(1, sum(reverse)),
        "packet_ratio": len(forward) / max(1, len(reverse)),
        "packet_size_mean": mean([p.size for p in packets]) if packets else 0.0,
        "packet_size_std": pstdev([p.size for p in packets]) if len(packets) > 1 else 0.0,
        "packet_size_min": float(min((p.size for p in packets), default=0)),
        "packet_size_max": float(max((p.size for p in packets), default=0)),
        "forward_size_mean": mean(forward) if forward else 0.0,
        "reverse_size_mean": mean(reverse) if reverse else 0.0,
        "iat_mean_s": mean(intervals) if intervals else 0.0,
        "iat_std_s": pstdev(intervals) if len(intervals) > 1 else 0.0,
        "iat_min_s": min(intervals, default=0.0),
        "iat_max_s": max(intervals, default=0.0),
        "iat_cv": pstdev(intervals) / mean(intervals)
        if len(intervals) > 1 and mean(intervals)
        else 0.0,
        "packet_size_entropy": _entropy([p.size for p in packets]),
        "small_packet_fraction": sum(p.size < 128 for p in packets) / max(1, len(packets)),
        "tcp_syn_count": float(sum(bool(p.tcp_flags & 0x02) for p in packets)),
        "tcp_fin_count": float(sum(bool(p.tcp_flags & 0x01) for p in packets)),
        "tcp_rst_count": float(sum(bool(p.tcp_flags & 0x04) for p in packets)),
        "tcp_psh_count": float(sum(bool(p.tcp_flags & 0x08) for p in packets)),
    }
    for direction, sizes in (("forward", forward), ("reverse", reverse)):
        total = max(1, len(sizes))
        for index in range(16):
            result[f"{direction}_size_bin_{index:02d}"] = (
                sum(min(15, size * 16 // 1501) == index for size in sizes) / total
            )
    return result


def extract_sequence(flow: FlowRecord, length: int = 64) -> tuple[list[list[float]], list[bool]]:
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
