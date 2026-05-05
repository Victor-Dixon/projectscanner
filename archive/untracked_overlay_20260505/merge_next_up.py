from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "projects" / "projectscanner"
TASKS_DIR = ROOT / "runtime" / "tasks"

MASTER = TASKS_DIR / "master_project_task_list.json"
SCANNER = TASKS_DIR / "projectscanner_scan_tasks.json"
OUT_JSON = TASKS_DIR / "next_up.json"
OUT_MD = TASKS_DIR / "next_up.md"


def load_tasks(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("tasks", [])


def normalize(task: dict, source: str) -> dict:
    return {
        "task_id": task.get("task_id", ""),
        "project": task.get("project", "unknown"),
        "lane": task.get("lane", "unknown"),
        "title": task.get("title", ""),
        "reason": task.get("reason", ""),
        "priority": int(task.get("priority", 0)),
        "verify": task.get("verify", ""),
        "source_board": source,
        "source_file": task.get("source_file", ""),
    }


def main() -> int:
    tasks = []
    tasks.extend(normalize(t, "master") for t in load_tasks(MASTER))
    tasks.extend(normalize(t, "projectscanner_scan") for t in load_tasks(SCANNER))

    seen = set()
    deduped = []
    for task in sorted(tasks, key=lambda t: (-t["priority"], t["project"], t["lane"], t["title"])):
        key = (task["project"], task["lane"], task["title"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(task)

    top = deduped[:15]
    generated = datetime.now(timezone.utc).isoformat()

    OUT_JSON.write_text(
        json.dumps(
            {
                "generated_at": generated,
                "task_count": len(top),
                "total_available_tasks": len(deduped),
                "tasks": top,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    lines = [
        "# Next Up",
        "",
        f"- Generated: `{generated}`",
        f"- Showing: `{len(top)}`",
        f"- Total available tasks: `{len(deduped)}`",
        "",
    ]

    for idx, task in enumerate(top, start=1):
        source_extra = f" / `{task['source_file']}`" if task["source_file"] else ""
        lines.append(
            f"## {idx}. {task['title']}\n"
            f"- Priority: `{task['priority']}`\n"
            f"- Project: `{task['project']}`\n"
            f"- Lane: `{task['lane']}`\n"
            f"- Source: `{task['source_board']}`{source_extra}\n"
            f"- Reason: {task['reason']}\n"
            f"- Verify: `{task['verify']}`\n"
        )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"WROTE_NEXT_JSON={OUT_JSON}")
    print(f"WROTE_NEXT_MD={OUT_MD}")
    print(f"TOTAL_AVAILABLE_TASKS={len(deduped)}")
    print(f"NEXT_COUNT={len(top)}")
    print("TOP_5:")
    for task in top[:5]:
        print(f"- P{task['priority']} {task['project']} :: {task['title']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
