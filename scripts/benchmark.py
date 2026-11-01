from __future__ import annotations

import argparse
import time
from pathlib import Path

from cipherscope.ingest.pcap import read_pcap


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure offline PCAP ingestion throughput")
    parser.add_argument("pcap")
    parser.add_argument("--capture-id", default="benchmark")
    parser.add_argument("--environment", default="benchmark")
    parser.add_argument("--salt", default="benchmark-salt-long-enough")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    path = Path(args.pcap)
    best = None
    for _ in range(args.repeats):
        start = time.perf_counter()
        flows = read_pcap(path, capture_id=args.capture_id, environment=args.environment, salt=args.salt)
        elapsed = time.perf_counter() - start
        total_packets = sum(len(flow.packets) for flow in flows)
        rate = total_packets / elapsed if elapsed else float("inf")
        if best is None or rate > best[0]:
            best = (rate, len(flows), total_packets, elapsed)
    assert best is not None
    rate, flow_count, packet_count, elapsed = best
    print(f"flows={flow_count} packets={packet_count} elapsed_s={elapsed:.4f} packets_per_second={rate:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())