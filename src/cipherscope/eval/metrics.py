from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
)


def expected_calibration_error(
    truth: np.ndarray, probabilities: np.ndarray, bins: int = 10
) -> float:
    """Return the top-label expected calibration error."""
    confidence = probabilities.max(axis=1)
    predicted = probabilities.argmax(axis=1)
    error = 0.0
    for lower in np.linspace(0, 1, bins, endpoint=False):
        mask = (confidence >= lower) & (confidence < lower + 1 / bins)
        if mask.any():
            error += float(
                mask.mean() * abs((predicted[mask] == truth[mask]).mean() - confidence[mask].mean())
            )
    return error


def fpr_at_recall(truth: np.ndarray, scores: np.ndarray, target_recall: float = 0.9) -> float:
    """Return the false-positive rate at a target recall for the positive class."""
    if len(set(truth.tolist())) < 2:
        return 1.0
    false_positive_rates, true_positive_rates, _ = roc_curve(truth, scores)
    selected = np.flatnonzero(true_positive_rates >= target_recall)
    return float(false_positive_rates[selected[0]]) if len(selected) else 1.0


def evaluate_predictions(
    truth: np.ndarray,
    prediction: np.ndarray,
    probabilities: np.ndarray,
    classes: list[str],
) -> dict[str, Any]:
    """Compute the metric bundle used by every split and model."""
    result: dict[str, Any] = {
        "rows": int(len(truth)),
        "accuracy": float(accuracy_score(truth, prediction)),
        "macro_f1": float(f1_score(truth, prediction, average="macro", zero_division=0)),
        "macro_precision": float(
            precision_score(truth, prediction, average="macro", zero_division=0)
        ),
        "macro_recall": float(recall_score(truth, prediction, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(truth, prediction).tolist(),
        "classes": classes,
        "calibration_ece": expected_calibration_error(truth, probabilities),
    }
    if "beacon" in classes:
        beacon_index = classes.index("beacon")
        beacon_truth = (truth == beacon_index).astype(int)
        beacon_scores = probabilities[:, beacon_index]
        result["beacon_pr_auc"] = (
            float(average_precision_score(beacon_truth, beacon_scores))
            if len(set(beacon_truth.tolist())) > 1
            else None
        )
        result["beacon_fpr_at_90_recall"] = fpr_at_recall(beacon_truth, beacon_scores)
    return result


def pooled_predictions(
    parts: list[tuple[np.ndarray, np.ndarray, np.ndarray]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Concatenate per-fold truth, prediction and probability arrays in order."""
    truth = np.concatenate([part[0] for part in parts])
    prediction = np.concatenate([part[1] for part in parts])
    probabilities = np.concatenate([part[2] for part in parts])
    return truth, prediction, probabilities
