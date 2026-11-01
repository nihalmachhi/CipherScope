from __future__ import annotations

import argparse
import random
from pathlib import Path

from cipherscope.flows.schema import FlowRecord, PacketRecord
from cipherscope.privacy.hashing import hash_identifier
from cipherscope.store.jsonl import write_feature_jsonl

ENVIRONMENTS = ("lab-alpha", "lab-beta", "lab-gamma")
LABELS = ("web", "streaming", "beacon")
BASE_TIME = 1_700_000_000.0


def _pseudonym(value: str, salt: str | None) -> str:
    return hash_identifier(f"synthetic:{value}", salt)


def _packet(timestamp: float, size: int, direction: int, flags: int) -> PacketRecord:
    return PacketRecord(
        timestamp=round(timestamp, 6),
        size=max(40, min(1500, size)),
        direction=direction,
        tcp_flags=flags,
    )


def _web_packets(rng: random.Random, start: float, polling: bool) -> list[PacketRecord]:
    """Browsing traffic; ``polling`` makes it look periodic, a hard negative."""
    count = rng.randint(12, 40) if polling else rng.randint(6, 30)
    gap = rng.uniform(8.0, 30.0) if polling else rng.uniform(0.05, 4.0)
    packets: list[PacketRecord] = []
    clock = start
    for index in range(count):
        direction = 1 if index % 2 == 0 else -1
        base = rng.randint(180, 620) if direction > 0 else rng.randint(400, 1400)
        packets.append(_packet(clock, base + rng.randint(-60, 60), direction, 24))
        clock += max(0.01, gap * rng.uniform(0.85, 1.15))
    return packets


def _streaming_packets(
    rng: random.Random, start: float, slow: bool, short: bool = False
) -> list[PacketRecord]:
    count = rng.randint(20, 50) if short else rng.randint(40, 200)
    if slow:
        rate = rng.uniform(0.15, 0.6)
    elif short:
        rate = rng.uniform(0.05, 0.3)
    else:
        rate = rng.uniform(0.01, 0.08)
    packets: list[PacketRecord] = []
    clock = start
    for index in range(count):
        direction = 1 if index % 9 else -1
        if short:
            size = rng.randint(200, 1200) if direction > 0 else rng.randint(60, 220)
        else:
            size = rng.randint(900, 1500) if direction > 0 else rng.randint(60, 220)
        packets.append(_packet(clock, size, direction, 24))
        clock += rate * rng.uniform(0.8, 1.2)
    return packets


def _beacon_packets(rng: random.Random, start: float, noisy: bool) -> list[PacketRecord]:
    count = rng.randint(4, 12) if noisy else rng.randint(4, 10)
    packets: list[PacketRecord] = []
    clock = start
    for index in range(count):
        direction = 1 if index % 2 == 0 else -1
        size = rng.randint(80, 520) if noisy else rng.randint(90, 260)
        packets.append(_packet(clock, size, direction, 24))
        clock += rng.uniform(0.05, 0.4)
    return packets


def _micro_poll_packets(rng: random.Random, start: float) -> list[PacketRecord]:
    """One tiny request/response exchange; the hardest negative for a beacon."""
    packets: list[PacketRecord] = []
    clock = start
    for index in range(rng.randint(2, 4)):
        direction = 1 if index % 2 == 0 else -1
        packets.append(_packet(clock, rng.randint(80, 400), direction, 24))
        clock += rng.uniform(0.05, 0.5)
    return packets


def _session_flows(
    *,
    rng: random.Random,
    salt: str | None,
    environment: str,
    dataset: str,
    label: str,
    scenario: str,
    host: str,
    peers: list[str],
    session_index: int,
    start: float,
) -> list[FlowRecord]:
    session_id = _pseudonym(f"{environment}:session:{session_index}", salt)
    flows: list[FlowRecord] = []
    if scenario == "web-micro-polling":
        period = rng.uniform(20.0, 100.0)
        jitter = rng.uniform(0.15, 0.4)
        peer = peers[0]
        clock = start
        for connection in range(rng.randint(6, 14)):
            packets = _micro_poll_packets(rng, clock)
            flows.append(
                _record(
                    rng=rng,
                    salt=salt,
                    environment=environment,
                    dataset=dataset,
                    label=label,
                    scenario=scenario,
                    host=host,
                    peer=peer,
                    session_id=session_id,
                    packets=packets,
                    index=connection,
                )
            )
            clock += period * (1.0 + rng.uniform(-jitter, jitter))
        return flows

    if label == "beacon":
        noisy = scenario == "beacon-noisy"
        period = rng.uniform(15.0, 120.0)
        jitter = rng.uniform(0.25, 0.5) if noisy else rng.uniform(0.01, 0.18)
        peer = peers[0]
        clock = start
        for connection in range(rng.randint(6, 14)):
            packets = _beacon_packets(rng, clock, noisy)
            flows.append(
                _record(
                    rng=rng,
                    salt=salt,
                    environment=environment,
                    dataset=dataset,
                    label=label,
                    scenario=scenario,
                    host=host,
                    peer=peer,
                    session_id=session_id,
                    packets=packets,
                    index=connection,
                )
            )
            clock += period * (1.0 + rng.uniform(-jitter, jitter))
        return flows

    flow_count = rng.randint(2, 5)
    clock = start
    for index in range(flow_count):
        peer = peers[index % len(peers)]
        if label == "streaming":
            packets = _streaming_packets(
                rng,
                clock,
                slow=scenario == "slow-streaming",
                short=scenario == "streaming-short",
            )
        else:
            packets = _web_packets(
                rng,
                clock,
                polling=scenario == "web-polling",
            )
        flows.append(
            _record(
                rng=rng,
                salt=salt,
                environment=environment,
                dataset=dataset,
                label=label,
                scenario=scenario,
                host=host,
                peer=peer,
                session_id=session_id,
                packets=packets,
                index=index,
            )
        )
        clock = packets[-1].timestamp + rng.uniform(1.0, 20.0)
    return flows


def _record(
    *,
    rng: random.Random,
    salt: str | None,
    environment: str,
    dataset: str,
    label: str,
    scenario: str,
    host: str,
    peer: str,
    session_id: str,
    packets: list[PacketRecord],
    index: int,
) -> FlowRecord:
    started = packets[0].timestamp
    flow_id = _pseudonym(f"{environment}:{session_id}:{index}", salt)
    return FlowRecord(
        flow_id=flow_id,
        host_hash=_pseudonym(host, salt),
        peer_hash=_pseudonym(peer, salt),
        capture_id=_pseudonym(f"{environment}:capture:{index % 4}", salt),
        environment=environment,
        label=label,
        started_at=started,
        protocol="tcp",
        packets=packets,
        completed_at=packets[-1].timestamp,
        session_id=session_id,
        dataset=dataset,
    )


def generate_demo(
    path: str | Path,
    seed: int = 13,
    flows_per_environment: int = 150,
    salt: str | None = None,
) -> int:
    """Write deterministic synthetic metadata for pipeline validation only.

    Three environments share opaque hashed identifiers, real multi-flow sessions,
    overlapping classes and hard negatives (periodic web polling, bursty browsing
    and slow streaming), so scores are not trivially perfect.
    """
    rng = random.Random(seed)
    flows: list[FlowRecord] = []
    for environment_index, environment in enumerate(ENVIRONMENTS):
        dataset = f"campaign-{environment_index + 1}"
        hosts = [f"host-{index:03d}" for index in range(24)]
        peers = [f"peer-{index:03d}" for index in range(40)]
        scenarios = (
            ("web", "web-browsing"),
            ("web", "web-browsing"),
            ("web", "web-polling"),
            ("web", "web-micro-polling"),
            ("streaming", "streaming"),
            ("streaming", "streaming-short"),
            ("streaming", "slow-streaming"),
            ("beacon", "beacon"),
            ("beacon", "beacon-noisy"),
        )
        environment_flows: list[FlowRecord] = []
        session_index = 0
        clock = BASE_TIME + environment_index * 86_400.0
        while len(environment_flows) < flows_per_environment:
            label, scenario = scenarios[session_index % len(scenarios)]
            host = hosts[session_index % len(hosts)]
            peer_pool = [peers[(session_index * 7 + offset) % len(peers)] for offset in range(3)]
            produced = _session_flows(
                rng=rng,
                salt=salt,
                environment=environment,
                dataset=dataset,
                label=label,
                scenario=scenario,
                host=host,
                peers=peer_pool,
                session_index=session_index,
                start=clock,
            )
            environment_flows.extend(produced)
            clock += rng.uniform(60.0, 900.0)
            session_index += 1
        flows.extend(environment_flows[:flows_per_environment])
    return write_feature_jsonl(flows, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate labelled synthetic metadata flows")
    parser.add_argument("--output", default="data/demo_flows.jsonl")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--flows-per-environment", type=int, default=150)
    args = parser.parse_args()
    count = generate_demo(
        args.output, seed=args.seed, flows_per_environment=args.flows_per_environment
    )
    print(f"Wrote {count} synthetic metadata flows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
