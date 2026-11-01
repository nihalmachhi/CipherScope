from __future__ import annotations

from typing import Any

import numpy as np

try:  # pragma: no cover - optional dependency
    import torch
    from torch import nn

    TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when the extra is absent
    torch = None
    nn = None
    TORCH_AVAILABLE = False

SEQUENCE_LENGTH = 64


class SequenceCNN(nn.Module if TORCH_AVAILABLE else object):  # type: ignore[misc]
    """A small 1D CNN over the 64x3 size/interval/flags tensor."""

    def __init__(self, classes: int) -> None:
        if not TORCH_AVAILABLE:
            raise RuntimeError("Install the [deep] extra to use the 1D-CNN model")
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(32, classes),
        )

    def forward(self, inputs: Any) -> Any:
        return self.net(inputs)


def train_sequence_model(
    tensors: list[list[list[float]]],
    labels: list[int],
    *,
    epochs: int = 20,
    seed: int = 7,
) -> Any:
    """Train the optional 1D-CNN on fixed-length sequence tensors."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("Install the [deep] extra to use the 1D-CNN model")
    torch.manual_seed(seed)
    features = torch.tensor(tensors, dtype=torch.float32).permute(0, 2, 1)
    targets = torch.tensor(labels, dtype=torch.long)
    model = SequenceCNN(classes=int(targets.max().item()) + 1)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = loss_fn(model(features), targets)
        loss.backward()
        optimizer.step()
    return model


def predict_sequence(model: Any, tensors: list[list[list[float]]]) -> np.ndarray:
    """Return predicted class indices for sequence tensors."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("Install the [deep] extra to use the 1D-CNN model")
    model.eval()
    with torch.no_grad():
        features = torch.tensor(tensors, dtype=torch.float32).permute(0, 2, 1)
        predicted: np.ndarray = model(features).argmax(dim=1).cpu().numpy()
    return predicted
