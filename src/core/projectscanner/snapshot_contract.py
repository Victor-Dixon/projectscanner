"""Snapshot payload validation for ingest contract enforcement."""

from __future__ import annotations

from typing import Any

from .workflow_mode import normalize_workflow_mode

_METADATA_REQUIRED = {
    "commit_sha": str,
    "timestamp": str,
    "scan_mode": str,
}


def _ensure_dict(payload: Any, payload_name: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"{payload_name} must be a JSON object")
    return payload


def validate_metadata_payload(metadata: Any) -> dict[str, Any]:
    """Validate metadata payload and normalize mode in-place copy."""
    data = _ensure_dict(metadata, "metadata.json")

    for field, expected_type in _METADATA_REQUIRED.items():
        if field not in data:
            raise ValueError(f"metadata.json missing required field: {field}")
        if not isinstance(data[field], expected_type) or not str(data[field]).strip():
            raise ValueError(f"metadata.json field '{field}' must be a non-empty {expected_type.__name__}")

    normalized = dict(data)
    normalized["scan_mode"] = normalize_workflow_mode(data.get("scan_mode"))
    return normalized


def validate_analysis_payload(analysis: Any) -> dict[str, Any]:
    """Validate analysis payload schema required by ingest path."""
    data = _ensure_dict(analysis, "analysis.json")

    files = data.get("files")
    if files is None:
        raise ValueError("analysis.json missing required field: files")
    if not isinstance(files, list):
        raise ValueError("analysis.json field 'files' must be a list")

    for index, item in enumerate(files):
        if not isinstance(item, dict):
            raise ValueError(f"analysis.json files[{index}] must be an object")
        path = item.get("path")
        if path is not None and not isinstance(path, str):
            raise ValueError(f"analysis.json files[{index}].path must be a string when present")

    issues = data.get("issues", [])
    if not isinstance(issues, list):
        raise ValueError("analysis.json field 'issues' must be a list when present")

    return data
