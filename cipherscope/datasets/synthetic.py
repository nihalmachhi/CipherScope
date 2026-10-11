from __future__ import annotations

import json
import random
from pathlib import Path

from cipherscope.features.tabular import extract_tabular
from cipherscope.flows.schema import FlowRecord, PacketRecord


def generate_demo(path: str | Path, seed: int = 13, flows_per_environment: int = 120) -> int:
    """Create deterministic synthetic metadata; no captured user traffic is included."""
    rng = random.Random(seed)
    rows = []
    labels = ("web", "streaming", "beacon")
    environments = ("lab-alpha", "lab-beta")
    for env_index, environment in enumerate(environments):
        for index in range(flows_per_environment):
            label = labels[index % len(labels)]
            host = (
                f"{environment}-beacon-host"
                if label == "beacon"
                else f"{environment}-host-{index // 6:03d}"
            )
            peer = (
                f"{environment}-beacon-peer"
                if label == "beacon"
                else f"{environment}-peer-{index % 23:03d}"
            )
            base = 1_700_000_000 + env_index * 10_000_000 + index * 29
            count = 16 if label == "beacon" else rng.randint(8, 24)
            gap = 30 if label == "beacon" else 0.25 if label == "web" else 0.1
            packets = []
            for packet_index in range(count):
                direction = 1 if packet_index % (2 if label == "web" else 4) == 0 else -1
                if label == "beacon":
                    size = rng.randint(90, 120)
                elif label == "streaming":
                    size = rng.randint(1050, 1450) if direction < 0 else rng.randint(60, 180)
                else:
                    size = rng.randint(180, 900)
                jitter = rng.uniform(-0.015, 0.015) if label == "beacon" else rng.uniform(0, 0.07)
                timestamp = base + packet_index * max(0.01, gap + jitter)
                if env_index and label == "web":
                    size = int(size * 0.92)
                packets.append(
                    PacketRecord(timestamp, size, direction, 0x10 if packet_index else 0x02)
                )
            flow = FlowRecord(
                f"synthetic-{environment}-{index:04d}",
                host,
                peer,
                f"capture-{environment}-{index // 20:02d}",
                environment,
                label,
                base,
                "tcp",
                packets,
                packets[-1].timestamp,
            )
            rows.append(
                {
                    "flow_id": flow.flow_id,
                    "host_hash": host,
                    "peer_hash": peer,
                    "capture_id": flow.capture_id,
                    "session_id": flow.flow_id,
                    "dataset": environment,
                    "environment": environment,
                    "label": label,
                    "started_at": flow.started_at,
                    "features": extract_tabular(flow),
                    "packets": [p.__dict__ for p in packets],
                }
            )
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    return len(rows)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic CipherScope demo flows")
    parser.add_argument("--output", default="data/demo_flows.jsonl")
    parser.add_argument("--count", type=int, default=120)
    args = parser.parse_args()
    print(f"Wrote {generate_demo(args.output, flows_per_environment=args.count)} synthetic flows")
