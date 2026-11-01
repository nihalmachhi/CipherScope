from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import GroupKFold

from cipherscope.models.base import TrainedModel, build_estimator, to_matrix


def calibrate(
    rows: list[dict[str, Any]],
    train_idx: np.ndarray,
    names: list[str],
    family: str,
    seed: int,
) -> TrainedModel:
    """Fit isotonic calibration on grouped folds carved only from the training rows."""
    from sklearn.preprocessing import LabelEncoder

    train_rows = [rows[int(index)] for index in train_idx]
    encoder = LabelEncoder().fit([str(row["label"]) for row in rows])
    groups = np.asarray([str(row["host_hash"]) for row in train_rows])
    folds = min(3, len(set(groups.tolist())))
    if folds < 2:
        raise ValueError("Calibration needs at least two host groups in the training rows")
    splits = list(GroupKFold(n_splits=folds).split(np.zeros(len(train_rows)), groups=groups))
    estimator = CalibratedClassifierCV(
        estimator=build_estimator(family, seed),
        method="isotonic",
        cv=splits,
    )
    estimator.fit(
        to_matrix(train_rows, names),
        encoder.transform([str(row["label"]) for row in train_rows]),
    )
    return TrainedModel(model=estimator, encoder=encoder, feature_names=names)
