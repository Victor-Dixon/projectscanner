#!/usr/bin/env bash
set -euo pipefail

python - << 'PY'
import json
from pathlib import Path

from project_artifact_standards import check_artifact_standards, summarize_artifact_standards

results = check_artifact_standards()
summary = summarize_artifact_standards(results)

out_json = Path("runtime/tasks/project_artifact_standard_report.json")
out_md = Path("runtime/tasks/project_artifact_standard_report.md")
out_json.parent.mkdir(parents=True, exist_ok=True)

out_json.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

lines = [
    "# Project Artifact Standard Report",
    "",
    f"- Projects checked: `{summary['project_count']}`",
    f"- Complete: `{summary['complete_count']}`",
    f"- Incomplete: `{summary['incomplete_count']}`",
    "",
    "## Required Artifacts",
]
for item in summary["required_artifacts"]:
    lines.append(f"- `{item}`")

lines += ["", "## Incomplete Projects"]
for item in summary["incomplete"][:80]:
    lines.append(
        f"- `{item['project']}` [{item['source_type']}]\n"
        f"  - dir: `{item['expected_dir']}`\n"
        f"  - missing: `{', '.join(item['missing_files'])}`"
    )

out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"WROTE_JSON={out_json}")
print(f"WROTE_MD={out_md}")
print(f"PROJECTS_CHECKED={summary['project_count']}")
print(f"COMPLETE={summary['complete_count']}")
print(f"INCOMPLETE={summary['incomplete_count']}")
PY

sed -n '1,180p' runtime/tasks/project_artifact_standard_report.md
