"""Versioned snapshot contract for CI ingest and history analysis."""

from __future__ import annotations

from typing import Any

ANALYSIS_SCHEMA_VERSION = "1.0"
METADATA_SCHEMA_VERSION = "1.0"


class SnapshotValidationError(ValueError):
    """Raised when snapshot metadata or analysis fails contract validation."""


def build_snapshot_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    """Convert scanner analysis into ingest-compatible ``analysis.json``."""
    files: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    for path, data in analysis.items():
        if path.startswith("__") and path.endswith("__"):
            continue
        if not isinstance(data, dict):
            continue

        functions = data.get("functions", [])
        classes = data.get("classes", [])
        files.append(
            {
                "path": path,
                "language": data.get("language", ""),
                "hash": data.get("hash", ""),
                "functions": len(functions) if isinstance(functions, list) else int(functions or 0),
                "classes": len(classes) if isinstance(classes, list) else int(classes or 0),
                "loc": data.get("loc", data.get("complexity", 0)),
            }
        )

        lint = data.get("lint", [])
        if isinstance(lint, list):
            for item in lint:
                if not isinstance(item, dict):
                    continue
                issues.append(
                    {
                        "rule": item.get("rule", "lint"),
                        "severity": item.get("severity", "info"),
                        "file_path": path,
                        "message": item.get("message", str(item)),
                        "line_start": item.get("line_start", item.get("line", 0)),
                    }
                )

    return {
        "schema_version": ANALYSIS_SCHEMA_VERSION,
        "total_files": len(files),
        "files": files,
        "issues": issues,
    }


def validate_metadata_payload(data: Any) -> None:
    if not isinstance(data, dict):
        raise SnapshotValidationError("metadata must be a JSON object")
    if "commit_sha" not in data:
        raise SnapshotValidationError("metadata missing required field: commit_sha")
    if not isinstance(data["commit_sha"], str) or not data["commit_sha"].strip():
        raise SnapshotValidationError("metadata.commit_sha must be a non-empty string")


def validate_analysis_payload(data: Any) -> None:
    if not isinstance(data, dict):
        raise SnapshotValidationError("analysis must be a JSON object")
    if "files" not in data:
        raise SnapshotValidationError("analysis missing required field: files")
    if not isinstance(data["files"], list):
        raise SnapshotValidationError("analysis.files must be an array")
    for index, entry in enumerate(data["files"]):
        if not isinstance(entry, dict):
            raise SnapshotValidationError(f"analysis.files[{index}] must be an object")
        if "path" not in entry:
            raise SnapshotValidationError(f"analysis.files[{index}] missing required field: path")
    issues = data.get("issues", [])
    if issues is not None and not isinstance(issues, list):
        raise SnapshotValidationError("analysis.issues must be an array when present")
