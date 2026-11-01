from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, cast

import numpy as np
from sklearn.preprocessing import LabelEncoder

FORBIDDEN_FEATURE_TOKENS = ("ip", "port", "mac", "timestamp", "absolute_time")


class UnsupportedModelError(ValueError):
    """Raised when an unknown model family is requested."""


class Classifier(Protocol):
    """The small surface every model in the zoo must provide."""

    def fit(self, matrix: np.ndarray, labels: np.ndarray) -> Any: ...

    def predict(self, matrix: np.ndarray) -> np.ndarray: ...

    def predict_proba(self, matrix: np.ndarray) -> np.ndarray: ...


@dataclass
class TrainedModel:
    """A fitted classifier plus the label mapping and feature order it expects."""

    model: Classifier
    encoder: LabelEncoder
    feature_names: list[str]

    def predict(self, rows: list[dict[str, Any]]) -> np.ndarray:
        return self.model.predict(to_matrix(rows, self.feature_names))

    def predict_proba(self, rows: list[dict[str, Any]]) -> np.ndarray:
        return self.model.predict_proba(to_matrix(rows, self.feature_names))


def feature_names(rows: list[dict[str, Any]]) -> list[str]:
    """Return the sorted, identifier-free feature names used by every model."""
    if not rows:
        raise ValueError("No rows available to derive feature names")
    names = sorted(rows[0]["features"])
    if any(token in name.lower() for name in names for token in FORBIDDEN_FEATURE_TOKENS):
        raise ValueError("Identifier or absolute-time feature found in model input")
    return names


def to_matrix(rows: list[dict[str, Any]], names: list[str]) -> np.ndarray:
    """Turn stored feature dictionaries into a dense float matrix."""
    return np.asarray(
        [[float(row["features"].get(name, 0.0)) for name in names] for row in rows],
        dtype=np.float32,
    )


def build_estimator(family: str, seed: int) -> Classifier:
    """Create an unfitted estimator for a named model family."""
    if family == "random_forest":
        from cipherscope.models.random_forest import build

        return cast(Classifier, build(seed))
    if family == "hist_gbm":
        from cipherscope.models.hist_gbm import build

        return cast(Classifier, build(seed))
    if family == "logreg":
        from cipherscope.models.logreg import build

        return cast(Classifier, build(seed))
    raise UnsupportedModelError(f"Unknown model family {family!r}")


def train(
    rows: list[dict[str, Any]],
    train_idx: np.ndarray,
    names: list[str],
    family: str = "random_forest",
    seed: int = 7,
) -> TrainedModel:
    """Fit one model on the given training rows."""
    train_rows = [rows[int(index)] for index in train_idx]
    encoder = LabelEncoder().fit([str(row["label"]) for row in rows])
    estimator = build_estimator(family, seed)
    estimator.fit(
        to_matrix(train_rows, names),
        encoder.transform([str(row["label"]) for row in train_rows]),
    )
    return TrainedModel(model=estimator, encoder=encoder, feature_names=names)
