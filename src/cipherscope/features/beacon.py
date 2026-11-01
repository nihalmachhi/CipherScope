from __future__ import annotations

from collections import defaultdict
from statistics import median, pstdev
from typing import Any

DEFAULT_THRESHOLD = 0.75


def _lag_autocorrelation(values: list[float], lag: int = 1) -> float:
    if len(values) <= lag:
        return 0.0
    left = values[:-lag]
    right = values[lag:]
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right, strict=True))
    left_var = sum((a - left_mean) ** 2 for a in left)
    right_var = sum((b - right_mean) ** 2 for b in right)
    denominator = (left_var * right_var) ** 0.5
    if denominator == 0:
        return 1.0
    ratio: float = numerator / denominator
    return max(-1.0, min(1.0, ratio))


def periodicity_score(times: list[float]) -> dict[str, float | int]:
    """Score how periodic a set of connection times looks.

    The estimate is robust: the period is the median interval and the spread is
    measured with the median absolute deviation, so one long gap cannot fake or
    destroy regularity. A lag-1 autocorrelation term rewards stable rhythm.

    Known false positives: NTP and other fixed-interval infrastructure, polling
    apps with a steady refresh, and load balancers that retry on a timer.
    """
    ordered = sorted(times)
    intervals = [ordered[index] - ordered[index - 1] for index in range(1, len(ordered))]
    if len(intervals) < 3:
        return {
            "score": 0.0,
            "period_s": 0,
            "interval_cv": 0.0,
            "within_ten_percent": 0.0,
            "mad_s": 0.0,
            "robust_cv": 0.0,
            "autocorrelation": 0.0,
        }

    center = median(intervals)
    deviations = [abs(value - center) for value in intervals]
    mad = median(deviations)
    robust_cv = (1.4826 * mad / center) if center else 0.0
    classic_cv = pstdev(intervals) / center if center else 0.0
    regular = sum(abs(value - center) <= center * 0.1 for value in intervals) / len(intervals)
    autocorrelation = _lag_autocorrelation(intervals)
    score = 0.55 * regular + 0.30 * (1.0 - min(robust_cv, 1.0)) + 0.15 * max(0.0, autocorrelation)
    return {
        "score": round(max(0.0, min(1.0, score)), 4),
        "period_s": round(center, 3),
        "interval_cv": round(classic_cv, 4),
        "within_ten_percent": round(regular, 4),
        "mad_s": round(mad, 4),
        "robust_cv": round(robust_cv, 4),
        "autocorrelation": round(autocorrelation, 4),
    }


def detect_beacons(
    flows: list[dict[str, Any]],
    *,
    min_connections: int = 4,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[dict[str, Any]]:
    """Group flows by an undirected host/peer pair and flag periodic callbacks."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for flow in flows:
        host, peer = str(flow["host_hash"]), str(flow["peer_hash"])
        grouped[(host, peer) if host <= peer else (peer, host)].append(flow)

    alerts = []
    for (host, peer), rows in grouped.items():
        if len(rows) < min_connections:
            continue
        metrics = periodicity_score([float(row["started_at"]) for row in rows])
        if float(metrics["score"]) < threshold:
            continue
        explanation = (
            f"{len(rows)} connections with a median interval of {metrics['period_s']}s, "
            f"{float(metrics['within_ten_percent']):.0%} of intervals within ten percent "
            "of that median."
        )
        alerts.append(
            {
                "host_hash": host,
                "peer_hash": peer,
                "connections": len(rows),
                "explanation": explanation,
                "review_required": True,
                **metrics,
            }
        )
    alerts.sort(key=lambda alert: float(alert["score"]), reverse=True)
    return alerts
