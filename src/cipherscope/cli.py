from __future__ import annotations

import argparse

from cipherscope.ingest.pcap import read_pcap
from cipherscope.store.jsonl import write_feature_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline, metadata-only CipherScope tools")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser(
        "ingest-pcap", help="Extract flow metadata from an authorized offline capture"
    )
    ingest.add_argument("pcap")
    ingest.add_argument("--capture-id", required=True)
    ingest.add_argument("--environment", required=True)
    ingest.add_argument("--label")
    ingest.add_argument("--output", default="data/flows.jsonl")
    args = parser.parse_args()
    if args.command == "ingest-pcap":
        flows = read_pcap(
            args.pcap, capture_id=args.capture_id, environment=args.environment, label=args.label
        )
        count = write_feature_jsonl(flows, args.output)
        print(f"Wrote {count} metadata-only flows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
