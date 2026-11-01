from __future__ import annotations

from collections import defaultdict
from typing import Any


def host_graph(flows: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: dict[str, dict[str, float | int | str]] = {}
    edges: dict[tuple[str, str], dict[str, float | int]] = defaultdict(
        lambda: {"flow_count": 0, "bytes_total": 0, "duration_total": 0.0}
    )
    for flow in flows:
        source, target = str(flow["host_hash"]), str(flow["peer_hash"])
        edge = edges[(source, target)]
        edge["flow_count"] += 1
        edge["bytes_total"] += int(flow.get("bytes_total", 0))
        edge["duration_total"] += float(flow.get("duration_s", 0))
        nodes.setdefault(source, {"id": source, "degree": 0, "flow_count": 0})
        nodes.setdefault(target, {"id": target, "degree": 0, "flow_count": 0})
        nodes[source]["flow_count"] += 1
        nodes[source]["degree"] += 1
        nodes[target]["degree"] += 1
    return {
        "nodes": list(nodes.values()),
        "edges": [
            {"source": source, "target": target, **values}
            for (source, target), values in edges.items()
        ],
    }
