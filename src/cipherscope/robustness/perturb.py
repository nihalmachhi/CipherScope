from __future__ import annotations

import random
from typing import Any


def perturb_padding(flow: dict[str, Any], level: float, seed: int = 7) -> dict[str, Any]:
    rng = random.Random(seed)
    result = {**flow, "packets": [dict(packet) for packet in flow["packets"]]}
    for packet in result["packets"]:
        packet["size"] = min(65535, round(packet["size"] * (1 + rng.uniform(0, level))))
    return result


def perturb_timing(flow: dict[str, Any], max_jitter_s: float, seed: int = 7) -> dict[str, Any]:
    rng = random.Random(seed)
    result = {**flow, "packets": [dict(packet) for packet in flow["packets"]]}
    offset = 0.0
    previous = 0.0
    for index, packet in enumerate(result["packets"]):
        current = float(packet["timestamp"])
        interval = max(0.0, current - previous) if index else 0.0
        offset += rng.uniform(0, max_jitter_s)
        packet["timestamp"] = (
            result["packets"][0]["timestamp"] + offset + interval if index else current
        )
        previous = current
    return result


def truncate_packets(flow: dict[str, Any], packet_limit: int) -> dict[str, Any]:
    result = {**flow, "packets": list(flow["packets"][: max(0, packet_limit)])}
    return result
