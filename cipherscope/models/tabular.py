from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
)
from sklearn.preprocessing import LabelEncoder


def _matrix(rows: list[dict[str, Any]], feature_names: list[str]) -> np.ndarray:
    return np.asarray(
        [[float(row["features"].get(name, 0.0)) for name in feature_names] for row in rows],
        dtype=np.float32,
    )


def train_baseline(
    rows: list[dict[str, Any]], train_idx: np.ndarray, feature_names: list[str], seed: int = 7
) -> tuple[RandomForestClassifier, LabelEncoder]:
    labels = LabelEncoder().fit([str(row["label"]) for row in rows])
    train_rows = [rows[int(index)] for index in train_idx]
    model = RandomForestClassifier(
        n_estimators=100, min_samples_leaf=2, class_weight="balanced", random_state=seed, n_jobs=1
    )
    model.fit(
        _matrix(train_rows, feature_names), labels.transform([r["label"] for r in train_rows])
    )
    return model, labels


def evaluate(
    model: RandomForestClassifier,
    labels: LabelEncoder,
    rows: list[dict[str, Any]],
    test_idx: np.ndarray,
    feature_names: list[str],
) -> dict[str, Any]:
    test_rows = [rows[int(index)] for index in test_idx]
    truth = labels.transform([row["label"] for row in test_rows])
    matrix = _matrix(test_rows, feature_names)
    prediction = model.predict(matrix)
    probabilities = model.predict_proba(matrix)
    beacon_idx = int(labels.transform(["beacon"])[0]) if "beacon" in labels.classes_ else 0
    beacon_truth = (truth == beacon_idx).astype(int)
    beacon_scores = probabilities[:, beacon_idx]
    false_positive_rates, true_positive_rates, _ = roc_curve(beacon_truth, beacon_scores)
    selected = np.flatnonzero(true_positive_rates >= 0.90)
    fpr_at_recall = float(false_positive_rates[selected[0]]) if len(selected) else 1.0
    return {
        "rows": len(test_rows),
        "accuracy": float(accuracy_score(truth, prediction)),
        "macro_f1": float(f1_score(truth, prediction, average="macro", zero_division=0)),
        "macro_precision": float(
            precision_score(truth, prediction, average="macro", zero_division=0)
        ),
        "macro_recall": float(recall_score(truth, prediction, average="macro", zero_division=0)),
        "beacon_pr_auc": float(average_precision_score(beacon_truth, beacon_scores))
        if len(set(beacon_truth)) > 1
        else None,
        "beacon_fpr_at_90_recall": fpr_at_recall,
        "confusion_matrix": confusion_matrix(truth, prediction).tolist(),
        "classes": labels.classes_.tolist(),
        "calibration_ece": expected_calibration_error(truth, probabilities),
        "probabilities_calibrated": False,
    }


def expected_calibration_error(
    truth: np.ndarray, probabilities: np.ndarray, bins: int = 10
) -> float:
    confidence = probabilities.max(axis=1)
    predicted = probabilities.argmax(axis=1)
    ece = 0.0
    for lower in np.linspace(0, 1, bins, endpoint=False):
        mask = (confidence >= lower) & (confidence < lower + 1 / bins)
        if mask.any():
            ece += float(
                mask.mean() * abs((predicted[mask] == truth[mask]).mean() - confidence[mask].mean())
            )
    return ece
