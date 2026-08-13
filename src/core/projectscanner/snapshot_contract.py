"""Snapshot artifact contract helpers for scanner CI output and ingestion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


SNAPSHOT_CONTRACT_VERSION = "projectscanner.snapshot.v1"
REQUIRED_METADATA_FIELDS = ("commit_sha", "timestamp", "scan_mode")
REQUIRED_ANALYSIS_FIELDS = ("schema", "total_files", "files", "issues")


class SnapshotContractError(ValueError):
    """Raised when a snapshot artifact does not match the ingest contract."""


def _count(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, int):
        return value
    return 0


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _file_hash(path: Path) -> str:
    try:
        import hashlib

        hasher = hashlib.md5()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return ""


def _loc(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return sum(1 for _line in handle)
    except (OSError, UnicodeDecodeError):
        return 0


def normalize_analysis_payload(
    analysis: Mapping[str, Any],
    *,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Convert the legacy path-keyed scanner report into analysis.json."""
    files: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    for rel_path, raw in sorted(analysis.items()):
        if rel_path.startswith("__") or not isinstance(raw, Mapping):
            continue

        source_path = project_root / rel_path if project_root else None
        file_item = {
            "path": rel_path,
            "language": raw.get("language", "unknown"),
            "hash": _file_hash(source_path) if source_path else "",
            "functions_count": _count(raw.get("functions")),
            "classes_count": _count(raw.get("classes")),
            "loc": _loc(source_path) if source_path else 0,
            "raw": dict(raw),
        }
        files.append(file_item)

        lint_items = raw.get("lint") or []
        if isinstance(lint_items, list):
            for lint in lint_items:
                issue = _normalize_issue(lint, rel_path)
                if issue:
                    issues.append(issue)

    return {
        "schema": SNAPSHOT_CONTRACT_VERSION,
        "total_files": len(files),
        "files": files,
        "issues": issues,
    }


def _normalize_issue(issue: Any, file_path: str) -> dict[str, Any] | None:
    if isinstance(issue, str):
        return {
            "rule": "lint",
            "severity": "warning",
            "file_path": file_path,
            "message": issue,
            "line_start": None,
        }
    if not isinstance(issue, Mapping):
        return None
    return {
        "rule": str(issue.get("rule") or "lint"),
        "severity": issue.get("severity") or "warning",
        "file_path": issue.get("file_path") or file_path,
        "message": issue.get("message") or _stable_json(issue),
        "line_start": issue.get("line_start"),
    }


def validate_metadata(metadata: Any) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise SnapshotContractError("metadata.json must contain a JSON object")

    missing = [field for field in REQUIRED_METADATA_FIELDS if not metadata.get(field)]
    if missing:
        raise SnapshotContractError(
            "metadata.json missing required field(s): " + ", ".join(missing)
        )
    return metadata


def validate_analysis_payload(analysis: Any) -> dict[str, Any]:
    if not isinstance(analysis, dict):
        raise SnapshotContractError("analysis.json must contain a JSON object")

    missing = [field for field in REQUIRED_ANALYSIS_FIELDS if field not in analysis]
    if missing:
        raise SnapshotContractError(
            "analysis.json missing required field(s): " + ", ".join(missing)
        )

    if analysis.get("schema") != SNAPSHOT_CONTRACT_VERSION:
        raise SnapshotContractError(
            f"analysis.json schema must be {SNAPSHOT_CONTRACT_VERSION}"
        )
    if not isinstance(analysis.get("files"), list):
        raise SnapshotContractError("analysis.json field files must be a list")
    if not isinstance(analysis.get("issues"), list):
        raise SnapshotContractError("analysis.json field issues must be a list")
    if not isinstance(analysis.get("total_files"), int):
        raise SnapshotContractError("analysis.json field total_files must be an integer")

    for index, file_item in enumerate(analysis["files"]):
        if not isinstance(file_item, dict):
            raise SnapshotContractError(f"analysis.json files[{index}] must be an object")
        if not file_item.get("path"):
            raise SnapshotContractError(f"analysis.json files[{index}].path is required")

    for index, issue in enumerate(analysis["issues"]):
        if not isinstance(issue, dict):
            raise SnapshotContractError(f"analysis.json issues[{index}] must be an object")
        if not issue.get("rule"):
            raise SnapshotContractError(f"analysis.json issues[{index}].rule is required")

    return analysis
