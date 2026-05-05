from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.home() / "projects" / "projectscanner"

GITHUB_INVENTORY = ROOT / "runtime" / "targets" / "github_inventory.json"
GITHUB_TARGETS = ROOT / "runtime" / "targets" / "github_scan_targets_latest.json"
LOCAL_CENSUS = ROOT / "runtime" / "targets" / "local_projects_census.json"
ARTIFACT_INVENTORY = ROOT / "runtime" / "reports" / "projectscanner_json_artifact_inventory.json"

OUT_DIR = ROOT / "runtime" / "tasks"
MASTER_JSON = OUT_DIR / "master_project_task_list.json"
MASTER_MD = OUT_DIR / "master_project_task_list.md"
NEXT_JSON = OUT_DIR / "master_next_up.json"
NEXT_MD = OUT_DIR / "master_next_up.md"


@dataclass(frozen=True)
class ProjectTask:
    task_id: str
    project: str
    lane: str
    title: str
    reason: str
    priority: int
    source: str
    status: str = "planned"
    verify: str = ""


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def classify_project(name: str) -> str:
    lower = name.lower()

    if lower in {"agenttools", "projectscanner"}:
        return "toolbelt"
    if any(x in lower for x in ["dreamos", "dream.os", "victor.os", "autodream"]):
        return "dreamos_family"
    if any(x in lower for x in ["homeschool", "professorsama", "teks", "staar"]):
        return "homeschool"
    if any(x in lower for x in ["trading", "trade", "stock", "options"]):
        return "trading"
    if any(x in lower for x in ["discord", "bot", "swarm", "agent"]):
        return "automation"
    return "other"


def make_id(project: str, lane: str, n: int) -> str:
    safe = project.lower().replace("/", "_").replace(".", "_").replace("-", "_")
    safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in safe)
    return f"{safe}_{lane}_{n:03d}"


def build_tasks() -> list[ProjectTask]:
    tasks: list[ProjectTask] = []

    github = load_json(GITHUB_INVENTORY, {"repos": []})
    targets = load_json(GITHUB_TARGETS, {"targets": []})
    local = load_json(LOCAL_CENSUS, {"projects": []})
    artifacts = load_json(ARTIFACT_INVENTORY, {"artifacts": []})

    local_by_name = {
        p.get("name", "").lower(): p
        for p in local.get("projects", [])
        if p.get("name")
    }

    target_by_name = {
        t.get("name", "").lower(): t
        for t in targets.get("targets", [])
        if t.get("name")
    }

    n = 1

    # GitHub repos: make scan/fetch tasks.
    for repo in github.get("repos", []):
        name_with_owner = repo.get("name_with_owner", "")
        repo_name = repo.get("name", "")
        branch = repo.get("default_branch", "")
        category = classify_project(repo_name)

        target = target_by_name.get(name_with_owner.lower(), {})
        status = target.get("status", "unknown")

        if status == "not_cloned":
            tasks.append(
                ProjectTask(
                    task_id=make_id(repo_name, "fetch", n),
                    project=repo_name,
                    lane="github_fetch",
                    title=f"Clone GitHub repo locally: {name_with_owner}",
                    reason=f"GitHub repo exists but local cached clone is missing. branch={branch}",
                    priority=80 if category in {"dreamos_family", "toolbelt", "homeschool"} else 50,
                    source="github_scan_targets_latest.json",
                    verify=f"test -d \"$HOME/projects/_github_sources/Victor-Dixon/{repo_name}/.git\"",
                )
            )
            n += 1

        tasks.append(
            ProjectTask(
                task_id=make_id(repo_name, "scan", n),
                project=repo_name,
                lane="project_scan",
                title=f"Generate normalized project scan for {repo_name}",
                reason=f"Ensure current local/cloud state has a project context snapshot. category={category}",
                priority=90 if category in {"dreamos_family", "toolbelt"} else 60,
                source="github_inventory.json",
                verify=f"test -f runtime/project_artifacts/*/{repo_name}/analysis.json || true",
            )
        )
        n += 1

    # Local dirty repo tasks.
    for project in local.get("projects", []):
        name = project.get("name", "")
        if not name:
            continue

        if project.get("dirty"):
            tasks.append(
                ProjectTask(
                    task_id=make_id(name, "dirty", n),
                    project=name,
                    lane="repo_hygiene",
                    title=f"Review dirty repo state: {name}",
                    reason="Local repo has uncommitted changes.",
                    priority=95 if classify_project(name) in {"dreamos_family", "toolbelt"} else 70,
                    source="local_projects_census.json",
                    verify=f"git -C {project.get('path')} status --short",
                )
            )
            n += 1

    # ProjectScanner artifact cleanup tasks.
    unknown_artifacts = [
        a for a in artifacts.get("artifacts", [])
        if a.get("confidence") in {"unknown", "low"}
    ]
    if unknown_artifacts:
        tasks.append(
            ProjectTask(
                task_id="projectscanner_artifact_classification_001",
                project="projectscanner",
                lane="artifact_library",
                title="Classify low-confidence ProjectScanner JSON artifacts",
                reason=f"{len(unknown_artifacts)} JSON artifact(s) have low/unknown project classification.",
                priority=75,
                source="projectscanner_json_artifact_inventory.json",
                verify="python analyze_projectscanner_jsons.sh || ./analyze_projectscanner_jsons.sh",
            )
        )

    # Core system tasks.
    tasks.append(
        ProjectTask(
            task_id="discord_ops_manager_panel_001",
            project="discord_ops_manager",
            lane="discord_control_plane",
            title="Add local/GitHub diff panel to Dream Discord console",
            reason="Operator needs one view showing local projects vs GitHub repos vs missing clones.",
            priority=100,
            source="operator_plan",
            verify="pytest -q && python -m py_compile bot.py dreamos_views.py",
        )
    )

    tasks.append(
        ProjectTask(
            task_id="projectscanner_global_artifacts_001",
            project="projectscanner",
            lane="global_project_library",
            title="Create normalized global project artifact library",
            reason="ProjectScanner currently has local self-artifacts and GitHub inventory, but not normalized analysis snapshots for every project.",
            priority=100,
            source="operator_plan",
            verify="test -d runtime/project_artifacts && find runtime/project_artifacts -name analysis.json | head",
        )
    )

    return sorted(tasks, key=lambda t: (-t.priority, t.project, t.lane))


def write_outputs(tasks: list[ProjectTask]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_count": len(tasks),
        "tasks": [asdict(t) for t in tasks],
    }

    MASTER_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Master Project Task List",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Tasks: `{payload['task_count']}`",
        "",
        "## Tasks",
    ]

    for task in tasks:
        lines.append(
            f"- **P{task.priority}** `{task.project}` / `{task.lane}` — {task.title}\n"
            f"  - id: `{task.task_id}`\n"
            f"  - reason: {task.reason}\n"
            f"  - verify: `{task.verify}`"
        )

    MASTER_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    next_tasks = tasks[:10]
    NEXT_JSON.write_text(
        json.dumps(
            {
                "generated_at": payload["generated_at"],
                "task_count": len(next_tasks),
                "tasks": [asdict(t) for t in next_tasks],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    next_lines = [
        "# Next Up",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Showing: `{len(next_tasks)}`",
        "",
    ]

    for idx, task in enumerate(next_tasks, start=1):
        next_lines.append(
            f"## {idx}. {task.title}\n"
            f"- Project: `{task.project}`\n"
            f"- Lane: `{task.lane}`\n"
            f"- Priority: `{task.priority}`\n"
            f"- Reason: {task.reason}\n"
            f"- Verify: `{task.verify}`\n"
        )

    NEXT_MD.write_text("\n".join(next_lines) + "\n", encoding="utf-8")


def main() -> int:
    tasks = build_tasks()
    write_outputs(tasks)

    print(f"WROTE_MASTER_JSON={MASTER_JSON}")
    print(f"WROTE_MASTER_MD={MASTER_MD}")
    print(f"WROTE_NEXT_JSON={NEXT_JSON}")
    print(f"WROTE_NEXT_MD={NEXT_MD}")
    print(f"TASK_COUNT={len(tasks)}")
    print("TOP_5:")
    for task in tasks[:5]:
        print(f"- P{task.priority} {task.project} :: {task.title}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
