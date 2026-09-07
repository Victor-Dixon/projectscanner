"""Tests for snapshot contract validation and conversion."""

from __future__ import annotations

import pytest

from core.projectscanner.snapshot_contract import (
    ANALYSIS_SCHEMA_VERSION,
    METADATA_SCHEMA_VERSION,
    SnapshotValidationError,
    build_snapshot_analysis,
    validate_analysis_payload,
    validate_metadata_payload,
)


def test_build_snapshot_analysis_skips_internal_keys():
    payload = build_snapshot_analysis(
        {
            "pkg/a.py": {
                "language": ".py",
                "functions": ["a"],
                "classes": [],
                "complexity": 2,
                "lint": [{"rule": "style", "severity": "low", "message": "ok", "line": 1}],
            },
            "__dependency_graph__": {"pkg/a.py": []},
        }
    )
    assert payload["schema_version"] == ANALYSIS_SCHEMA_VERSION
    assert payload["total_files"] == 1
    assert payload["files"][0]["path"] == "pkg/a.py"
    assert payload["files"][0]["functions"] == 1
    assert len(payload["issues"]) == 1


def test_validate_analysis_payload_rejects_missing_files():
    with pytest.raises(SnapshotValidationError, match="files"):
        validate_analysis_payload({"schema_version": ANALYSIS_SCHEMA_VERSION})


def test_validate_analysis_payload_rejects_wrong_files_type():
    with pytest.raises(SnapshotValidationError, match="array"):
        validate_analysis_payload(
            {"schema_version": ANALYSIS_SCHEMA_VERSION, "files": "nope"}
        )


def test_validate_analysis_payload_rejects_unsupported_schema_version():
    with pytest.raises(SnapshotValidationError, match="schema_version"):
        validate_analysis_payload({"schema_version": "0.9", "files": []})


def test_validate_analysis_payload_rejects_inconsistent_total_files():
    with pytest.raises(SnapshotValidationError, match="total_files"):
        validate_analysis_payload(
            {
                "schema_version": ANALYSIS_SCHEMA_VERSION,
                "total_files": 2,
                "files": [{"path": "pkg/a.py"}],
            }
        )


def test_validate_metadata_payload_requires_commit_sha():
    with pytest.raises(SnapshotValidationError, match="commit_sha"):
        validate_metadata_payload({"schema_version": METADATA_SCHEMA_VERSION})


def test_validate_metadata_payload_rejects_unsupported_schema_version():
    with pytest.raises(SnapshotValidationError, match="schema_version"):
        validate_metadata_payload({"schema_version": "0.9", "commit_sha": "abc123"})


def test_validate_metadata_payload_accepts_current_contract():
    validate_metadata_payload(
        {"schema_version": METADATA_SCHEMA_VERSION, "commit_sha": "abc123"}
    )
