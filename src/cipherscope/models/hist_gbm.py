from __future__ import annotations

from sklearn.ensemble import HistGradientBoostingClassifier


def build(seed: int) -> HistGradientBoostingClassifier:
    """Return a histogram gradient-boosting classifier."""
    return HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.08,
        class_weight="balanced",
        random_state=seed,
    )
