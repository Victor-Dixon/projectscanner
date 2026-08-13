"""Tests for file cache policy helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from core.projectscanner.file_cache import (  # noqa: E402
    is_excluded_cache_key,
    is_valid_cache_entry,
    load_file_cache,
    prune_file_cache,
    quarantine_legacy_caches,
)


def test_is_excluded_cache_key_temp_repos():
    assert is_excluded_cache_key("temp_repos/foo/bar.py")
    assert is_excluded_cache_key(r"temp_scan\x\y.py")
    assert not is_excluded_cache_key("src/core/foo.py")


def test_is_valid_cache_entry_requires_mtime_and_size():
    assert is_valid_cache_entry({"mtime": 1.0, "size": 100})
    assert not is_valid_cache_entry({"hash": "abc"})
    assert not is_valid_cache_entry({"mtime": 1.0})


def test_prune_file_cache_drops_excluded_invalid_and_caps():
    cache = {
        "src/a.py": {"mtime": 1.0, "size": 10},
        "temp_repos/clone/a.py": {"mtime": 2.0, "size": 20},
        "scripts/b.py": {"hash": "legacy-only"},
        "scripts/c.py": {"mtime": 3.0, "size": 30},
    }
    pruned = prune_file_cache(cache, max_entries=2)
    assert "temp_repos/clone/a.py" not in pruned
    assert "scripts/b.py" not in pruned
    assert len(pruned) == 2
    assert "src/a.py" in pruned
    assert "scripts/c.py" in pruned


def test_quarantine_legacy_cache_any_size(tmp_path: Path):
    legacy = tmp_path / "dependency_cache.json"
    legacy.write_text('{"src/a.py": {"hash": "x"}}', encoding="utf-8")
    moved = quarantine_legacy_caches(tmp_path)
    assert len(moved) == 1
    assert not legacy.exists()
    assert (tmp_path / "runtime" / "cache" / "dependency_cache.legacy.bak").is_file()


def test_quarantine_legacy_huge_cache(tmp_path: Path):
    legacy = tmp_path / "dependency_cache.json"
    legacy.write_text('{"x": ' + ("0" * 600_000) + "}", encoding="utf-8")
    moved = quarantine_legacy_caches(tmp_path)
    assert len(moved) == 1
    assert not legacy.exists()


def test_load_file_cache_uses_canonical_only(tmp_path: Path):
    canonical = tmp_path / ".projectscanner_cache.json"
    canonical.write_text(
        json.dumps(
            {
                "src/foo.py": {"mtime": 1.0, "size": 12},
                "src/stale.py": {"hash": "legacy"},
            }
        ),
        encoding="utf-8",
    )
    loaded = load_file_cache(tmp_path)
    assert "src/foo.py" in loaded
    assert "src/stale.py" not in loaded


def test_load_file_cache_refresh(tmp_path: Path):
    canonical = tmp_path / ".projectscanner_cache.json"
    canonical.write_text(json.dumps({"src/foo.py": {"mtime": 1.0, "size": 1}}), encoding="utf-8")
    loaded = load_file_cache(tmp_path, refresh=True)
    assert loaded == {}
    assert not canonical.exists()
