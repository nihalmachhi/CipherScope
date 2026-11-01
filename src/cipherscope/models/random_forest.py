from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier


def build(seed: int) -> RandomForestClassifier:
    """Return the balanced random-forest baseline."""
    return RandomForestClassifier(
        n_estimators=150,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=seed,
        n_jobs=1,
    )
