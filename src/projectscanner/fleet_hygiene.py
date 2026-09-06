"""Fleet hygiene intelligence built from reusable AgentTools Git facts.

ProjectScanner owns aggregation and interpretation in this lane. Generic Git
inspection lives in ``agent_tools.repo``. This module remains read-only: it does
not delete branches, prune worktrees, or apply repository policy.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.intelligence.dirty_classifier import aggregate_dirty_classes

SCHEMA = "projectscanner_fleet_hygiene_snapshot.v1"


class FleetHygieneError(RuntimeError):
    """Raised when repository hygiene evidence cannot be built safely."""


def _load_repo_tools():
    try:
        from agent_tools.repo import (
            GitRepoToolError,
            compare_refs,
            list_branches,
            list_worktrees,
            remote_default_branch,
            repo_identity,
        )
    except ImportError as exc:
        raise FleetHygieneError(
            "fleet hygiene requires AgentTools repo primitives; "
            "install projectscanner with the [hygiene] extra"
        ) from exc

    return {
        "error": GitRepoToolError,
        "compare_refs": compare_refs,
        "list_branches": list_branches,
        "list_worktrees": list_worktrees,
        "remote_default_branch": remote_default_branch,
        "repo_identity": repo_identity,
    }


def _committed_at(timestamp: int | None) -> str:
    if timestamp is None:
        return ""
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


def _branch_lookup(branches: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    local = {row["name"]: row for row in branches["local"]}
    remote = {row["name"]: row for row in branches["remote_branches"]}
    return local, remote


def _canonical_ref(
    *,
    identity: dict[str, Any],
    branches: dict[str, Any],
    remote_default: dict[str, str],
    override: str | None,
) -> tuple[str, str]:
    local, remote = _branch_lookup(branches)

    def resolve(name: str) -> tuple[str, str] | None:
        normalized = name.removeprefix("origin/")
        if normalized in local:
            return normalized, str(local[normalized]["ref"])
        if normalized in remote:
            return normalized, str(remote[normalized]["ref"])
        return None

    if override:
        resolved = resolve(override)
        if resolved is None:
            raise FleetHygieneError(f"canonical branch not found: {override}")
        return resolved

    if remote_default.get("branch"):
        resolved = resolve(remote_default["branch"])
        if resolved is not None:
            return resolved

    for fallback in ("master", "main"):
        resolved = resolve(fallback)
        if resolved is not None:
            return resolved

    current = str(identity.get("current_branch", ""))
    if current:
        resolved = resolve(current)
        if resolved is not None:
            return resolved

    raise FleetHygieneError("unable to determine canonical branch; pass --canonical-branch")


def _decorate_branches(
    repo: Path,
    branches: dict[str, Any],
    *,
    canonical_branch: str,
    canonical_ref: str,
    current_branch: str,
    compare_refs,
) -> dict[str, Any]:
    local_items: list[dict[str, Any]] = []
    for row in branches["local"]:
        comparison = compare_refs(repo, base=canonical_ref, head=row["ref"])
        local_items.append(
            {
                "name": row["name"],
                "sha": row["sha"],
                "committed_at": _committed_at(row.get("commit_timestamp")),
                "upstream": row.get("upstream", ""),
                "is_current": row["name"] == current_branch,
                "is_canonical": row["name"] == canonical_branch,
                "ahead_of_canonical": comparison["ahead"],
                "behind_canonical": comparison["behind"],
                "merged_to_canonical": comparison["head_is_ancestor_of_base"],
                "local_only": not bool(row.get("upstream")),
            }
        )

    remote_items: list[dict[str, Any]] = []
    for row in branches["remote_branches"]:
        comparison = compare_refs(repo, base=canonical_ref, head=row["ref"])
        remote_items.append(
            {
                "name": row["name"],
                "remote_ref": f"origin/{row['name']}",
                "sha": row["sha"],
                "committed_at": _committed_at(row.get("commit_timestamp")),
                "is_canonical": row["name"] == canonical_branch,
                "ahead_of_canonical": comparison["ahead"],
                "behind_canonical": comparison["behind"],
                "merged_to_canonical": comparison["head_is_ancestor_of_base"],
            }
        )

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


def _decorate_worktrees(raw: dict[str, Any], canonical_branch: str) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for row in raw["items"]:
        paths = [entry["path"] for entry in row.get("status_entries", [])]
        items.append(
            {
                "path": row["path"],
                "head": row["head"],
                "branch": row["branch"],
                "branch_ref": row["branch_ref"],
                "exists": row["exists"],
                "is_canonical": row["branch"] == canonical_branch,
                "detached": row["detached"],
                "bare": row["bare"],
                "locked": row["locked"],
                "locked_reason": row["locked_reason"],
                "prunable": row["prunable"],
                "prunable_reason": row["prunable_reason"],
                "dirty_count": row["dirty_count"],
                "untracked_count": row["untracked_count"],
                "dirty_total": row["dirty_total"],
                "dirty_classes": aggregate_dirty_classes(paths),
            }
        )

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
    """Build branch/worktree intelligence without mutating repository state."""

    tools = _load_repo_tools()
    try:
        identity = tools["repo_identity"](repo_path)
        repo = Path(identity["path"])
        branch_facts = tools["list_branches"](repo)
        worktree_facts = tools["list_worktrees"](repo)
        remote_default = tools["remote_default_branch"](repo)
        canonical_name, canonical_ref = _canonical_ref(
            identity=identity,
            branches=branch_facts,
            remote_default=remote_default,
            override=canonical_branch,
        )
        branches = _decorate_branches(
            repo,
            branch_facts,
            canonical_branch=canonical_name,
            canonical_ref=canonical_ref,
            current_branch=str(identity.get("current_branch", "")),
            compare_refs=tools["compare_refs"],
        )
        worktrees = _decorate_worktrees(worktree_facts, canonical_name)
    except tools["error"] as exc:
        raise FleetHygieneError(str(exc)) from exc

    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "repo": {
            "name": identity["name"],
            "path": identity["path"],
            "origin": identity["origin"],
            "head": identity["head"],
            "current_branch": identity["current_branch"],
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
