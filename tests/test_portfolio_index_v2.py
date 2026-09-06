from __future__ import annotations

import json
import subprocess
from pathlib import Path

from projectscanner.portfolio_index_v2 import (
    SCHEMA_VERSION,
    build_task_inventory,
    export_portfolio_index_v2,
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write(repo: Path, name: str, content: str) -> None:
    (repo / name).write_text(content, encoding="utf-8")


def _init_repo(repo: Path) -> None:
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "projectscanner@example.invalid")
    _git(repo, "config", "user.name", "ProjectScanner Test")
    _git(repo, "branch", "-M", "master")

    _write(repo, "README.md", "# Example\n")
    _write(repo, "DOMAIN_MODEL.md", "# Domain\n")
    _write(
        repo,
        "MASTER_TASK_LIST.md",
        "# Tasks\n\n"
        "- TASK-001 | P0 | ACTIVE | Ship the HQ evidence contract\n"
        "- TASK-002 | P1 | BLOCKED | Wait for a dependency\n",
    )
    _write(
        repo,
        "MASTER_TASK_LOG.md",
        "# Log\n\n- TASK-OLD | P2 | COMPLETE | Historical completed work\n",
    )
    _write(
        repo,
        "NEXT_UP.md",
        "# Next Up\n\n## Immediate Queue\n\n"
        "1. `TASK-001 | P0 | ACTIVE` — Ship the HQ evidence contract\n"
        "2. `TASK-002 | P1 | BLOCKED` — Wait for a dependency\n",
    )

    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "planning baseline")


def test_portfolio_index_v2_classifies_evidence_tasks_and_model_projections(tmp_path):
    projects = tmp_path / "projects"
    projects.mkdir()
    repo = projects / "Example"
    _init_repo(repo)

    analysis_library = tmp_path / "analysis-library"
    deep = analysis_library / "deep"
    deep.mkdir(parents=True)
    (deep / "project_analysis_Example.json").write_text("{}\n", encoding="utf-8")
    (deep / "chatgpt_project_context_Example.json").write_text("{}\n", encoding="utf-8")

    out = tmp_path / "out"
    result = export_portfolio_index_v2(
        projects,
        out,
        analysis_library_root=analysis_library,
    )

    index = json.loads(Path(result["portfolio_index_v2"]).read_text(encoding="utf-8"))
    assert index["schema_version"] == SCHEMA_VERSION
    assert index["authority"] == "projectscanner_evidence_not_execution_state"
    assert index["repo_count"] == 1
    assert index["projection_contract"]["planner_authority"] == "DreamVault"

    item = index["repos"][0]
    inventory = item["task_inventory"]
    assert inventory["master"]["recognized_count"] == 2
    assert inventory["next_up"]["recognized_count"] == 2
    assert inventory["log"]["recognized_count"] == 1
    assert inventory["projection"]["valid"] is True
    assert inventory["projection"]["assignable_count"] == 1
    assert inventory["projection"]["assignable"][0]["task_id"] == "TASK-001"

    artifacts = item["artifacts"]
    assert artifacts["repo_analysis"]["role"] == "repository_evidence"
    assert artifacts["planning_contract"]["role"] == "normalized_planning_evidence"
    assert artifacts["chatgpt_context"]["role"] == "model_projection"
    assert artifacts["chatgpt_context"]["authoritative"] is False

    library = item["analysis_library"]
    assert library["project_analysis"] == [
        {
            "path": "deep/project_analysis_Example.json",
            "role": "deep_project_evidence",
            "authoritative": False,
        }
    ]
    assert library["model_context"] == [
        {
            "path": "deep/chatgpt_project_context_Example.json",
            "role": "deep_model_projection",
            "authoritative": False,
        }
    ]


def test_task_inventory_fails_closed_on_projection_drift(tmp_path):
    repo = tmp_path / "Example"
    repo.mkdir()
    _write(
        repo,
        "MASTER_TASK_LIST.md",
        "- TASK-001 | P0 | ACTIVE | Canonical title\n"
        "- TASK-002 | P1 | READY | Secondary task\n",
    )
    _write(repo, "MASTER_TASK_LOG.md", "# Log\n")
    _write(
        repo,
        "NEXT_UP.md",
        "1. TASK-001 | P1 | ACTIVE | Wrong priority\n"
        "2. TASK-404 | P1 | READY | Unknown task\n",
    )

    planning = {
        "repo_path": str(repo),
        "authority": {
            "master_task_list": "MASTER_TASK_LIST.md",
            "master_task_log": "MASTER_TASK_LOG.md",
            "next_up": "NEXT_UP.md",
        },
    }

    inventory = build_task_inventory(planning)

    assert inventory["projection"]["valid"] is False
    assert inventory["projection"]["assignable"] == []
    assert "PRIORITY_DRIFT:TASK-001" in inventory["projection"]["errors"]
    assert "UNKNOWN_NEXT_UP_TASK:TASK-404" in inventory["projection"]["errors"]
