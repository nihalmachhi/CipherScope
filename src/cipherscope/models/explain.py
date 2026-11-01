from __future__ import annotations

from typing import Any, TypedDict

from sklearn.inspection import permutation_importance

from cipherscope.models.base import TrainedModel, to_matrix


class FeatureImportance(TypedDict):
    """One feature's permutation-importance estimate."""

    feature: str
    importance_mean: float
    importance_std: float


def top_permutation_importance(
    model: TrainedModel,
    rows: list[dict[str, Any]],
    *,
    seed: int = 7,
    repeats: int = 3,
    limit: int = 10,
) -> list[FeatureImportance]:
    """Rank features by how much shuffling them hurts macro-F1 on held-out rows."""
    matrix = to_matrix(rows, model.feature_names)
    truth = model.encoder.transform([str(row["label"]) for row in rows])
    result = permutation_importance(
        model.model,
        matrix,
        truth,
        n_repeats=repeats,
        random_state=seed,
        scoring="f1_macro",
    )
    ranking: list[FeatureImportance] = [
        {
            "feature": name,
            "importance_mean": float(mean),
            "importance_std": float(std),
        }
        for name, mean, std in zip(
            model.feature_names,
            result.importances_mean,
            result.importances_std,
            strict=True,
        )
    ]
    ranking.sort(key=lambda item: item["importance_mean"], reverse=True)
    return ranking[:limit]
