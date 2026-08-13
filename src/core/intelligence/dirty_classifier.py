"""Classify repo paths into governed dirty buckets."""

from __future__ import annotations

import re
from pathlib import Path

# Ordered: first match wins
DIR_CLASS_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("runtime_state", re.compile(r"(^|/)(runtime/state|runtime/leases|runtime/cockpit)(/|$)", re.I)),
    ("generated_reports", re.compile(r"(^|/)(data/reports|report/|reports/|\.projectscanner_cache)(/|$)", re.I)),
    ("generated_runtime", re.compile(r"(^|/)(runtime/targets|runtime/reports|runtime/project_artifacts|__pycache__|\.pytest_cache|node_modules|dist/|build/)(/|$)", re.I)),
    ("archive_material", re.compile(r"(^|/)(archive/|_archive/|imports/)(/|$)", re.I)),
    ("experiment_overlay", re.compile(r"(^|/)(experiments?/|overlay/|variant/|sandbox/)(/|$)", re.I)),
    ("documentation", re.compile(r"(^|/)docs(/|$)|\.md$|\.rst$", re.I)),
    ("configuration", re.compile(r"(^|/)(\.github/|\.vscode/|config/|_ops/)(/|$)|\.(ya?ml|toml|ini|cfg)$", re.I)),
    ("tests", re.compile(r"(^|/)(tests?/|test_)|(^|/)tests\.", re.I)),
    ("source_code", re.compile(r"\.(py|rs|js|ts|tsx|jsx|go|java|cs|cpp|h)$", re.I)),
)

EXT_GENERATED = re.compile(
    r"\.(json|log|sqlite3?|db|cache|pyc|min\.js|map)$|_cache\.json$|\.generated\.",
    re.I,
)


def normalize_rel(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def classify_path(rel_path: str) -> str:
    rel = normalize_rel(rel_path)
    if rel.startswith("runtime/state/intelligence_packet"):
        return "intelligence_artifact"
    for name, pattern in DIR_CLASS_RULES:
        if pattern.search(rel):
            return name
    if EXT_GENERATED.search(rel):
        return "generated_artifacts"
    return "unclassified"


def aggregate_dirty_classes(paths: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for p in paths:
        bucket = classify_path(p)
        counts[bucket] = counts.get(bucket, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: (-x[1], x[0])))


def git_status_paths(repo_root: Path) -> tuple[list[str], dict[str, int]]:
    """Return (paths, stats) where stats has dirty_count and untracked_count."""
    import subprocess

    stats = {"dirty_count": 0, "untracked_count": 0}
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return [], stats
    if proc.returncode != 0:
        return [], stats
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        index = line[:2]
        entry = line[3:].strip()
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1].strip()
        paths.append(normalize_rel(entry))
        if index.strip() == "??":
            stats["untracked_count"] += 1
        else:
            stats["dirty_count"] += 1
    return paths, stats
