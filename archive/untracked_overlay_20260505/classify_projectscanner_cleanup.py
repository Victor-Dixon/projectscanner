from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path.home() / "projects" / "projectscanner"
OUT_JSON = ROOT / "runtime" / "reports" / "projectscanner_cleanup_manifest.json"
OUT_MD = ROOT / "runtime" / "reports" / "projectscanner_cleanup_manifest.md"


@dataclass(frozen=True)
class CleanupItem:
    path: str
    kind: str
    classification: str
    action: str
    reason: str


def classify(path: Path) -> CleanupItem:
    rel = path.relative_to(ROOT)
    s = str(rel)
    name = path.name
    kind = "dir" if path.is_dir() else "file"

    if "__pycache__" in s or name.endswith(".pyc") or ".pytest_cache" in s:
        return CleanupItem(s, kind, "cache_delete", "delete", "Python/test cache; safe generated noise.")

    if s.startswith("runtime/"):
        return CleanupItem(s, kind, "generated_runtime", "keep_or_gitignore", "Generated reports/artifacts; keep outputs but usually do not commit bulky runtime trees.")

    if s.startswith("tests/"):
        return CleanupItem(s, kind, "keep_tests", "keep", "Test coverage.")

    if s.startswith("docs/") or s in {"TASK_LIST.md", "README.md", "projects_report.md", "projectscanner_report.txt"}:
        return CleanupItem(s, kind, "keep_docs", "keep", "Project documentation/planning/report material.")

    if s.startswith("core/"):
        return CleanupItem(s, kind, "compat_shim_keep", "keep", "Compatibility shim for legacy imports like core.projectscanner.")

    if s.startswith(("engine/", "src/", "report/", "config/", "cli/")):
        return CleanupItem(s, kind, "keep_source", "keep", "Source package or project config.")

    if name in {
        "scan_targets.py",
        "scan_targets_cli.py",
        "github_sources.py",
        "project_sources_cli.py",
        "local_projects_census.py",
        "project_artifact_standards.py",
        "build_project_artifacts.py",
        "build_master_project_tasks.py",
        "extract_scan_tasks.py",
        "merge_next_up.py",
    }:
        return CleanupItem(s, kind, "keep_source", "keep", "Current ProjectScanner source module.")

    if name.endswith(".json") and name in {
        "project_analysis_projectscanner.json",
        "chatgpt_project_context_projectscanner.json",
    }:
        return CleanupItem(s, kind, "generated_runtime", "move_to_runtime_or_keep_reference", "Project scan artifact currently at repo root; candidate to relocate after references are updated.")

    if name.endswith(".sh") and name in {
        "analyze_projectscanner_jsons.sh",
        "inspect_project_scan.sh",
        "run_artifact_standard_report.sh",
        "investigate_projectscanner.sh",
    }:
        return CleanupItem(s, kind, "keep_source", "keep", "Current operational script.")

    if name.endswith(".py") and (
        name.startswith("fix_")
        or name.startswith("add_")
        or name.startswith("mark_")
        or name in {"final_comment_fix.py", "test_no_headers.py"}
    ):
        return CleanupItem(s, kind, "legacy_script_review", "archive_candidate", "One-off maintenance script; review before archive.")

    if name.endswith((".bat", ".sh")) and name.startswith("launch_"):
        return CleanupItem(s, kind, "candidate_archive", "review", "Launcher script; keep if still used, otherwise archive.")

    if name in {"LICENSE", "__init__.py", "main.py", "run.py", "requirements.txt", "pytest.ini"}:
        return CleanupItem(s, kind, "keep_source", "keep", "Repo root project file.")

    return CleanupItem(s, kind, "candidate_archive", "review", "Unclassified item; review before move/delete.")


def main() -> int:
    items = []

    for path in sorted(ROOT.rglob("*")):
        if path == OUT_JSON or path == OUT_MD:
            continue
        if ".git" in path.parts:
            continue
        items.append(classify(path))

    counts = Counter(item.classification for item in items)

    payload = {
        "root": str(ROOT),
        "item_count": len(items),
        "classification_counts": dict(sorted(counts.items())),
        "items": [asdict(item) for item in items],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# ProjectScanner Cleanup Manifest",
        "",
        f"- Root: `{ROOT}`",
        f"- Items: `{len(items)}`",
        "",
        "## Classification Counts",
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"- `{key}`: {value}")

    lines += ["", "## Delete Candidates"]
    for item in items:
        if item.action == "delete":
            lines.append(f"- `{item.path}` — {item.reason}")

    lines += ["", "## Archive/Review Candidates"]
    for item in items:
        if item.action in {"archive_candidate", "review", "move_to_runtime_or_keep_reference"}:
            lines.append(f"- `{item.path}` [{item.classification}] — {item.reason}")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"WROTE_JSON={OUT_JSON}")
    print(f"WROTE_MD={OUT_MD}")
    print(f"ITEM_COUNT={len(items)}")
    print("CLASSIFICATION_COUNTS=" + json.dumps(dict(sorted(counts.items())), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
