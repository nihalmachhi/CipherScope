from __future__ import annotations

from collections import defaultdict
from statistics import median, pstdev
from typing import Any


def periodicity_score(times: list[float]) -> dict[str, float | int]:
    ordered = sorted(times)
    intervals = [ordered[index] - ordered[index - 1] for index in range(1, len(ordered))]
    if len(intervals) < 3:
        return {"score": 0.0, "period_s": 0, "interval_cv": 0.0, "within_ten_percent": 0.0}
    center = median(intervals)
    cv = pstdev(intervals) / center if center else 0.0
    regular = sum(abs(value - center) <= center * 0.1 for value in intervals) / len(intervals)
    return {
        "score": max(0.0, min(1.0, 0.65 * regular + 0.35 * (1 - min(cv, 1)))),
        "period_s": round(center, 3),
        "interval_cv": round(cv, 4),
        "within_ten_percent": round(regular, 4),
    }


def detect_beacons(
    flows: list[dict[str, Any]], *, min_connections: int = 4
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for flow in flows:
        grouped[(str(flow["host_hash"]), str(flow["peer_hash"]))].append(flow)
    alerts = []
    for (host, peer), rows in grouped.items():
        if len(rows) < min_connections:
            continue
        metrics = periodicity_score([float(row["started_at"]) for row in rows])
        if metrics["score"] >= 0.75:
            explanation = (
                f"{len(rows)} observed connections with median interval "
                f"{metrics['period_s']}s and {metrics['within_ten_percent']:.0%} "
                "of intervals within ten percent of that median."
            )
            alerts.append(
                {
                    "host_hash": host,
                    "peer_hash": peer,
                    "connections": len(rows),
                    "explanation": explanation,
                    **metrics,
                }
            )
    return alerts
