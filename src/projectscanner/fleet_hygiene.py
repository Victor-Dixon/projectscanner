"""Fleet hygiene evidence for branches and Git worktrees.

This module is intentionally observational. It records Git facts that downstream
governance can use; it does not delete branches, prune worktrees, or decide
promotion/retention policy.
"""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.intelligence.dirty_classifier import aggregate_dirty_classes, git_status_paths

SCHEMA = "projectscanner_fleet_hygiene_snapshot.v1"


class FleetHygieneError(RuntimeError):
    """Raised when a repository cannot be inspected safely."""


def _run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}"
        raise FleetHygieneError(f"git {' '.join(args)} failed for {repo}: {detail}")
    return proc


def _git_text(repo: Path, *args: str, check: bool = True) -> str:
    return _run_git(repo, *args, check=check).stdout.strip()


def _repo_root(path: Path | str) -> Path:
    candidate = Path(path).expanduser().resolve()
    if not candidate.exists():
        raise FleetHygieneError(f"repository path does not exist: {candidate}")
    root = _git_text(candidate, "rev-parse", "--show-toplevel", check=False)
    if not root:
        raise FleetHygieneError(f"not a Git worktree: {candidate}")
    return Path(root).resolve()


def _ref_exists(repo: Path, ref: str) -> bool:
    return _run_git(repo, "rev-parse", "--verify", "--quiet", ref, check=False).returncode == 0


def _resolve_canonical_branch(repo: Path, override: str | None = None) -> tuple[str, str]:
    if override:
        candidates = (override, f"refs/heads/{override}", f"refs/remotes/origin/{override}")
        for ref in candidates:
            if _ref_exists(repo, ref):
                resolved = override.removeprefix("origin/")
                canonical_ref = (
                    f"refs/heads/{resolved}"
                    if _ref_exists(repo, f"refs/heads/{resolved}")
                    else f"refs/remotes/origin/{resolved}"
                )
                return resolved, canonical_ref
        raise FleetHygieneError(f"canonical branch not found: {override}")

    origin_head = _git_text(
        repo,
        "symbolic-ref",
        "--quiet",
        "--short",
        "refs/remotes/origin/HEAD",
        check=False,
    )
    if origin_head.startswith("origin/"):
        branch = origin_head.removeprefix("origin/")
        local = f"refs/heads/{branch}"
        remote = f"refs/remotes/origin/{branch}"
        return branch, local if _ref_exists(repo, local) else remote

    for branch in ("master", "main"):
        local = f"refs/heads/{branch}"
        remote = f"refs/remotes/origin/{branch}"
        if _ref_exists(repo, local):
            return branch, local
        if _ref_exists(repo, remote):
            return branch, remote

    current = _git_text(repo, "branch", "--show-current", check=False)
    if current:
        return current, f"refs/heads/{current}"

    raise FleetHygieneError("unable to determine canonical branch; pass --canonical-branch")


def _ahead_behind(repo: Path, canonical_ref: str, candidate_ref: str) -> tuple[int | None, int | None]:
    proc = _run_git(
        repo,
        "rev-list",
        "--left-right",
        "--count",
        f"{canonical_ref}...{candidate_ref}",
        check=False,
    )
    if proc.returncode != 0:
        return None, None
    parts = proc.stdout.strip().split()
    if len(parts) != 2:
        return None, None
    try:
        behind, ahead = (int(parts[0]), int(parts[1]))
    except ValueError:
        return None, None
    return ahead, behind


def _merged_to_canonical(repo: Path, candidate_ref: str, canonical_ref: str) -> bool | None:
    proc = _run_git(repo, "merge-base", "--is-ancestor", candidate_ref, canonical_ref, check=False)
    if proc.returncode == 0:
        return True
    if proc.returncode == 1:
        return False
    return None


def _branch_rows(repo: Path, namespace: str) -> list[dict[str, str]]:
    fmt = "%(refname:short)%00%(objectname)%00%(committerdate:iso-strict)%00%(upstream:short)"
    out = _git_text(repo, "for-each-ref", f"--format={fmt}", namespace, check=False)
    rows: list[dict[str, str]] = []
    for line in out.splitlines():
        parts = line.split("\x00")
        if len(parts) != 4:
            continue
        name, sha, committed_at, upstream = parts
        rows.append(
            {
                "name": name,
                "sha": sha,
                "committed_at": committed_at,
                "upstream": upstream,
            }
        )
    return rows


def _branch_inventory(
    repo: Path,
    canonical_branch: str,
    canonical_ref: str,
    current_branch: str,
) -> dict[str, Any]:
    local_items: list[dict[str, Any]] = []
    for row in _branch_rows(repo, "refs/heads"):
        ref = f"refs/heads/{row['name']}"
        ahead, behind = _ahead_behind(repo, canonical_ref, ref)
        local_items.append(
            {
                **row,
                "is_current": row["name"] == current_branch,
                "is_canonical": row["name"] == canonical_branch,
                "ahead_of_canonical": ahead,
                "behind_canonical": behind,
                "merged_to_canonical": _merged_to_canonical(repo, ref, canonical_ref),
                "local_only": not bool(row["upstream"]),
            }
        )

    remote_items: list[dict[str, Any]] = []
    for row in _branch_rows(repo, "refs/remotes/origin"):
        if row["name"] == "origin/HEAD":
            continue
        short = row["name"].removeprefix("origin/")
        ref = f"refs/remotes/origin/{short}"
        ahead, behind = _ahead_behind(repo, canonical_ref, ref)
        remote_items.append(
            {
                "name": short,
                "remote_ref": row["name"],
                "sha": row["sha"],
                "committed_at": row["committed_at"],
                "is_canonical": short == canonical_branch,
                "ahead_of_canonical": ahead,
                "behind_canonical": behind,
                "merged_to_canonical": _merged_to_canonical(repo, ref, canonical_ref),
            }
        )

    local_items.sort(key=lambda row: row["name"])
    remote_items.sort(key=lambda row: row["name"])
    return {
        "local_count": len(local_items),
        "remote_count": len(remote_items),
        "local_only_count": sum(1 for row in local_items if row["local_only"]),
        "merged_noncanonical_local_count": sum(
            1 for row in local_items if not row["is_canonical"] and row["merged_to_canonical"] is True
        ),
        "merged_noncanonical_remote_count": sum(
            1 for row in remote_items if not row["is_canonical"] and row["merged_to_canonical"] is True
        ),
        "local": local_items,
        "remote": remote_items,
    }


def parse_worktree_porcelain(text: str) -> list[dict[str, Any]]:
    """Parse ``git worktree list --porcelain`` output into stable records."""

    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}

    def flush() -> None:
        nonlocal current
        if current:
            records.append(current)
            current = {}

    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if not line:
            flush()
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            if current:
                flush()
            current["path"] = value
        elif key == "HEAD":
            current["head"] = value
        elif key == "branch":
            current["branch_ref"] = value
            current["branch"] = value.removeprefix("refs/heads/")
        elif key in {"bare", "detached", "prunable"}:
            current[key] = True
            if value:
                current[f"{key}_reason"] = value
        elif key == "locked":
            current["locked"] = True
            if value:
                current["locked_reason"] = value
        else:
            current[key] = value or True

    flush()
    return records


def _worktree_inventory(repo: Path, canonical_branch: str) -> dict[str, Any]:
    raw = _git_text(repo, "worktree", "list", "--porcelain")
    records = parse_worktree_porcelain(raw)
    items: list[dict[str, Any]] = []

    for record in records:
        path = Path(str(record.get("path", ""))).resolve()
        exists = path.exists()
        bare = bool(record.get("bare", False))
        dirty_paths: list[str] = []
        status_stats = {"dirty_count": 0, "untracked_count": 0}
        dirty_classes: dict[str, int] = {}

        if exists and not bare:
            dirty_paths, status_stats = git_status_paths(path)
            dirty_classes = aggregate_dirty_classes(dirty_paths)

        branch = str(record.get("branch", ""))
        item = {
            "path": str(path),
            "head": str(record.get("head", "")),
            "branch": branch,
            "branch_ref": str(record.get("branch_ref", "")),
            "exists": exists,
            "is_canonical": branch == canonical_branch,
            "detached": bool(record.get("detached", False)),
            "bare": bare,
            "locked": bool(record.get("locked", False)),
            "locked_reason": str(record.get("locked_reason", "")),
            "prunable": bool(record.get("prunable", False)),
            "prunable_reason": str(record.get("prunable_reason", "")),
            "dirty_count": int(status_stats["dirty_count"]),
            "untracked_count": int(status_stats["untracked_count"]),
            "dirty_total": int(status_stats["dirty_count"]) + int(status_stats["untracked_count"]),
            "dirty_classes": dirty_classes,
        }
        items.append(item)

    items.sort(key=lambda row: row["path"])
    return {
        "count": len(items),
        "dirty_count": sum(1 for row in items if row["dirty_total"] > 0),
        "detached_count": sum(1 for row in items if row["detached"]),
        "locked_count": sum(1 for row in items if row["locked"]),
        "prunable_count": sum(1 for row in items if row["prunable"]),
        "items": items,
    }


def build_fleet_hygiene_snapshot(
    repo_path: Path | str,
    *,
    canonical_branch: str | None = None,
) -> dict[str, Any]:
    """Build branch/worktree evidence without mutating repository state."""

    repo = _repo_root(repo_path)
    canonical_name, canonical_ref = _resolve_canonical_branch(repo, canonical_branch)
    current_branch = _git_text(repo, "branch", "--show-current", check=False)
    head = _git_text(repo, "rev-parse", "HEAD")
    origin = _git_text(repo, "remote", "get-url", "origin", check=False)

    branches = _branch_inventory(repo, canonical_name, canonical_ref, current_branch)
    worktrees = _worktree_inventory(repo, canonical_name)

    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "repo": {
            "name": repo.name,
            "path": str(repo),
            "origin": origin,
            "head": head,
            "current_branch": current_branch,
            "canonical_branch": canonical_name,
            "canonical_ref": canonical_ref,
        },
        "branches": branches,
        "worktrees": worktrees,
        "signals": {
            "noncanonical_local_branch_count": max(0, branches["local_count"] - 1),
            "noncanonical_remote_branch_count": max(0, branches["remote_count"] - 1),
            "local_only_branch_count": branches["local_only_count"],
            "merged_noncanonical_local_count": branches["merged_noncanonical_local_count"],
            "merged_noncanonical_remote_count": branches["merged_noncanonical_remote_count"],
            "dirty_worktree_count": worktrees["dirty_count"],
            "detached_worktree_count": worktrees["detached_count"],
            "prunable_worktree_count": worktrees["prunable_count"],
        },
        "policy": {
            "decision_owner": "DreamVault",
            "mutation_owner": "CPC",
            "scanner_mutations_made": False,
        },
    }
