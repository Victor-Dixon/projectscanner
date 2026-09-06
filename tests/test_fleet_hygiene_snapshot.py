"""Tests for branch/worktree fleet hygiene evidence."""

from __future__ import annotations

import subprocess
from pathlib import Path

from projectscanner.fleet_hygiene import (
    SCHEMA,
    build_fleet_hygiene_snapshot,
    parse_worktree_porcelain,
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _init_repo(repo: Path) -> None:
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "projectscanner@example.invalid")
    _git(repo, "config", "user.name", "ProjectScanner Test")
    _git(repo, "branch", "-M", "master")
    (repo / "README.md").write_text("baseline\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "baseline")


def test_parse_worktree_porcelain_handles_flags_and_reasons():
    text = """worktree /repo
HEAD abc123
branch refs/heads/master

worktree /repo-wt
HEAD def456
detached
locked operator hold

"""
    rows = parse_worktree_porcelain(text)
    assert rows == [
        {
            "path": "/repo",
            "head": "abc123",
            "branch_ref": "refs/heads/master",
            "branch": "master",
        },
        {
            "path": "/repo-wt",
            "head": "def456",
            "detached": True,
            "locked": True,
            "locked_reason": "operator hold",
        },
    ]


def test_snapshot_inventory_reports_branch_and_dirty_worktree_evidence(tmp_path):
    repo = tmp_path / "demo"
    _init_repo(repo)

    _git(repo, "checkout", "-b", "feat/demo")
    (repo / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(repo, "add", "feature.py")
    _git(repo, "commit", "-m", "feature")
    _git(repo, "checkout", "master")

    worktree = tmp_path / "demo-worktree"
    _git(repo, "worktree", "add", "-b", "fix/worktree", str(worktree), "master")
    (worktree / "scratch.py").write_text("DIRTY = True\n", encoding="utf-8")

    snapshot = build_fleet_hygiene_snapshot(repo, canonical_branch="master")

    assert snapshot["schema"] == SCHEMA
    assert snapshot["repo"]["canonical_branch"] == "master"
    assert snapshot["policy"]["scanner_mutations_made"] is False

    branches = snapshot["branches"]
    assert branches["local_count"] == 3
    by_name = {row["name"]: row for row in branches["local"]}
    assert by_name["master"]["is_canonical"] is True
    assert by_name["feat/demo"]["ahead_of_canonical"] == 1
    assert by_name["feat/demo"]["behind_canonical"] == 0
    assert by_name["feat/demo"]["merged_to_canonical"] is False

    worktrees = snapshot["worktrees"]
    assert worktrees["count"] == 2
    assert worktrees["dirty_count"] == 1
    dirty = next(row for row in worktrees["items"] if row["path"] == str(worktree.resolve()))
    assert dirty["branch"] == "fix/worktree"
    assert dirty["dirty_total"] == 1
    assert dirty["dirty_classes"]["source_code"] == 1


def test_snapshot_rejects_non_git_path(tmp_path):
    target = tmp_path / "plain"
    target.mkdir()

    try:
        build_fleet_hygiene_snapshot(target)
    except RuntimeError as exc:
        assert "not a Git worktree" in str(exc)
    else:
        raise AssertionError("expected non-git path to be rejected")
