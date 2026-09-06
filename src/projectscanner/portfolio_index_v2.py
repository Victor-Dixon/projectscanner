"""Compile ProjectScanner evidence into an HQ-ready portfolio index.

This module deliberately remains an evidence compiler. Repository planning files
remain repository-local authority, DreamVault remains governance/planner
authority, and model-facing context files remain projections rather than inputs
that can override evidence.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .export_intelligence import export_portfolio

SCHEMA_VERSION = "dreamos.portfolio-index.v2"
TASK_SCHEMA_VERSION = "dreamos.fleet-task-inventory.v1"
ASSIGNABLE_STATUSES = {"READY", "ACTIVE"}

_TASK_RE = re.compile(
    r"(?P<task_id>[A-Z][A-Z0-9._-]+)\s*\|\s*"
    r"(?P<priority>P[0-3])\s*\|\s*"
    r"(?P<status>READY|ACTIVE|BLOCKED|COMPLETE|BACKLOG)"
    r"(?:\s*\|\s*|\s+[—-]\s+)"
    r"(?P<title>.+?)\s*$"
)

_BUNDLE_ARTIFACTS = {
    "repo_analysis": ("repo_analysis.json", "repository_evidence"),
    "planning_contract": ("planning_contract.json", "normalized_planning_evidence"),
    "chatgpt_context": ("chatgpt_context.json", "model_projection"),
    "cleanup_recommendations": ("cleanup_recommendations.json", "recommendation_projection"),
    "docs_gap_report": ("docs_gap_report.md", "operator_projection"),
}


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _task_rows(text: str) -> list[dict[str, Any]]:
    """Extract fleet-standard task rows without interpreting free-form prose."""

    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        # Backticks are presentation markup, not task semantics. Removing them
        # lets both ``TASK | P0 | READY | title`` and
        # ``TASK | P0 | READY` — title`` normalize to one record shape.
        line = raw_line.replace("`", "").strip()
        match = _TASK_RE.search(line)
        if not match:
            continue
        row = match.groupdict()
        rows.append(
            {
                "task_id": row["task_id"],
                "priority": row["priority"],
                "status": row["status"],
                "title": row["title"].strip(),
                "line": line_number,
            }
        )
    return rows


def _duplicates(rows: list[dict[str, Any]]) -> list[str]:
    counts = Counter(str(row["task_id"]) for row in rows)
    return sorted(task_id for task_id, count in counts.items() if count > 1)


def _load_authority_text(planning: dict[str, Any], logical_name: str) -> tuple[str | None, str]:
    authority = planning.get("authority") if isinstance(planning.get("authority"), dict) else {}
    relative = authority.get(logical_name)
    repo_path = planning.get("repo_path")
    if not isinstance(relative, str) or not relative or not isinstance(repo_path, str):
        return None, ""
    path = Path(repo_path) / relative
    if not path.is_file():
        return relative, ""
    return relative, path.read_text(encoding="utf-8")


def build_task_inventory(planning: dict[str, Any]) -> dict[str, Any]:
    """Normalize master/list/log planning rows for one repository.

    The normalized inventory is intentionally planner-neutral. It proves which
    fleet-standard task records are present and whether NEXT_UP is a consistent
    bounded projection of MASTER_TASK_LIST. It does not rank tasks or authorize
    execution.
    """

    master_path, master_text = _load_authority_text(planning, "master_task_list")
    log_path, log_text = _load_authority_text(planning, "master_task_log")
    next_path, next_text = _load_authority_text(planning, "next_up")

    master_rows = _task_rows(master_text)
    next_rows = _task_rows(next_text)
    log_rows = _task_rows(log_text)

    errors: list[str] = []
    for task_id in _duplicates(master_rows):
        errors.append(f"DUPLICATE_MASTER_TASK:{task_id}")
    for task_id in _duplicates(next_rows):
        errors.append(f"DUPLICATE_NEXT_UP:{task_id}")

    if len(next_rows) > 5:
        errors.append("NEXT_UP_MORE_THAN_FIVE")

    master_by_id: dict[str, dict[str, Any]] = {}
    for row in master_rows:
        master_by_id.setdefault(str(row["task_id"]), row)

    next_ids: set[str] = set()
    for row in next_rows:
        task_id = str(row["task_id"])
        next_ids.add(task_id)
        canonical = master_by_id.get(task_id)
        if canonical is None:
            errors.append(f"UNKNOWN_NEXT_UP_TASK:{task_id}")
            continue
        if canonical["priority"] != row["priority"]:
            errors.append(f"PRIORITY_DRIFT:{task_id}")
        if canonical["status"] != row["status"]:
            errors.append(f"STATUS_DRIFT:{task_id}")

    active_master = {
        str(row["task_id"])
        for row in master_rows
        if row["status"] == "ACTIVE"
    }
    for task_id in sorted(active_master - next_ids):
        errors.append(f"MISSING_ACTIVE:{task_id}")

    projection_valid = not errors
    assignable: list[dict[str, Any]] = []
    if projection_valid:
        for row in next_rows:
            canonical = master_by_id.get(str(row["task_id"]))
            if canonical and canonical["status"] in ASSIGNABLE_STATUSES:
                assignable.append(dict(canonical))

    return {
        "schema_version": TASK_SCHEMA_VERSION,
        "authority": {
            "master_task_list": master_path,
            "master_task_log": log_path,
            "next_up": next_path,
        },
        "master": {
            "recognized_count": len(master_rows),
            "tasks": master_rows,
        },
        "next_up": {
            "recognized_count": len(next_rows),
            "tasks": next_rows,
        },
        "log": {
            "recognized_count": len(log_rows),
            "tasks": log_rows,
        },
        "projection": {
            "valid": projection_valid,
            "errors": errors,
            "assignable_count": len(assignable),
            "assignable": assignable,
        },
    }


def _bundle_artifacts(bundle_dir: Path, out_root: Path) -> dict[str, dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}
    for key, (filename, role) in _BUNDLE_ARTIFACTS.items():
        path = bundle_dir / filename
        artifacts[key] = {
            "path": path.relative_to(out_root).as_posix(),
            "exists": path.is_file(),
            "role": role,
            "authoritative": False,
        }
    return artifacts


def _analysis_library(repo_name: str, root: Path | None) -> dict[str, Any]:
    if root is None:
        return {
            "root": None,
            "project_analysis": [],
            "model_context": [],
        }

    root = root.resolve()
    project_pattern = f"project_analysis_{repo_name}.json"
    context_pattern = f"chatgpt_project_context_{repo_name}.json"

    def matches(pattern: str) -> list[str]:
        return sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob(pattern)
            if path.is_file()
        )

    return {
        "root": str(root),
        "project_analysis": [
            {
                "path": path,
                "role": "deep_project_evidence",
                "authoritative": False,
            }
            for path in matches(project_pattern)
        ],
        "model_context": [
            {
                "path": path,
                "role": "deep_model_projection",
                "authoritative": False,
            }
            for path in matches(context_pattern)
        ],
    }


def compile_portfolio_index_v2(
    out_root: Path,
    *,
    analysis_library_root: Path | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Compile an HQ-ready evidence index from an existing v1 export bundle."""

    out_root = out_root.resolve()
    source_path = out_root / "portfolio_index.json"
    source = _read_json(source_path)
    generated_at = generated_at or datetime.now(UTC)

    repos: list[dict[str, Any]] = []
    for record in source.get("repos", []):
        if not isinstance(record, dict):
            continue
        repo_name = str(record.get("repo") or "")
        if not repo_name:
            continue

        bundle_dir = out_root / repo_name
        planning_path = bundle_dir / "planning_contract.json"
        planning = _read_json(planning_path) if planning_path.is_file() else {}

        enriched = dict(record)
        enriched["task_inventory"] = build_task_inventory(planning)
        enriched["artifacts"] = _bundle_artifacts(bundle_dir, out_root)
        enriched["analysis_library"] = _analysis_library(repo_name, analysis_library_root)
        repos.append(enriched)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at.astimezone(UTC).isoformat(),
        "authority": "projectscanner_evidence_not_execution_state",
        "source_index": {
            "schema_version": source.get("schema_version"),
            "path": source_path.name,
            "generated_at": source.get("generated_at"),
        },
        "repo_count": len(repos),
        "active_repo_count": sum(1 for repo in repos if repo.get("fleet_state") == "active"),
        "status_counts": dict(source.get("status_counts") or {}),
        "repos": sorted(repos, key=lambda item: str(item.get("repo_key") or "")),
        "projection_contract": {
            "planner_candidate_source": "repos[].task_inventory.projection.assignable",
            "planner_authority": "DreamVault",
            "model_context_role": "projection_only",
            "generated_artifacts_override_repository_authority": False,
        },
    }


def export_portfolio_index_v2(
    projects_root: Path,
    out_root: Path,
    *,
    repos: list[str] | None = None,
    analysis_library_root: Path | None = None,
) -> dict[str, Any]:
    """Run the existing v1 export, then compile the additive v2 evidence view."""

    export_result = export_portfolio(
        projects_root=projects_root,
        out_root=out_root,
        repos=repos,
    )
    index = compile_portfolio_index_v2(
        out_root,
        analysis_library_root=analysis_library_root,
    )
    output = out_root.resolve() / "portfolio_index_v2.json"
    output.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        **export_result,
        "portfolio_index_v2": str(output),
        "schema_version": SCHEMA_VERSION,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile ProjectScanner portfolio evidence for Dream.OS HQ")
    parser.add_argument("--projects-root", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--repos", nargs="*", default=None)
    parser.add_argument("--analysis-library-root", type=Path, default=None)
    args = parser.parse_args()

    result = export_portfolio_index_v2(
        projects_root=args.projects_root,
        out_root=args.out_root,
        repos=args.repos,
        analysis_library_root=args.analysis_library_root,
    )
    print("PROJECTSCANNER_PORTFOLIO_INDEX_V2=PASS")
    print(f"REPOS={result['repos']}")
    print(f"OUTPUT={result['portfolio_index_v2']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
