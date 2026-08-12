"""Portfolio intelligence export for Dream.OS handoff."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from .planning_contract import inspect_planning_contract

PORTFOLIO_SCHEMA_VERSION = "dreamos.portfolio-index.v1"
DOC_KEYS = ["readme", "prd", "roadmap", "master_task_list", "next_up"]


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def markers(repo: Path) -> dict:
    children = list(repo.iterdir()) if repo.exists() else []
    names = [p.name for p in children]
    upper = [n.upper() for n in names]
    return {
        "readme": any(n in names for n in ["README.md", "readme.md", "README.txt"]),
        "prd": any("PRD" in n for n in upper),
        "roadmap": any("ROADMAP" in n for n in upper),
        "master_task_list": "MASTER_TASK_LIST.md" in names,
        "next_up": "NEXT_UP.md" in names,
        "package_json": "package.json" in names,
        "pyproject": "pyproject.toml" in names,
        "requirements": "requirements.txt" in names,
        "pytest_ini": "pytest.ini" in names,
        "github_workflows": (repo / ".github" / "workflows").exists(),
    }


def docs_score(marker_data: dict) -> int:
    return round((sum(1 for key in DOC_KEYS if marker_data.get(key)) / len(DOC_KEYS)) * 100)


def _github_full_name(origin: str) -> str | None:
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$", origin.strip())
    if not match:
        return None
    return f"{match.group(1)}/{match.group(2)}"


def scan_repo(repo: Path) -> dict:
    marker_data = markers(repo)
    files = [p for p in repo.rglob("*") if ".git" not in p.parts and p.is_file()]
    dirs = [p for p in repo.rglob("*") if ".git" not in p.parts and p.is_dir()]
    status = run(["git", "status", "--short"], repo).splitlines()
    origin = run(["git", "remote", "get-url", "origin"], repo)
    branch = run(["git", "branch", "--show-current"], repo) or "NO_BRANCH"

    return {
        "name": repo.name,
        "path": str(repo),
        "generated": datetime.now(UTC).isoformat(),
        "is_git": (repo / ".git").exists(),
        "branch": branch,
        "head": run(["git", "rev-parse", "HEAD"], repo) or "NO_HEAD",
        "dirty": bool(status),
        "git_status_short": status,
        "origin": origin,
        "repository_full_name": _github_full_name(origin),
        "file_count": len(files),
        "dir_count": len(dirs),
        "top_level": sorted([p.name for p in repo.iterdir() if p.name != ".git"]),
        "docs_markers": marker_data,
        "docs_score": docs_score(marker_data),
        "missing_docs": [key for key in DOC_KEYS if not marker_data.get(key)],
    }


def _source_url(analysis: dict, planning: dict) -> str | None:
    full_name = analysis.get("repository_full_name")
    branch = analysis.get("branch")
    next_up = planning.get("authority", {}).get("next_up")
    if not full_name or not branch or branch == "NO_BRANCH" or not next_up:
        return None
    return f"https://github.com/{full_name}/blob/{branch}/{next_up}"


def _portfolio_record(analysis: dict, planning: dict) -> dict:
    return {
        "repo_key": planning["repo_key"],
        "planning_schema": planning["schema_version"],
        "repo": analysis["name"],
        "repository_full_name": analysis.get("repository_full_name"),
        "fleet_state": planning["fleet_state"],
        "contract_status": planning["contract_status"],
        "active_lane": planning["active_lane"],
        "next_actions": planning["next_actions"],
        "findings": planning["findings"],
        "authority": planning["authority"],
        "branch": analysis["branch"],
        "head_sha": analysis["head"],
        "dirty": analysis["dirty"],
        "docs_score": analysis["docs_score"],
        "source": _source_url(analysis, planning),
    }


def write_bundle(repo: Path, out_root: Path) -> dict:
    analysis = scan_repo(repo)
    planning = inspect_planning_contract(repo)
    record = _portfolio_record(analysis, planning)
    out = out_root / repo.name
    out.mkdir(parents=True, exist_ok=True)

    context = {
        "repo": analysis["name"],
        "repo_key": planning["repo_key"],
        "current_state": {
            "branch": analysis["branch"],
            "head": analysis["head"],
            "dirty": analysis["dirty"],
            "file_count": analysis["file_count"],
            "docs_score": analysis["docs_score"],
            "missing_docs": analysis["missing_docs"],
            "planning_contract_status": planning["contract_status"],
            "active_lane": planning["active_lane"],
            "planning_findings": planning["findings"],
        },
        "operator_guidance": {
            "safe_next_action": (
                "planning_reconciliation"
                if planning["contract_status"] != "PASS"
                else "docs_refresh"
                if analysis["missing_docs"]
                else "maintain"
            ),
            "guardrails": [
                "No destructive cleanup without a promotion manifest.",
                "Commit only scoped artifacts per lane.",
                "Verify with tests or file checks before commit.",
                "Flag planning contradictions; do not silently rewrite authority files.",
            ],
        },
    }

    recommendations = {
        "repo": analysis["name"],
        "repo_key": planning["repo_key"],
        "recommended_next_classes": (
            ["planning_reconciliation"]
            if planning["contract_status"] != "PASS"
            else ["docs_refresh"]
            if analysis["missing_docs"]
            else ["no_docs_gap_detected"]
        ),
        "missing_docs": analysis["missing_docs"],
        "planning_contract_status": planning["contract_status"],
        "planning_findings": planning["findings"],
        "risk": "medium" if analysis["dirty"] or planning["findings"] else "low",
    }

    (out / "repo_analysis.json").write_text(
        json.dumps(analysis, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "planning_contract.json").write_text(
        json.dumps(planning, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "chatgpt_context.json").write_text(
        json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "cleanup_recommendations.json").write_text(
        json.dumps(recommendations, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "docs_gap_report.md").write_text(
        f"# {analysis['name']} Docs Gap Report\n\n"
        f"- Docs score: {analysis['docs_score']}\n"
        f"- Missing docs: {', '.join(analysis['missing_docs']) or 'none'}\n"
        f"- Planning contract: {planning['contract_status']}\n"
        f"- Active lane: {planning['active_lane'] or 'Unknown'}\n\n"
        "DOCS_GAP_REPORT=PASS\n",
        encoding="utf-8",
    )
    return record


def _build_index(records: list[dict], generated_at: datetime) -> dict:
    ordered = sorted(records, key=lambda item: item["repo_key"])
    active = [item for item in ordered if item["fleet_state"] == "active"]
    statuses = Counter(item["contract_status"] for item in active)
    return {
        "schema_version": PORTFOLIO_SCHEMA_VERSION,
        "generated_at": generated_at.astimezone(UTC).isoformat(),
        "repo_count": len(ordered),
        "active_repo_count": len(active),
        "status_counts": {
            "PASS": statuses.get("PASS", 0),
            "WARN": statuses.get("WARN", 0),
            "FAIL": statuses.get("FAIL", 0),
        },
        "repos": ordered,
    }


def export_portfolio(
    projects_root: Path,
    out_root: Path,
    repos: list[str] | None = None,
) -> dict:
    generated_at = datetime.now(UTC)
    if repos is None:
        repos = [
            p.name
            for p in projects_root.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.name != "_ARCHIVE"
        ]

    records: list[dict] = []
    for name in sorted(set(repos), key=str.lower):
        repo = projects_root / name
        if repo.is_dir():
            records.append(write_bundle(repo, out_root))

    index = _build_index(records, generated_at)
    out_root.mkdir(parents=True, exist_ok=True)
    index_path = out_root / "portfolio_index.json"
    index_path.write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "repos": len(records),
        "active_repos": index["active_repo_count"],
        "out_root": str(out_root),
        "portfolio_index": str(index_path),
    }
