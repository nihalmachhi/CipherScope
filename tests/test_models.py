from __future__ import annotations

import numpy as np
import pytest

from cipherscope.models.base import UnsupportedModelError, build_estimator, feature_names, to_matrix


def rows() -> list[dict]:
    return [
        {"features": {"packet_count": 3.0, "duration_s": 1.0}, "label": "web"},
        {"features": {"packet_count": 9.0, "duration_s": 2.0}, "label": "beacon"},
    ]


def test_to_matrix_uses_declared_feature_order() -> None:
    matrix = to_matrix(rows(), ["packet_count", "duration_s"])
    assert matrix.shape == (2, 2)
    assert matrix.dtype == np.float32
    assert matrix[0].tolist() == [3.0, 1.0]


def test_identifier_features_are_refused() -> None:
    leaky = [{"features": {"src_ip_hash": 1.0}, "label": "web"}]
    with pytest.raises(ValueError, match="Identifier"):
        feature_names(leaky)


def test_unknown_model_family_is_rejected() -> None:
    with pytest.raises(UnsupportedModelError):
        build_estimator("mystery", seed=7)
