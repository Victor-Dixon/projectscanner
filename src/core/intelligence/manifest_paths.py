"""Canonical paths for intelligence artifacts."""

from __future__ import annotations

from pathlib import Path

PACKET_SCHEMA = "projectscanner_intelligence_packet.v1"
PACKET_FILENAME = "intelligence_packet.v1.json"
REPO_GRAPH_FILENAME = "repo_graph.json"


def packet_path_for_repo(repo_root: Path) -> Path:
    return repo_root.resolve() / "runtime" / "state" / PACKET_FILENAME


def repo_graph_path(projectscanner_root: Path) -> Path:
    return projectscanner_root.resolve() / "runtime" / "state" / REPO_GRAPH_FILENAME


def ecosystem_artifacts_dir(projectscanner_root: Path) -> Path:
    return projectscanner_root.resolve() / "runtime" / "project_artifacts"
