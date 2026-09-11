from __future__ import annotations

import json
from pathlib import Path

from build_project_artifacts import artifact_payloads_for_target
from project_artifact_standards import expected_dir_for_target
from scan_targets import (
    as_scan_target,
    as_target_dict,
    make_local_target,
    target_summary,
    write_target_manifest,
)


def test_expected_dir_and_payload_builder_accept_scan_target(tmp_path: Path):
    repo = tmp_path / "projectscanner"
    repo.mkdir()
    target = make_local_target(repo)

    path_from_obj = expected_dir_for_target(target)
    path_from_dict = expected_dir_for_target(as_target_dict(target))
    assert path_from_obj == path_from_dict

    payloads = artifact_payloads_for_target(target)
    assert payloads["scan_target.json"]["target"]["name"] == "projectscanner"


def test_target_summary_accepts_dict_and_scan_target(tmp_path: Path):
    repo = tmp_path / "agent-tools"
    repo.mkdir()
    target = make_local_target(repo)

    summary_obj = target_summary(target)
    summary_dict = target_summary(as_target_dict(target))
    assert summary_obj["name"] == summary_dict["name"] == "agent-tools"
    assert summary_obj["source_type"] == summary_dict["source_type"]


def test_four_target_manifest_roundtrip_accepts_both_shapes(tmp_path: Path):
    names = ["Dream.os-Core", "Dream.os", "AgentTools", "projectscanner"]
    targets = []
    for name in names:
        path = tmp_path / name
        path.mkdir()
        targets.append(make_local_target(path))

    manifest = tmp_path / "targets.json"
    write_target_manifest(targets, manifest)
    raw = json.loads(manifest.read_text(encoding="utf-8"))["targets"]

    assert len(raw) == 4
    for item in raw:
        _ = expected_dir_for_target(item)
        _ = target_summary(item)
        normalized = as_scan_target(item)
        assert normalized.name
