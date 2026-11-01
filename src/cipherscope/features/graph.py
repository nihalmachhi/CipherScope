from __future__ import annotations

from collections import defaultdict
from typing import Any


def host_graph(flows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build an undirected host graph from stored flow metadata."""
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {"flow_count": 0, "bytes_total": 0, "duration_total": 0.0}
    )
    for flow in flows:
        source, target = str(flow["host_hash"]), str(flow["peer_hash"])
        key = (source, target) if source <= target else (target, source)
        edge = edges[key]
        edge["flow_count"] += 1
        edge["bytes_total"] += int(flow.get("bytes_total", 0))
        edge["duration_total"] += float(flow.get("duration_s", 0))
        nodes.setdefault(source, {"id": source, "degree": 0, "flow_count": 0})
        nodes.setdefault(target, {"id": target, "degree": 0, "flow_count": 0})
        nodes[source]["flow_count"] += 1
        nodes[target]["flow_count"] += 1
        if source != target:
            nodes[source]["degree"] += 1
            nodes[target]["degree"] += 1
    return {
        "nodes": list(nodes.values()),
        "edges": [
            {"source": source, "target": target, **values}
            for (source, target), values in edges.items()
        ],
    }
