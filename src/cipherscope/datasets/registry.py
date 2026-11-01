from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

from cipherscope.flows.schema import FlowRecord


class DatasetNotFoundError(KeyError):
    """Raised when a dataset name has no registered specification."""


class LicenseNotAcceptedError(RuntimeError):
    """Raised when real traffic is requested without explicit licence acceptance."""


DATASETS: dict[str, dict[str, Any]] = {
    "synthetic_demo": {
        "title": "Synthetic demo",
        "license": "Generated in this project",
        "source": "Deterministic local generator",
        "contains_real_traffic": False,
        "loader": None,
    },
    "iscx_vpn_nonvpn": {
        "title": "ISCX VPN-nonVPN",
        "license": "Verify the current dataset terms before use",
        "source": "Canadian Institute for Cybersecurity",
        "contains_real_traffic": True,
        "loader": "iscx",
    },
    "cic_ids2017": {
        "title": "CIC-IDS2017",
        "license": "Verify the current dataset terms before use",
        "source": "Canadian Institute for Cybersecurity",
        "contains_real_traffic": True,
        "loader": "cic_ids2017",
    },
    "ustc_tfc2016": {
        "title": "USTC-TFC2016",
        "license": "Verify the current dataset terms before use",
        "source": "USTC research dataset",
        "contains_real_traffic": True,
        "loader": "ustc",
    },
}


def get_spec(name: str) -> dict[str, Any]:
    """Return the registry entry for a dataset name."""
    try:
        return DATASETS[name]
    except KeyError as exc:
        raise DatasetNotFoundError(
            f"Unknown dataset {name!r}; choose from {sorted(DATASETS)}"
        ) from exc


def load_dataset(
    name: str,
    path: str | Path,
    *,
    accept_license: bool,
    capture_id: str,
    environment: str,
    label: str | None = None,
    salt: str | None = None,
) -> list[FlowRecord]:
    """Load a registered dataset, requiring explicit licence acceptance for real traffic."""
    spec = get_spec(name)
    if spec["contains_real_traffic"] and not accept_license:
        raise LicenseNotAcceptedError(
            f"{spec['title']} contains real traffic. Read its terms and pass "
            "--i-accept-dataset-license before loading it."
        )
    loader = spec["loader"]
    if loader is None:
        raise DatasetNotFoundError(f"{name!r} has no file loader")
    module = import_module(f"cipherscope.datasets.loaders.{loader}")
    return list(
        module.load(
            path,
            capture_id=capture_id,
            environment=environment,
            label=label,
            salt=salt,
        )
    )
