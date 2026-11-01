from __future__ import annotations

from collections.abc import Callable

import numpy as np


def bootstrap_ci(
    values: np.ndarray,
    statistic: Callable[[np.ndarray], float] = np.mean,
    *,
    confidence: float = 0.95,
    resamples: int = 2000,
    seed: int = 7,
) -> dict[str, float]:
    """Return a percentile bootstrap confidence interval for a statistic."""
    sample = np.asarray(values, dtype=float)
    if sample.size == 0:
        raise ValueError("Cannot bootstrap an empty sample")
    rng = np.random.default_rng(seed)
    draws = np.array(
        [statistic(rng.choice(sample, size=sample.size, replace=True)) for _ in range(resamples)]
    )
    tail = (1.0 - confidence) / 2.0
    return {
        "estimate": float(statistic(sample)),
        "low": float(np.quantile(draws, tail)),
        "high": float(np.quantile(draws, 1.0 - tail)),
        "confidence": confidence,
        "resamples": resamples,
    }
