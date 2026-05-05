#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/projects/projectscanner"
OUT_DIR="$ROOT/runtime/reports"
OUT_JSON="$OUT_DIR/projectscanner_json_artifact_inventory.json"
OUT_MD="$OUT_DIR/projectscanner_json_artifact_inventory.md"

mkdir -p "$OUT_DIR"

python - << 'PY'
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path.home() / "projects" / "projectscanner"
OUT_DIR = ROOT / "runtime" / "reports"
OUT_JSON = OUT_DIR / "projectscanner_json_artifact_inventory.json"
OUT_MD = OUT_DIR / "projectscanner_json_artifact_inventory.md"

PATTERNS = [
    ("chatgpt_project_context", re.compile(r"chatgpt_project_context[_-](?P<project>.+)\.json$", re.I)),
    ("project_analysis", re.compile(r"project_analysis[_-](?P<project>.+)\.json$", re.I)),
    ("project_context", re.compile(r"project_context[_-](?P<project>.+)\.json$", re.I)),
    ("bridge_analysis", re.compile(r"bridge_analysis[_-](?P<project>.+)\.json$", re.I)),
]

def slug(value: str) -> str:
    value = value.strip().replace("\\", "/").split("/")[-1]
    value = re.sub(r"\.json$", "", value, flags=re.I)
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown"

def load_json(path: Path) -> tuple[bool, Any, str]:
    try:
        return True, json.loads(path.read_text(encoding="utf-8")), ""
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"

def top_keys(raw: Any) -> list[str]:
    return list(raw.keys())[:30] if isinstance(raw, dict) else []

def project_mentions(raw: Any, path: Path) -> list[str]:
    found = []

    def add(value: Any) -> None:
        if isinstance(value, str) and value.strip():
            found.append(slug(value))

    if isinstance(raw, dict):
        for key in ("project", "project_name", "name", "repo", "repository", "target_project", "root_name"):
            add(raw.get(key))
        for key in ("path", "root", "project_root", "repo_path", "repository_path"):
            value = raw.get(key)
            if isinstance(value, str):
                add(Path(value).name)
        for parent_key in ("metadata", "summary", "analysis"):
            parent = raw.get(parent_key)
            if isinstance(parent, dict):
                for key in ("project", "project_name", "name", "repo", "repository"):
                    add(parent.get(key))

    for _, pattern in PATTERNS:
        match = pattern.match(path.name)
        if match:
            add(match.group("project"))

    if path.parent.name == "reports":
        stem = path.stem
        for prefix in ("project_context_", "project_analysis_", "chatgpt_project_context_", "bridge_analysis_"):
            if stem.startswith(prefix):
                add(stem.removeprefix(prefix))

    clean = []
    seen = set()
    for item in found:
        if item and item not in seen:
            seen.add(item)
            clean.append(item)
    return clean

def classify(path: Path, raw: Any) -> tuple[str, str]:
    lower_name = path.name.lower()
    keys = {k.lower() for k in top_keys(raw)}

    for artifact_type, pattern in PATTERNS:
        if pattern.match(path.name):
            return artifact_type, "filename_pattern"

    if {"files", "summary"} <= keys or {"files", "analysis"} <= keys:
        return "project_analysis", "top_level_keys"
    if "project_context" in keys or "context" in keys:
        return "project_context", "top_level_keys"
    if "projects" in keys or "repos" in keys or "repositories" in keys:
        return "project_registry", "top_level_keys"
    if "bridge" in lower_name:
        return "bridge_analysis", "filename_keyword"
    if path.parent.name == "reports":
        return "runtime_report", "runtime_reports_dir"
    return "json_artifact", "fallback"

def confidence(mentions: list[str], artifact_type: str, reason: str) -> str:
    if mentions and reason == "filename_pattern":
        return "high"
    if mentions and artifact_type != "json_artifact":
        return "medium"
    if mentions:
        return "low"
    return "unknown"

def recommended_destination(project: str, artifact_type: str) -> str:
    project = slug(project)
    if project == "unknown":
        project = "_unknown"
    return f"runtime/project_artifacts/{project}/{artifact_type}.json"

artifacts = []

for path in sorted(ROOT.rglob("*.json")):
    if path == OUT_JSON:
        continue

    rel = path.relative_to(ROOT)
    ok, raw, error = load_json(path)

    if not ok:
        artifacts.append({
            "source_path": str(rel),
            "valid_json": False,
            "error": error,
            "project": "unknown",
            "project_mentions": [],
            "artifact_type": "invalid_json",
            "classification_reason": "parse_error",
            "confidence": "unknown",
            "top_level_type": "invalid",
            "top_keys": [],
            "recommended_name": f"{slug(path.stem)}.invalid_json.json",
            "recommended_destination": f"runtime/project_artifacts/_invalid/{path.name}",
            "size_bytes": path.stat().st_size,
        })
        continue

    artifact_type, reason = classify(path, raw)
    mentions = project_mentions(raw, path)
    project = mentions[0] if mentions else "unknown"
    conf = confidence(mentions, artifact_type, reason)

    artifacts.append({
        "source_path": str(rel),
        "valid_json": True,
        "error": "",
        "project": project,
        "project_mentions": mentions,
        "artifact_type": artifact_type,
        "classification_reason": reason,
        "confidence": conf,
        "top_level_type": type(raw).__name__,
        "top_keys": top_keys(raw),
        "recommended_name": f"{slug(project if project != 'unknown' else path.stem)}.{artifact_type}.json",
        "recommended_destination": recommended_destination(project, artifact_type),
        "size_bytes": path.stat().st_size,
    })

by_project = Counter(a["project"] for a in artifacts)
by_type = Counter(a["artifact_type"] for a in artifacts)
by_confidence = Counter(a["confidence"] for a in artifacts)

inventory = {
    "root": str(ROOT),
    "artifact_count": len(artifacts),
    "by_project": dict(sorted(by_project.items())),
    "by_type": dict(sorted(by_type.items())),
    "by_confidence": dict(sorted(by_confidence.items())),
    "artifacts": artifacts,
}

OUT_JSON.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")

lines = [
    "# ProjectScanner JSON Artifact Inventory",
    "",
    f"- Root: `{ROOT}`",
    f"- JSON artifacts: `{len(artifacts)}`",
    "",
    "## By Type",
]
for key, value in sorted(by_type.items()):
    lines.append(f"- `{key}`: {value}")

lines += ["", "## By Project"]
for key, value in sorted(by_project.items()):
    lines.append(f"- `{key}`: {value}")

lines += ["", "## Low/Unknown Confidence Items"]
low = [a for a in artifacts if a["confidence"] in {"low", "unknown"}]
if not low:
    lines.append("- None")
else:
    for a in low[:80]:
        lines.append(
            f"- `{a['source_path']}` → project=`{a['project']}` "
            f"type=`{a['artifact_type']}` reason=`{a['classification_reason']}`"
        )

lines += ["", "## Proposed Naming Map"]
for a in artifacts:
    lines.append(
        f"- `{a['source_path']}` → `{a['recommended_destination']}` "
        f"confidence=`{a['confidence']}`"
    )

OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"WROTE_JSON={OUT_JSON}")
print(f"WROTE_MD={OUT_MD}")
print(f"ARTIFACT_COUNT={len(artifacts)}")
print("BY_TYPE=" + json.dumps(dict(sorted(by_type.items())), sort_keys=True))
print("BY_CONFIDENCE=" + json.dumps(dict(sorted(by_confidence.items())), sort_keys=True))
PY

echo
echo "SUMMARY:"
python - << 'PY'
import json
from pathlib import Path

p = Path("runtime/reports/projectscanner_json_artifact_inventory.json")
data = json.loads(p.read_text(encoding="utf-8"))

print("artifact_count:", data["artifact_count"])
print("by_type:", data["by_type"])
print("by_project:", data["by_project"])
print("by_confidence:", data["by_confidence"])

print("\nFirst 20 artifacts:")
for a in data["artifacts"][:20]:
    print(f"- {a['source_path']} | project={a['project']} | type={a['artifact_type']} | confidence={a['confidence']} -> {a['recommended_name']}")
PY
