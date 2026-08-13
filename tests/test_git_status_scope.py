"""Tests for scoped git status pathspec builder."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from core.intelligence.dirty_classifier import (  # noqa: E402
    git_status_paths,
    git_status_scope_pathspecs,
)


def test_git_status_scope_pathspecs_minimal_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "main.py").write_text("x\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    (repo / "temp_repos").mkdir()

    specs = git_status_scope_pathspecs(repo)
    assert "src/" in specs
    assert "pyproject.toml" in specs
    assert "temp_repos/" not in specs


def test_git_status_paths_uses_scoped_git_command(monkeypatch, tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "run.py").write_text("pass\n", encoding="utf-8")

    captured: dict = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        result = MagicMock()
        result.returncode = 0
        result.stdout = " M src/main.py\n?? run.py\n"
        return result

    monkeypatch.setattr("core.intelligence.dirty_classifier.subprocess.run", fake_run)

    paths, stats = git_status_paths(repo)
    assert "src/main.py" in paths
    assert "run.py" in paths
    assert stats["dirty_count"] == 1
    assert stats["untracked_count"] == 1
    assert "status" in captured["cmd"]
    assert "--" in captured["cmd"]
    assert "temp_repos" not in " ".join(captured["cmd"])
