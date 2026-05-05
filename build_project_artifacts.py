from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_artifact_standards import (
    ARTIFACT_ROOT,
    REQUIRED_ARTIFACTS,
    check_artifact_standards,
    expected_dir_for_target,
    load_targets,
    summarize_artifact_standards,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def artifact_payloads_for_target(target: dict[str, Any]) -> dict[str, dict[str, Any]]:
    source_type = target.get("source_type", "unknown")
    name = target.get("name") or target.get("repo") or "unknown"
    local_path = target.get("local_path", "")
    status = target.get("status", "unknown")

    now = utc_now()

    scan_target = {
        "artifact_schema": "projectscanner.scan_target.v1",
        "generated_at": now,
        "target": target,
    }

    analysis = {
        "artifact_schema": "projectscanner.analysis.v1",
        "generated_at": now,
        "project": name,
        "source_type": source_type,
        "status": "baseline_generated",
        "summary": "Baseline analysis artifact generated from scan target metadata. Deep scanner output not attached yet.",
        "signals": {
            "target_status": status,
            "local_path_exists": bool(local_path and Path(local_path).exists()),
            "is_git_repo": bool(local_path and (Path(local_path) / ".git").exists()),
        },
        "next_enrichment": [
            "attach file-level project scan",
            "attach dependency summary",
            "attach test/CI summary",
            "attach stale/noise classification",
        ],
    }

    context = {
        "artifact_schema": "projectscanner.context.v1",
        "generated_at": now,
        "project": name,
        "source_type": source_type,
        "context": {
            "name": name,
            "local_path": local_path,
            "github_url": target.get("github_url", ""),
            "branch": target.get("branch", ""),
            "owner": target.get("owner", ""),
            "repo": target.get("repo", ""),
        },
    }

    next_up = {
        "artifact_schema": "projectscanner.next_up.v1",
        "generated_at": now,
        "project": name,
        "tasks": [
            {
                "title": "Attach real scanner analysis",
                "priority": 90,
                "status": "planned",
                "verify": "analysis.json contains scanner_output or file_inventory",
            },
            {
                "title": "Classify project role and priority",
                "priority": 80,
                "status": "planned",
                "verify": "health.json contains category and readiness score",
            },
        ],
    }

    health = {
        "artifact_schema": "projectscanner.health.v1",
        "generated_at": now,
        "project": name,
        "source_type": source_type,
        "status": "baseline",
        "checks": {
            "scan_target_present": True,
            "analysis_present": True,
            "context_present": True,
            "next_up_present": True,
            "deep_scan_present": False,
            "local_path_exists": bool(local_path and Path(local_path).exists()),
            "git_repo_present": bool(local_path and (Path(local_path) / ".git").exists()),
        },
    }

    return {
        "scan_target.json": scan_target,
        "analysis.json": analysis,
        "context.json": context,
        "next_up.json": next_up,
        "health.json": health,
    }


def build_project_artifacts() -> dict[str, Any]:
    targets = load_targets()
    written = []

    for target in targets:
        artifact_dir = expected_dir_for_target(target)
        payloads = artifact_payloads_for_target(target)

        for filename in REQUIRED_ARTIFACTS:
            write_json(artifact_dir / filename, payloads[filename])
            written.append(str(artifact_dir / filename))

    results = check_artifact_standards(targets)
    summary = summarize_artifact_standards(results)

    report = {
        "generated_at": utc_now(),
        "target_count": len(targets),
        "files_written": len(written),
        "artifact_root": str(ARTIFACT_ROOT),
        "standard_summary": summary,
        "written": written,
    }

    out = Path("runtime/tasks/build_project_artifacts_report.json")
    write_json(out, report)

    return report


def main() -> int:
    report = build_project_artifacts()
    summary = report["standard_summary"]

    print(f"ARTIFACT_ROOT={report['artifact_root']}")
    print(f"TARGET_COUNT={report['target_count']}")
    print(f"FILES_WRITTEN={report['files_written']}")
    print(f"COMPLETE={summary['complete_count']}")
    print(f"INCOMPLETE={summary['incomplete_count']}")
    print("REPORT=runtime/tasks/build_project_artifacts_report.json")
    return 0 if summary["incomplete_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
