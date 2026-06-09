"""Classify repo paths into governed dirty buckets."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from core.projectscanner.file_cache import SCAN_EXCLUDE_DIR_NAMES

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

GIT_STATUS_SCOPE_DIRS: tuple[str, ...] = (
    "src",
    "scripts",
    "tests",
    "config",
    "docs",
    ".github",
)

GIT_STATUS_SCOPE_ROOT_FILES: tuple[str, ...] = (
    "run.py",
    "main.py",
    "standalone_scanner.py",
    "unified_compat.py",
    "pyproject.toml",
    "requirements.txt",
    "README.md",
    "CANONICAL.md",
    ".gitignore",
)

GIT_STATUS_MAX_PATHS = 5000
GIT_STATUS_TIMEOUT_SEC = 30


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


def git_status_scope_pathspecs(repo_root: Path) -> list[str]:
    """High-signal paths only — avoids full-repo status over temp_repos etc."""
    specs: list[str] = []
    for name in GIT_STATUS_SCOPE_DIRS:
        path = repo_root / name
        if path.is_dir():
            specs.append(f"{name}/")
        elif path.is_file():
            specs.append(name)
    for name in GIT_STATUS_SCOPE_ROOT_FILES:
        path = repo_root / name
        if path.is_file():
            specs.append(name)
    return specs


def _path_under_excluded_dir(rel_path: str) -> bool:
    parts = normalize_rel(rel_path).split("/")
    return any(part in SCAN_EXCLUDE_DIR_NAMES for part in parts if part)


def _parse_porcelain(stdout: str) -> tuple[list[str], dict[str, int]]:
    stats: dict[str, int] = {"dirty_count": 0, "untracked_count": 0, "truncated": 0}
    paths: list[str] = []
    for line in stdout.splitlines():
        if len(paths) >= GIT_STATUS_MAX_PATHS:
            stats["truncated"] = 1
            break
        if len(line) < 4:
            continue
        index = line[:2]
        entry = line[3:].strip()
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1].strip()
        rel = normalize_rel(entry)
        if _path_under_excluded_dir(rel):
            continue
        paths.append(rel)
        if index.strip() == "??":
            stats["untracked_count"] += 1
        else:
            stats["dirty_count"] += 1
    return paths, stats


def git_status_paths(repo_root: Path) -> tuple[list[str], dict[str, int]]:
    """Return (paths, stats) for scoped git status (not entire repo tree)."""
    stats: dict[str, int] = {"dirty_count": 0, "untracked_count": 0, "truncated": 0}
    pathspecs = git_status_scope_pathspecs(repo_root)
    if not pathspecs:
        return [], stats
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain", "--", *pathspecs],
            capture_output=True,
            text=True,
            timeout=GIT_STATUS_TIMEOUT_SEC,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return [], stats
    if proc.returncode != 0:
        return [], stats
    paths, parsed_stats = _parse_porcelain(proc.stdout)
    stats.update(parsed_stats)
    return paths, stats
