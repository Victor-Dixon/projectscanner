"""Regression: four-target ScanTarget/dict boundary must not AttributeError."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "src"))

from project_artifact_standards import expected_dir_for_target  # noqa: E402
from scan_targets import (  # noqa: E402
    as_scan_target,
    as_target_dict,
    make_local_target,
    target_summary,
    write_target_manifest,
)
from core.intelligence.authority_report import (  # noqa: E402
    build_authority_report,
    classify_repo,
)


def test_expected_dir_accepts_scan_target_and_dict(tmp_path: Path):
    repo = tmp_path / "projectscanner"
    repo.mkdir()
    target = make_local_target(repo)
    # Historically crashed: AttributeError: 'ScanTarget' object has no attribute 'get'
    path_from_obj = expected_dir_for_target(target)
    path_from_dict = expected_dir_for_target(as_target_dict(target))
    assert path_from_obj == path_from_dict
    assert "projectscanner" in str(path_from_obj)


def test_target_summary_accepts_dict_and_scan_target(tmp_path: Path):
    repo = tmp_path / "agent-tools"
    repo.mkdir()
    target = make_local_target(repo)
    # Historically crashed: AttributeError: 'dict' object has no attribute 'source_type'
    summary_obj = target_summary(target)
    summary_dict = target_summary(as_target_dict(target))
    assert summary_obj["name"] == "agent-tools"
    assert summary_dict["name"] == "agent-tools"
    assert summary_obj["source_type"] == summary_dict["source_type"]


def test_four_target_manifest_roundtrip_no_attribute_error(tmp_path: Path):
    names = ["Dream.os-Core", "Dream.os", "AgentTools", "projectscanner"]
    paths = []
    for name in names:
        p = tmp_path / name
        p.mkdir()
        (p / "README.md").write_text(f"# {name}\n", encoding="utf-8")
        paths.append(p)
    targets = [make_local_target(p) for p in paths]
    manifest = tmp_path / "targets.json"
    write_target_manifest(targets, manifest)
    raw = json.loads(manifest.read_text(encoding="utf-8"))["targets"]
    assert len(raw) == 4
    for item in raw:
        # dict form used by artifact standards / JSON consumers
        _ = expected_dir_for_target(item)
        _ = target_summary(item)
        _ = as_scan_target(item)


def test_classify_toolbelt_and_canonical(tmp_path: Path):
    core = tmp_path / "Dream.os-Core"
    core.mkdir()
    (core / "AGENTS.md").write_text(
        "Dream.os-Core owns runtime contracts and orchestration primitives.\n",
        encoding="utf-8",
    )
    tools = tmp_path / "agent-tools"
    tools.mkdir()
    (tools / "AGENTS.md").write_text(
        "AgentTools is the operator/control-plane toolbelt.\n",
        encoding="utf-8",
    )
    scanner = tmp_path / "projectscanner"
    scanner.mkdir()
    (scanner / "CONSOLIDATION_MANIFEST.md").write_text(
        "ProjectScanner owns scanning mechanics; toolbelt role.\n",
        encoding="utf-8",
    )
    variant = tmp_path / "Dream.os"
    variant.mkdir()
    (variant / "README.md").write_text("Legacy Dream.os variant / promotion candidate.\n", encoding="utf-8")

    peers = {p.name for p in (core, tools, scanner, variant)}
    assert classify_repo(repo=core, peer_names=peers)["classification"] == "canonical"
    assert classify_repo(repo=tools, peer_names=peers)["classification"] == "toolbelt"
    assert classify_repo(repo=scanner, peer_names=peers)["classification"] == "toolbelt"
    assert classify_repo(repo=variant, peer_names=peers)["classification"] == "variant"

    report = build_authority_report([core, variant, tools, scanner])
    assert report["schema"] == "projectscanner.portfolio_authority_report.v1"
    assert report["authority_scope"] == "controlled_scan_set"
    assert "portfolio-wide" in (report.get("authority_scope_note") or "")
    assert "Dream.os-Core" in report["summary"]["canonical"]
    assert "projectscanner" in report["summary"]["toolbelt"]
    assert "agent-tools" in report["summary"]["toolbelt"]
    assert report["auto_promote"] is False
    # Dream.os-Core entry uses scan-set-scoped recommendation, not portfolio promotion.
    core_row = next(r for r in report["repositories"] if r["name"] == "Dream.os-Core")
    assert core_row["promotion_recommendation"]["action"] == "KEEP_CANONICAL_IN_SCAN_SET"
    assert core_row["promotion_recommendation"]["auto_promote"] is False
