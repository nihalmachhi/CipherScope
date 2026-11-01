from __future__ import annotations

from pathlib import Path

import pytest

from cipherscope.cli import build_parser, main
from cipherscope.store.jsonl import load_rows

FIXTURES = Path(__file__).parent / "fixtures"
SALT = "cli-test-salt-long-enough"


def test_build_parser_requires_command() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_ingest_pcap_command_writes_flows(tmp_path) -> None:
    from scapy.all import IP, TCP, wrpcap

    capture = tmp_path / "capture.pcap"
    packet = IP(src="192.0.2.1", dst="198.51.100.2") / TCP(sport=1234, dport=443, flags="PA")
    packet.time = 1000.0
    wrpcap(str(capture), [packet])

    output = tmp_path / "flows.jsonl"
    rc = main(
        [
            "ingest-pcap",
            str(capture),
            "--capture-id",
            "lab",
            "--environment",
            "lab",
            "--output",
            str(output),
        ]
    )
    assert rc == 0
    assert output.exists()
    flows = load_rows(output)
    assert len(flows) == 1


def test_ingest_csv_command_writes_flows(tmp_path) -> None:
    csv_path = tmp_path / "packets.csv"
    csv_path.write_text(
        "timestamp,src_ip,dst_ip,src_port,dst_port,protocol,length\n"
        "1.0,192.0.2.1,198.51.100.2,1234,443,tcp,100\n",
        encoding="utf-8",
    )
    output = tmp_path / "flows.jsonl"
    rc = main(
        [
            "ingest-csv",
            str(csv_path),
            "--capture-id",
            "lab",
            "--environment",
            "lab",
            "--output",
            str(output),
        ]
    )
    assert rc == 0
    assert load_rows(output)


def test_load_dataset_command_requires_license(tmp_path) -> None:
    output = tmp_path / "flows.jsonl"
    with pytest.raises(SystemExit):
        main(
            [
                "load-dataset",
                "iscx_vpn_nonvpn",
                str(FIXTURES / "iscx_tiny.csv"),
                "--capture-id",
                "lab",
                "--environment",
                "lab",
                "--output",
                str(output),
            ]
        )


def test_load_dataset_command_with_license(tmp_path) -> None:
    output = tmp_path / "flows.jsonl"
    rc = main(
        [
            "load-dataset",
            "cic_ids2017",
            str(FIXTURES / "cic_tiny.csv"),
            "--i-accept-dataset-license",
            "--capture-id",
            "lab",
            "--environment",
            "lab",
            "--output",
            str(output),
            "--label",
            "benign",
        ]
    )
    assert rc == 0
    assert load_rows(output)
