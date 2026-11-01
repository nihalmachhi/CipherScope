"""Drift detection for metadata feature distributions.

The module compares a baseline window with a current window. It never looks at
raw identifiers, only at the already-extracted numeric feature dictionaries, and
it reports two standard statistics:

* **Population Stability Index (PSI)** over baseline-quantile bins.
* **Kolmogorov-Smirnov (KS)** two-sample distance with an asymptotic p-value.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

PSI_STABLE = 0.10
PSI_MODERATE = 0.25
EPSILON = 1e-6


def _baseline_edges(baseline: np.ndarray, bins: int) -> np.ndarray:
    """Return monotonic bin edges from baseline quantiles."""
    quantiles = np.quantile(baseline, np.linspace(0.0, 1.0, bins + 1))
    edges = np.unique(quantiles)
    if edges.size < 3:
        low, high = float(baseline.min()), float(baseline.max())
        if low == high:
            low, high = low - 0.5, high + 0.5
        edges = np.linspace(low, high, bins + 1)
    edges = edges.astype(float)
    edges[0] = -np.inf
    edges[-1] = np.inf
    return edges


def population_stability_index(
    baseline: list[float] | np.ndarray,
    current: list[float] | np.ndarray,
    *,
    bins: int = 10,
) -> dict[str, Any]:
    """Return PSI and per-bin shares for two samples of one feature."""
    left = np.asarray(baseline, dtype=float)
    right = np.asarray(current, dtype=float)
    if left.size == 0 or right.size == 0:
        raise ValueError("PSI needs two non-empty samples")
    edges = _baseline_edges(left, bins)
    left_counts, _ = np.histogram(left, bins=edges)
    right_counts, _ = np.histogram(right, bins=edges)
    left_share = left_counts / left.size
    right_share = right_counts / right.size
    psi = 0.0
    details: list[dict[str, float]] = []
    for index in range(len(edges) - 1):
        expected = max(float(left_share[index]), EPSILON)
        actual = max(float(right_share[index]), EPSILON)
        contribution = (actual - expected) * math.log(actual / expected)
        psi += contribution
        details.append(
            {
                "lower": float(edges[index]),
                "upper": float(edges[index + 1]),
                "baseline_share": float(left_share[index]),
                "current_share": float(right_share[index]),
                "contribution": float(contribution),
            }
        )
    return {"psi": float(psi), "bins": details}


def ks_two_sample(
    baseline: list[float] | np.ndarray, current: list[float] | np.ndarray
) -> dict[str, float]:
    """Return the two-sample KS statistic and an asymptotic p-value."""
    left = np.sort(np.asarray(baseline, dtype=float))
    right = np.sort(np.asarray(current, dtype=float))
    if left.size == 0 or right.size == 0:
        raise ValueError("KS needs two non-empty samples")
    grid = np.concatenate([left, right])
    left_cdf = np.searchsorted(left, grid, side="right") / left.size
    right_cdf = np.searchsorted(right, grid, side="right") / right.size
    statistic = float(np.max(np.abs(left_cdf - right_cdf)))
    effective = math.sqrt(left.size * right.size / (left.size + right.size))
    lam = (effective + 0.12 + 0.11 / effective) * statistic
    if statistic == 0.0:
        p_value = 1.0
    else:
        p_value = 0.0
        if lam > 0:
            p_value = 2.0 * sum(
                (-1) ** (k - 1) * math.exp(-2.0 * (k**2) * (lam**2)) for k in range(1, 101)
            )
    return {"statistic": statistic, "p_value": float(min(1.0, max(0.0, p_value)))}


def psi_severity(psi: float) -> str:
    """Map a PSI value to the conventional severity band."""
    if psi < PSI_STABLE:
        return "stable"
    if psi < PSI_MODERATE:
        return "moderate"
    return "significant"


def feature_drift(
    baseline_rows: list[dict[str, Any]],
    current_rows: list[dict[str, Any]],
    *,
    bins: int = 10,
    limit: int | None = None,
) -> dict[str, Any]:
    """Compare per-feature distributions between two labelled row windows."""
    if not baseline_rows or not current_rows:
        raise ValueError("Drift needs a baseline and a current window")
    names = sorted(baseline_rows[0]["features"])
    results: list[dict[str, Any]] = []
    for name in names:
        left = [float(row["features"].get(name, 0.0)) for row in baseline_rows]
        right = [float(row["features"].get(name, 0.0)) for row in current_rows]
        if len(set(left) | set(right)) == 1:
            continue
        psi = population_stability_index(left, right, bins=bins)
        ks = ks_two_sample(left, right)
        results.append(
            {
                "feature": name,
                "psi": psi["psi"],
                "severity": psi_severity(psi["psi"]),
                "ks_statistic": ks["statistic"],
                "ks_p_value": ks["p_value"],
            }
        )
    results.sort(key=lambda item: item["psi"], reverse=True)
    if limit is not None:
        results = results[:limit]
    drifted = [item for item in results if item["severity"] != "stable"]
    return {
        "baseline_rows": len(baseline_rows),
        "current_rows": len(current_rows),
        "features_compared": len(results),
        "drifted_features": len(drifted),
        "status": "drift-detected" if drifted else "stable",
        "features": results,
    }


def chronological_drift(
    rows: list[dict[str, Any]], *, bins: int = 10, limit: int = 10
) -> dict[str, Any]:
    """Split rows by median start time and compare the earlier and later halves."""
    if len(rows) < 4:
        raise ValueError("Chronological drift needs at least four flows")
    ordered = sorted(rows, key=lambda row: float(row["started_at"]))
    middle = len(ordered) // 2
    report = feature_drift(ordered[:middle], ordered[middle:], bins=bins, limit=limit)
    report["split_at"] = float(ordered[middle]["started_at"])
    return report
