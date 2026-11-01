from __future__ import annotations

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build(seed: int) -> Pipeline:
    """Return a scaled multinomial logistic-regression classifier."""
    return Pipeline(
        steps=[
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=seed,
                ),
            ),
        ]
    )
