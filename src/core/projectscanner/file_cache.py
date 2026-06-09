"""File-hash cache policy: exclusions, canonical path, legacy quarantine."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Align with .gitignore — skipped anywhere in a relative path.
SCAN_EXCLUDE_DIR_NAMES: frozenset[str] = frozenset(
    {
        "__pycache__",
        "node_modules",
        "migrations",
        "build",
        "target",
        ".git",
        "coverage",
        "chrome_profile",
        "logs",
        "venv",
        "env",
        ".env",
        ".venv",
        "virtualenv",
        "ENV",
        "VENV",
        ".ENV",
        ".VENV",
        "python-env",
        "python-venv",
        "py-env",
        "py-venv",
        "envs",
        "conda-env",
        ".conda-env",
        ".poetry",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "data",
        "temp_repos",
        "temp_scan",
        "temp_github_scan",
        "temp_github_deploy",
        "github_library",
        "github_library_enhanced",
        "archive",
        "_archive",
        "imports",
    }
)

LEGACY_CACHE_FILENAMES: tuple[str, ...] = (
    "dependency_cache.json",
    ".dependency_cache.json",
)

CANONICAL_CACHE_FILENAME = ".projectscanner_cache.json"
DEFAULT_MAX_CACHE_ENTRIES = 15_000


def _normalize_rel(rel_path: str) -> str:
    return rel_path.replace("\\", "/").lstrip("./")


def is_excluded_cache_key(rel_path: str) -> bool:
    """True when any path segment is a scan-excluded directory name."""
    parts = _normalize_rel(rel_path).split("/")
    return any(part in SCAN_EXCLUDE_DIR_NAMES for part in parts if part)


def is_valid_cache_entry(value: Any) -> bool:
    """Cache hits require mtime+size (legacy hash-only rows are invalid)."""
    if not isinstance(value, dict):
        return False
    mtime = value.get("mtime")
    size = value.get("size")
    if mtime is None or size is None:
        return False
    try:
        float(mtime)
        int(size)
    except (TypeError, ValueError):
        return False
    return True


def normalize_cache_entry(value: dict[str, Any]) -> dict[str, str]:
    entry: dict[str, str] = {"mtime": value["mtime"], "size": value["size"]}
    if "hash" in value and value["hash"] is not None:
        entry["hash"] = str(value["hash"])
    return entry


def prune_file_cache(
    cache: Dict[str, Any],
    *,
    max_entries: int = DEFAULT_MAX_CACHE_ENTRIES,
) -> Dict[str, Dict[str, str]]:
    """Drop excluded/invalid keys; cap size with stable key order."""
    cleaned: Dict[str, Dict[str, str]] = {}
    for key, value in cache.items():
        if not isinstance(key, str) or is_excluded_cache_key(key):
            continue
        if is_valid_cache_entry(value):
            cleaned[key] = normalize_cache_entry(value)
    if len(cleaned) <= max_entries:
        return cleaned
    keys = sorted(cleaned.keys())[:max_entries]
    return {k: cleaned[k] for k in keys}


def _canonical_cache_path(output_dir: Path) -> Path:
    return output_dir / CANONICAL_CACHE_FILENAME


def _legacy_quarantine_dir(output_dir: Path) -> Path:
    return output_dir / "runtime" / "cache"


def quarantine_legacy_caches(output_dir: Path) -> list[Path]:
    """
    Move legacy root cache files aside without parsing them.
    Any dependency_cache.json at scan output root is quarantined (all sizes).
    """
    moved: list[Path] = []
    quarantine_dir = _legacy_quarantine_dir(output_dir)
    for idx, name in enumerate(LEGACY_CACHE_FILENAMES):
        legacy = output_dir / name
        if not legacy.is_file():
            continue
        try:
            size = legacy.stat().st_size
        except OSError:
            continue
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        dest = quarantine_dir / (
            "dependency_cache.legacy.bak" if idx == 0 else "dependency_cache_dot.legacy.bak"
        )
        if dest.exists():
            dest.unlink()
        shutil.move(str(legacy), str(dest))
        logger.info("Quarantined legacy cache %s (%d bytes) -> %s", legacy, size, dest)
        moved.append(dest)
    return moved


def invalidate_file_cache(output_dir: Path) -> None:
    """Remove canonical cache (operator --refresh-cache)."""
    output_dir = output_dir.resolve()
    quarantine_legacy_caches(output_dir)
    path = _canonical_cache_path(output_dir)
    if path.is_file():
        path.unlink()
        logger.info("Removed canonical cache %s", path)


def load_file_cache(output_dir: Path, *, refresh: bool = False) -> Dict[str, Dict[str, str]]:
    """Load canonical cache; quarantine legacy files first; strip hash-only rows."""
    output_dir = output_dir.resolve()
    quarantine_legacy_caches(output_dir)
    if refresh:
        invalidate_file_cache(output_dir)
        return {}
    path = _canonical_cache_path(output_dir)
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        logger.warning("Could not load cache from %s, starting fresh", path)
        return {}
    if not isinstance(data, dict):
        return {}
    raw_count = len(data)
    pruned = prune_file_cache(data)
    dropped = raw_count - len(pruned)
    if dropped:
        logger.info(
            "Dropped %d invalid/stale cache entries from %s (%d valid remain)",
            dropped,
            path.name,
            len(pruned),
        )
    return pruned


def save_file_cache(output_dir: Path, cache: Dict[str, Dict[str, str]]) -> None:
    """Prune and write canonical cache only."""
    output_dir = output_dir.resolve()
    pruned = prune_file_cache(cache)
    path = _canonical_cache_path(output_dir)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(pruned, f, indent=2)
    except Exception as exc:
        logger.error("Failed to save file cache: %s", exc)
