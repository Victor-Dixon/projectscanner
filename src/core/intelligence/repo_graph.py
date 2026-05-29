"""Ecosystem repo graph — ownership boundaries and relationships."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .manifest_paths import repo_graph_path

# Canonical ecosystem ontology (agents consume this, not hallucinated boundaries)
ECOSYSTEM_NODES: dict[str, dict[str, Any]] = {
    "DreamVault": {
        "role": "governance_and_memory_layer",
        "owns": ["governance", "runtime/tasks", "runtime/contracts", "data/reports"],
        "consumes": ["projectscanner_intelligence_packet.v1", "dreamos.runtime_packet.v1"],
        "path_hints": ["DreamVault", "Projects/DreamVault"],
    },
    "projectscanner": {
        "role": "ecosystem_sensor_layer",
        "owns": [
            "repo intelligence",
            "repo topology",
            "ecosystem graph",
            "intelligence packets",
        ],
        "emits": ["projectscanner_intelligence_packet.v1", "repo_graph.json"],
        "path_hints": ["projectscanner"],
    },
    "AgentTools": {
        "role": "operator_control_plane",
        "owns": ["MCP", "integrations", "dashboards"],
        "consumes": ["projectscanner_intelligence_packet.v1"],
        "path_hints": ["AgentTools"],
    },
    "Dream.os-Core": {
        "role": "orchestration_primitives",
        "owns": ["runtime contracts", "orchestration primitives"],
        "path_hints": ["Dream.os-Core", "DreamOS", "Victor.os"],
    },
    "DreamSync": {
        "role": "distributed_transport",
        "owns": ["transport", "leasing"],
        "path_hints": ["DreamSync"],
    },
    "PublicationRouter": {
        "role": "operational_visibility",
        "owns": ["outbound publication", "surface adapters"],
        "consumes": ["dreamos.runtime_packet.v1"],
        "path_hints": ["DreamVault"],
    },
}

ECOSYSTEM_EDGES: list[dict[str, str]] = [
    {"from": "projectscanner", "to": "DreamVault", "relation": "feeds_governance"},
    {"from": "projectscanner", "to": "Dream.os-Core", "relation": "feeds_orchestration"},
    {"from": "projectscanner", "to": "AgentTools", "relation": "feeds_operator_plane"},
    {"from": "DreamVault", "to": "Dream.os-Core", "relation": "governs_execution"},
    {"from": "Dream.os-Core", "to": "DreamSync", "relation": "uses_transport"},
    {"from": "Dream.os-Core", "to": "PublicationRouter", "relation": "emits_runtime_packets"},
    {"from": "DreamVault", "to": "PublicationRouter", "relation": "promotes_closeouts"},
]


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class RepoGraphBuilder:
    """Build and persist runtime/state/repo_graph.json."""

    def __init__(self, projectscanner_root: Path | str):
        self.root = Path(projectscanner_root).resolve()

    def build(self, discovered_repos: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        repos = discovered_repos or []
        return {
            "schema": "projectscanner_repo_graph.v1",
            "generated_at": utc_now(),
            "generator": "projectscanner",
            "generator_root": str(self.root),
            "nodes": ECOSYSTEM_NODES,
            "edges": ECOSYSTEM_EDGES,
            "discovered_repos": repos,
            "operating_model": {
                "sensor_layer": "projectscanner",
                "governance_layer": "DreamVault",
                "execution_layer": ["Cursor", "Ollama", "Dream.os-Core"],
                "intelligence_flow": [
                    "filesystem",
                    "projectscanner normalization",
                    "governance contracts",
                    "LLM reasoning",
                    "deterministic execution",
                ],
            },
        }

    def write(self, out_path: Path | None = None) -> Path:
        graph = self.build()
        target = out_path or repo_graph_path(self.root)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        return target


def build_repo_graph(projectscanner_root: Path | str, out_path: Path | None = None) -> Path:
    return RepoGraphBuilder(projectscanner_root).write(out_path)
