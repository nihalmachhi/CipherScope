from __future__ import annotations

import argparse

from cipherscope.datasets.registry import load_dataset
from cipherscope.ingest.csv_flows import read_packet_csv
from cipherscope.ingest.pcap import iter_pcap
from cipherscope.store.jsonl import write_feature_jsonl, write_feature_jsonl_stream


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--capture-id", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--label")
    parser.add_argument("--output", default="data/flows.jsonl")


def build_parser() -> argparse.ArgumentParser:
    """Build the offline command-line interface."""
    parser = argparse.ArgumentParser(description="Offline, metadata-only CipherScope tools")
    commands = parser.add_subparsers(dest="command", required=True)

    pcap = commands.add_parser(
        "ingest-pcap", help="Extract flow metadata from an authorized offline capture"
    )
    pcap.add_argument("path")
    _add_common(pcap)

    csv_parser = commands.add_parser(
        "ingest-csv", help="Extract flow metadata from a packet-level CSV export"
    )
    csv_parser.add_argument("path")
    _add_common(csv_parser)

    dataset = commands.add_parser(
        "load-dataset", help="Load a registered dataset after accepting its licence"
    )
    dataset.add_argument("name")
    dataset.add_argument("path")
    dataset.add_argument("--i-accept-dataset-license", action="store_true", required=True)
    _add_common(dataset)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "ingest-pcap":
        count = write_feature_jsonl_stream(
            iter_pcap(
                args.path,
                capture_id=args.capture_id,
                environment=args.environment,
                label=args.label,
            ),
            args.output,
        )
        print(f"Wrote {count} metadata-only flows to {args.output}")
        return 0
    elif args.command == "ingest-csv":
        flows = read_packet_csv(
            args.path,
            capture_id=args.capture_id,
            environment=args.environment,
            label=args.label,
        )
    else:
        flows = load_dataset(
            args.name,
            args.path,
            accept_license=args.i_accept_dataset_license,
            capture_id=args.capture_id,
            environment=args.environment,
            label=args.label,
        )
    count = write_feature_jsonl(flows, args.output)
    print(f"Wrote {count} metadata-only flows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
