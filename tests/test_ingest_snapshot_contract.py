import json
import sqlite3
from pathlib import Path

import pytest

from ingest_snapshot import ingest_snapshot
from src.core.projectscanner.snapshot_contract import SNAPSHOT_CONTRACT_VERSION, SnapshotContractError


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _metadata(**overrides):
    payload = {
        "commit_sha": "abc123def456",
        "branch": "main",
        "timestamp": "2026-07-27T12-00-00Z",
        "scanner_version": "0.1.0",
        "scan_mode": "main",
        "duration_seconds": 3,
        "workflow_run_id": "99",
    }
    payload.update(overrides)
    return payload


def _analysis(**overrides):
    payload = {
        "schema": SNAPSHOT_CONTRACT_VERSION,
        "total_files": 2,
        "files": [
            {
                "path": "src/a.py",
                "language": ".py",
                "hash": "hash-a",
                "functions_count": 2,
                "classes_count": 1,
                "loc": 10,
                "raw": {"functions": ["one", "two"], "classes": ["A"]},
            },
            {
                "path": "src/b.js",
                "language": ".js",
                "hash": "hash-b",
                "functions_count": 1,
                "classes_count": 0,
                "loc": 4,
                "raw": {"functions": ["run"], "classes": []},
            },
        ],
        "issues": [
            {
                "rule": "long_function",
                "severity": "warning",
                "file_path": "src/a.py",
                "message": "too long",
                "line_start": 7,
            }
        ],
    }
    payload.update(overrides)
    return payload


def _snapshot_dir(tmp_path: Path, *, metadata=None, analysis=None) -> Path:
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    _write_json(snapshot / "metadata.json", _metadata() if metadata is None else metadata)
    _write_json(snapshot / "analysis.json", _analysis() if analysis is None else analysis)
    return snapshot


def _count(db_path: Path, table: str) -> int:
    with sqlite3.connect(db_path) as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_ingest_requires_metadata_file(tmp_path):
    snapshot = _snapshot_dir(tmp_path)
    (snapshot / "metadata.json").unlink()

    with pytest.raises(FileNotFoundError, match="metadata.json"):
        ingest_snapshot(snapshot, "repo", db_path=tmp_path / "history.db")


def test_ingest_requires_analysis_file(tmp_path):
    snapshot = _snapshot_dir(tmp_path)
    (snapshot / "analysis.json").unlink()

    with pytest.raises(FileNotFoundError, match="analysis.json"):
        ingest_snapshot(snapshot, "repo", db_path=tmp_path / "history.db")


def test_ingest_rejects_metadata_without_commit_sha(tmp_path):
    metadata = _metadata()
    del metadata["commit_sha"]
    snapshot = _snapshot_dir(tmp_path, metadata=metadata)

    with pytest.raises(SnapshotContractError, match="commit_sha"):
        ingest_snapshot(snapshot, "repo", db_path=tmp_path / "history.db")


def test_ingest_rejects_analysis_without_files_list(tmp_path):
    analysis = _analysis()
    del analysis["files"]
    snapshot = _snapshot_dir(tmp_path, analysis=analysis)

    with pytest.raises(SnapshotContractError, match="files"):
        ingest_snapshot(snapshot, "repo", db_path=tmp_path / "history.db")


def test_ingest_rejects_malformed_analysis_payload(tmp_path):
    snapshot = _snapshot_dir(tmp_path, analysis=["not", "an", "object"])

    with pytest.raises(SnapshotContractError, match="JSON object"):
        ingest_snapshot(snapshot, "repo", db_path=tmp_path / "history.db")


def test_ingest_is_idempotent_for_same_repo_and_commit(tmp_path):
    snapshot = _snapshot_dir(tmp_path)
    db_path = tmp_path / "history.db"

    ingest_snapshot(snapshot, "repo", db_path=db_path)
    ingest_snapshot(snapshot, "repo", db_path=db_path)

    assert _count(db_path, "snapshots") == 1
    assert _count(db_path, "files") == 2
    assert _count(db_path, "issues") == 1


def test_ingest_preserves_file_and_issue_counts(tmp_path):
    snapshot = _snapshot_dir(tmp_path)
    db_path = tmp_path / "history.db"

    ingest_snapshot(snapshot, "repo", db_path=db_path)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        snap = conn.execute("SELECT total_files FROM snapshots").fetchone()
        files = conn.execute(
            "SELECT path, functions_count, classes_count, loc_estimate FROM files ORDER BY path"
        ).fetchall()
        issues = conn.execute(
            "SELECT rule, severity, file_path, message, line_start FROM issues"
        ).fetchall()

    assert snap["total_files"] == 2
    assert [row["path"] for row in files] == ["src/a.py", "src/b.js"]
    assert files[0]["functions_count"] == 2
    assert files[0]["classes_count"] == 1
    assert files[0]["loc_estimate"] == 10
    assert len(issues) == 1
    assert dict(issues[0]) == {
        "rule": "long_function",
        "severity": "warning",
        "file_path": "src/a.py",
        "message": "too long",
        "line_start": 7,
    }
