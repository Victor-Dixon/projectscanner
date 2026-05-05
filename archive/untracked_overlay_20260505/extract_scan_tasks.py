from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


ROOT = Path.home() / "projects" / "projectscanner"
PROJECT_ANALYSIS = ROOT / "project_analysis_projectscanner.json"
CHATGPT_CONTEXT = ROOT / "chatgpt_project_context_projectscanner.json"

OUT_DIR = ROOT / "runtime" / "tasks"
OUT_JSON = OUT_DIR / "projectscanner_scan_tasks.json"
OUT_MD = OUT_DIR / "projectscanner_scan_tasks.md"
NEXT_MD = OUT_DIR / "projectscanner_next_up.md"


@dataclass(frozen=True)
class ScanTask:
    task_id: str
    project: str
    source_file: str
    lane: str
    title: str
    reason: str
    priority: int
    verify: str


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def classify_file(path: str) -> tuple[str, int, str]:
    lower = path.lower()

    if path == "__dependency_graph__":
        return ("architecture", 90, "Dependency graph should be summarized for project structure and coupling risk.")

    if lower.endswith(("task_list.md", "docs/next_up.md", "docs/roadmap.md", "docs/sprint_tasks.md")):
        return ("planning", 95, "Planning document should feed master task list and next-up board.")

    if lower.startswith("tests/") or "/test_" in lower or lower.endswith("_test.py"):
        return ("testing", 80, "Test file should be checked for coverage signals and failing legacy assumptions.")

    if lower.startswith(".github/workflows/"):
        return ("ci", 85, "CI workflow should be validated against current project layout.")

    if lower.startswith("src/") or lower.startswith("engine/") or lower.startswith("projectscanner.engine/"):
        return ("code_analysis", 75, "Source file should be included in project scan quality review.")

    if lower.endswith(".md"):
        return ("docs", 60, "Documentation should be checked for stale status and roadmap value.")

    if lower.endswith((".json", ".yaml", ".yml", ".toml")):
        return ("config", 70, "Config/artifact file should be classified and normalized.")

    return ("inventory", 40, "File is part of scan inventory.")


def extract_detail_summary(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("summary", "description", "purpose", "analysis", "content_summary"):
            if key in value and isinstance(value[key], str) and value[key].strip():
                return value[key].strip()[:240]
        keys = ", ".join(list(value.keys())[:8])
        return f"scan entry keys: {keys}"
    if isinstance(value, str):
        return value[:240]
    return type(value).__name__


def build_tasks() -> list[ScanTask]:
    analysis = load_json(PROJECT_ANALYSIS)
    context = load_json(CHATGPT_CONTEXT)

    tasks: list[ScanTask] = []
    n = 1

    if isinstance(context, dict):
        count = context.get("num_files_analyzed")
        tasks.append(
            ScanTask(
                task_id="projectscanner_context_summary_001",
                project="projectscanner",
                source_file=str(CHATGPT_CONTEXT.relative_to(ROOT)),
                lane="project_context",
                title="Summarize ProjectScanner ChatGPT project context",
                reason=f"Context file reports num_files_analyzed={count}; convert into operator-readable project summary.",
                priority=100,
                verify="test -f runtime/tasks/projectscanner_scan_tasks.md",
            )
        )

    if isinstance(analysis, dict):
        for source_file, detail in analysis.items():
            lane, base_priority, reason = classify_file(source_file)
            summary = extract_detail_summary(detail)

            # Promote obvious high-value files.
            priority = base_priority
            lower = source_file.lower()
            if any(x in lower for x in ["next_up", "task_list", "roadmap", "current_state", "validation_report"]):
                priority += 10
            if "github_library_scanner" in lower or "scanner.py" in lower or "scan_targets" in lower:
                priority += 10

            tasks.append(
                ScanTask(
                    task_id=f"projectscanner_{lane}_{n:03d}",
                    project="projectscanner",
                    source_file=source_file,
                    lane=lane,
                    title=f"Review scan signal: {source_file}",
                    reason=f"{reason} {summary}",
                    priority=min(priority, 100),
                    verify=f"test -e '{source_file}' || true",
                )
            )
            n += 1

    return sorted(tasks, key=lambda t: (-t.priority, t.lane, t.source_file))


def write_outputs(tasks: list[ScanTask]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "projectscanner",
        "source": str(PROJECT_ANALYSIS),
        "task_count": len(tasks),
        "tasks": [asdict(t) for t in tasks],
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# ProjectScanner Scan-Derived Tasks",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Tasks: `{payload['task_count']}`",
        "",
        "## Top Tasks",
    ]

    for task in tasks[:50]:
        lines.append(
            f"- **P{task.priority}** `{task.lane}` — {task.title}\n"
            f"  - file: `{task.source_file}`\n"
            f"  - reason: {task.reason}\n"
            f"  - verify: `{task.verify}`"
        )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    next_lines = [
        "# Next Up",
        "",
        "Top scan-derived tasks from ProjectScanner.",
        "",
    ]

    for i, task in enumerate(tasks[:10], start=1):
        next_lines.append(
            f"## {i}. {task.title}\n"
            f"- Priority: `{task.priority}`\n"
            f"- Lane: `{task.lane}`\n"
            f"- File: `{task.source_file}`\n"
            f"- Reason: {task.reason}\n"
            f"- Verify: `{task.verify}`\n"
        )

    NEXT_MD.write_text("\n".join(next_lines) + "\n", encoding="utf-8")


def main() -> int:
    tasks = build_tasks()
    write_outputs(tasks)

    print(f"WROTE_JSON={OUT_JSON}")
    print(f"WROTE_MD={OUT_MD}")
    print(f"WROTE_NEXT={NEXT_MD}")
    print(f"TASK_COUNT={len(tasks)}")
    print("TOP_10:")
    for task in tasks[:10]:
        print(f"- P{task.priority} {task.lane} :: {task.source_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
