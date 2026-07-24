from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from scan_targets import as_target_dict


# Repo-relative SSOT (fixes silent empty target loads from ~/projects/projectscanner).
ROOT = Path(__file__).resolve().parent
ARTIFACT_ROOT = ROOT / "runtime" / "project_artifacts"
GITHUB_TARGETS = ROOT / "runtime" / "targets" / "github_scan_targets_latest.json"
LOCAL_TARGETS = ROOT / "runtime" / "targets" / "local_scan_targets_latest.json"

REQUIRED_ARTIFACTS = [
    "scan_target.json",
    "analysis.json",
    "context.json",
    "next_up.json",
    "health.json",
]


@dataclass(frozen=True)
class ArtifactStandardResult:
    project: str
    source_type: str
    expected_dir: str
    missing_files: list[str]
    present_files: list[str]

    @property
    def complete(self) -> bool:
        return not self.missing_files


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def safe_name(value: str) -> str:
    return value.replace("/", "__").replace(" ", "_")


def expected_dir_for_target(target: Mapping[str, Any] | Any) -> Path:
    """Accept ScanTarget or dict — AttributeError guard for four-target scans."""
    target = as_target_dict(target)
    source_type = target.get("source_type", "unknown")

    if source_type == "github":
        owner = target.get("owner", "unknown")
        repo = target.get("repo", target.get("name", "unknown"))
        return ARTIFACT_ROOT / "github" / owner / repo

    name = target.get("repo") or target.get("name") or Path(target.get("local_path", "unknown")).name
    return ARTIFACT_ROOT / "local" / safe_name(str(name))


def load_targets() -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []

    for path in [GITHUB_TARGETS, LOCAL_TARGETS]:
        data = load_json(path, {"targets": []})
        for item in data.get("targets", []):
            targets.append(as_target_dict(item))

    return targets


def check_artifact_standards(targets: list[Any] | None = None) -> list[ArtifactStandardResult]:
    targets = targets if targets is not None else load_targets()
    results: list[ArtifactStandardResult] = []

    for raw in targets:
        target = as_target_dict(raw)
        expected_dir = expected_dir_for_target(target)
        present = []
        missing = []

        for filename in REQUIRED_ARTIFACTS:
            if (expected_dir / filename).exists():
                present.append(filename)
            else:
                missing.append(filename)

        results.append(
            ArtifactStandardResult(
                project=str(target.get("name", target.get("repo", "unknown"))),
                source_type=str(target.get("source_type", "unknown")),
                expected_dir=str(expected_dir),
                missing_files=missing,
                present_files=present,
            )
        )

    return results


def summarize_artifact_standards(results: list[ArtifactStandardResult]) -> dict[str, Any]:
    complete = [r for r in results if r.complete]
    incomplete = [r for r in results if not r.complete]

    return {
        "project_count": len(results),
        "complete_count": len(complete),
        "incomplete_count": len(incomplete),
        "required_artifacts": REQUIRED_ARTIFACTS,
        "incomplete": [
            {
                "project": r.project,
                "source_type": r.source_type,
                "expected_dir": r.expected_dir,
                "missing_files": r.missing_files,
                "present_files": r.present_files,
            }
            for r in incomplete
        ],
    }
