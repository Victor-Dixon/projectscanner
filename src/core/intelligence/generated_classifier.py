"""Detect generated, runtime, and experiment boundary signals."""

from __future__ import annotations

import re
from pathlib import Path

GENERATED_MARKERS = (
    ".projectscanner_cache.json",
    "dependency_cache.json",
    "project_analysis_",
    "chatgpt_project_context_",
)

EXPERIMENT_MARKERS = (
    "archive/untracked_overlay",
    "experiments/",
    "experiment/",
    "variant/",
    "overlay/",
    "sandbox/",
    "salvage",
)

RUNTIME_NOISE_DIRS = frozenset(
    {
        "runtime/targets",
        "runtime/reports",
        "runtime/project_artifacts",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
    }
)


def is_generated_artifact(rel_path: str) -> bool:
    rel = rel_path.replace("\\", "/")
    if any(m in rel for m in GENERATED_MARKERS):
        return True
    if re.search(r"runtime/(targets|reports|project_artifacts)/", rel, re.I):
        return True
    if rel.endswith(".pyc") or rel.endswith(".min.js"):
        return True
    return False


def detect_experiment_boundary(repo_root: Path, dirty_paths: list[str]) -> dict:
    signals: list[str] = []
    name_lower = repo_root.name.lower()
    if any(x in name_lower for x in ("variant", "experiment", "overlay", "salvage")):
        signals.append("repo_name_experiment_hint")
    for p in dirty_paths:
        norm = p.replace("\\", "/")
        for marker in EXPERIMENT_MARKERS:
            if marker.rstrip("/") in norm:
                signals.append(f"path:{marker}")
                break
    archive = repo_root / "archive"
    if archive.is_dir():
        signals.append("archive_tree_present")
    return {
        "is_experiment": len(signals) > 0,
        "signals": sorted(set(signals)),
    }


def runtime_noise_ratio(dirty_classes: dict[str, int]) -> float:
    noise_keys = {
        "generated_reports",
        "generated_runtime",
        "generated_artifacts",
        "runtime_state",
        "archive_material",
    }
    total = sum(dirty_classes.values()) or 1
    noise = sum(dirty_classes.get(k, 0) for k in noise_keys)
    return noise / total
