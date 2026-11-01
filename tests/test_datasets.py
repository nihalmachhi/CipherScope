from __future__ import annotations

from pathlib import Path

import pytest

from cipherscope.datasets.registry import (
    DatasetNotFoundError,
    LicenseNotAcceptedError,
    load_dataset,
)
from cipherscope.ingest.csv_flows import CsvIngestError, read_packet_csv

FIXTURES = Path(__file__).parent / "fixtures"
SALT = "dataset-test-salt-long-enough"


def test_packet_csv_normalises_to_one_flow() -> None:
    flows = read_packet_csv(
        FIXTURES / "iscx_tiny.csv",
        capture_id="iscx-lab",
        environment="lab-alpha",
        dataset="iscx-vpn-nonvpn",
        label="vpn",
        salt=SALT,
    )
    assert len(flows) == 1
    assert len(flows[0].packets) == 7
    assert flows[0].dataset == "iscx-vpn-nonvpn"
    assert flows[0].host_hash.startswith("h:")
    assert flows[0].bytes_total > 0


def test_real_dataset_requires_license_acceptance() -> None:
    with pytest.raises(LicenseNotAcceptedError):
        load_dataset(
            "iscx_vpn_nonvpn",
            FIXTURES / "iscx_tiny.csv",
            accept_license=False,
            capture_id="iscx-lab",
            environment="lab-alpha",
            salt=SALT,
        )


def test_registered_loader_runs_with_acceptance() -> None:
    flows = load_dataset(
        "cic_ids2017",
        FIXTURES / "cic_tiny.csv",
        accept_license=True,
        capture_id="cic-lab",
        environment="lab-beta",
        label="benign",
        salt=SALT,
    )
    assert len(flows) == 1
    assert flows[0].dataset == "cic-ids2017"


def test_unknown_dataset_is_rejected() -> None:
    with pytest.raises(DatasetNotFoundError):
        load_dataset(
            "mystery",
            FIXTURES / "iscx_tiny.csv",
            accept_license=True,
            capture_id="x",
            environment="y",
            salt=SALT,
        )


def test_csv_missing_columns_is_rejected(tmp_path) -> None:
    broken = tmp_path / "broken.csv"
    broken.write_text("timestamp,src_ip\n1,192.0.2.1\n", encoding="utf-8")
    with pytest.raises(CsvIngestError, match="missing required columns"):
        read_packet_csv(
            broken,
            capture_id="x",
            environment="y",
            salt=SALT,
        )
