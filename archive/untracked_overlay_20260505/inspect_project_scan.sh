#!/usr/bin/env bash
set -euo pipefail

python - << 'PY'
import json
from pathlib import Path

targets = [
    Path("project_analysis_projectscanner.json"),
    Path("chatgpt_project_context_projectscanner.json"),
    Path("runtime/reports/projectscanner_json_artifact_inventory.json"),
    Path("runtime/targets/github_inventory.json"),
    Path("runtime/targets/github_scan_targets_latest.json"),
]

for path in targets:
    print("\n" + "=" * 80)
    print(f"FILE: {path}")
    print("=" * 80)

    if not path.exists():
        print("MISSING")
        continue

    raw = json.loads(path.read_text(encoding="utf-8"))
    print("TYPE:", type(raw).__name__)

    if isinstance(raw, dict):
        print("TOP_KEYS:", list(raw.keys())[:80])

        for key in [
            "project",
            "project_name",
            "name",
            "summary",
            "analysis",
            "files",
            "directories",
            "technologies",
            "dependencies",
            "issues",
            "recommendations",
            "tasks",
            "next_steps",
            "todos",
            "repo_count",
            "targets",
            "repos",
            "artifacts",
        ]:
            if key in raw:
                value = raw[key]
                print(f"\nKEY: {key}")
                print("VALUE_TYPE:", type(value).__name__)

                if isinstance(value, dict):
                    print("DICT_KEYS:", list(value.keys())[:50])
                    print(json.dumps(value, indent=2)[:2500])
                elif isinstance(value, list):
                    print("LIST_LEN:", len(value))
                    print(json.dumps(value[:3], indent=2)[:2500])
                else:
                    print(str(value)[:2500])

    elif isinstance(raw, list):
        print("LIST_LEN:", len(raw))
        print(json.dumps(raw[:3], indent=2)[:3000])
PY
