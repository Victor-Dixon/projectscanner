"""Tests for observability kernel intelligence packet."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from core.intelligence.dirty_classifier import aggregate_dirty_classes, classify_path  # noqa: E402
from core.intelligence.packet_builder import IntelligencePacketBuilder  # noqa: E402
from core.intelligence.repo_graph import RepoGraphBuilder  # noqa: E402


def test_classify_runtime_state():
    assert classify_path("runtime/state/foo.json") == "runtime_state"


def test_classify_source_code():
    assert classify_path("src/core/foo.py") == "source_code"


def test_aggregate_dirty_classes():
    paths = ["runtime/state/x.json", "src/a.py", "data/reports/r.md"]
    counts = aggregate_dirty_classes(paths)
    assert counts["runtime_state"] == 1
    assert counts["source_code"] == 1
    assert counts["generated_reports"] == 1


def test_build_packet_for_projectscanner(tmp_path):
    # Use real projectscanner root when available
    root = _ROOT
    builder = IntelligencePacketBuilder(root)
    packet = builder.build()
    assert packet["schema"] == "projectscanner_intelligence_packet.v1"
    assert packet["repo"] == root.name
    assert "dirty_classes" in packet
    assert packet["risk_level"] in ("low", "medium", "high", "critical")
    assert isinstance(packet["candidate_lanes"], list)


def test_write_packet(tmp_path):
    builder = IntelligencePacketBuilder(_ROOT)
    out = builder.write(tmp_path / "runtime" / "state" / "intelligence_packet.v1.json")
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "projectscanner_intelligence_packet.v1"


def test_repo_graph_builder():
    builder = RepoGraphBuilder(_ROOT)
    graph = builder.build()
    assert graph["schema"] == "projectscanner_repo_graph.v1"
    assert "DreamVault" in graph["nodes"]
    assert "projectscanner" in graph["nodes"]
    assert any(e["from"] == "projectscanner" for e in graph["edges"])
