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
from core.intelligence.packet_validation import (  # noqa: E402
    intelligence_packet_canonical_sha256,
    validate_intelligence_packet,
)
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


def _make_minimal_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "sample_repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_x.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    (repo / "runtime" / "state").mkdir(parents=True)
    return repo


def test_build_packet_shape_and_validation(monkeypatch, tmp_path):
    repo = _make_minimal_repo(tmp_path)

    # Keep tests fast + deterministic: don't shell out to git for unit tests.
    monkeypatch.setattr(
        "core.intelligence.packet_builder.git_status_paths",
        lambda _repo_root: (["src/main.py", "tests/test_x.py"], {"dirty_count": 1, "untracked_count": 1}),
    )
    monkeypatch.setattr(
        "core.intelligence.packet_builder._git_meta",
        lambda _repo_root: {"is_repo": False, "branch": "", "dirty_count": 0, "untracked_count": 0},
    )

    builder = IntelligencePacketBuilder(repo)
    packet = builder.build()
    assert packet["schema"] == "projectscanner_intelligence_packet.v1"
    assert packet["repo"] == repo.name
    assert "dirty_classes" in packet
    assert packet["risk_level"] in ("low", "medium", "high", "critical")
    assert isinstance(packet["candidate_lanes"], list)
    validate_intelligence_packet(packet)
    assert isinstance(packet.get("canonical_sha256"), str)
    assert len(packet["canonical_sha256"]) == 64


def test_write_packet_is_deterministic_and_self_hashes(monkeypatch, tmp_path):
    repo = _make_minimal_repo(tmp_path)
    monkeypatch.setattr(
        "core.intelligence.packet_builder.git_status_paths",
        lambda _repo_root: (["src/main.py"], {"dirty_count": 1, "untracked_count": 0}),
    )
    monkeypatch.setattr(
        "core.intelligence.packet_builder._git_meta",
        lambda _repo_root: {"is_repo": False, "branch": "", "dirty_count": 0, "untracked_count": 0},
    )

    builder = IntelligencePacketBuilder(repo)
    out = builder.write(repo / "runtime" / "state" / "intelligence_packet.v1.json")
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "projectscanner_intelligence_packet.v1"
    validate_intelligence_packet(data)
    assert data.get("canonical_sha256") == intelligence_packet_canonical_sha256(data)

    # canonical hash stable across runs (generated_at changes)
    a = builder.build()
    b = builder.build()
    assert a["canonical_sha256"] == b["canonical_sha256"]


def test_repo_graph_builder_smoke(tmp_path):
    # Keep repo graph tests separate from packet hardening;
    # this just asserts the builder can run.
    sys.path.insert(0, str(_ROOT / "src"))
    from core.intelligence.repo_graph import RepoGraphBuilder  # noqa: E402

    builder = RepoGraphBuilder(_ROOT)
    graph = builder.build()
    assert graph["schema"] == "projectscanner_repo_graph.v1"
