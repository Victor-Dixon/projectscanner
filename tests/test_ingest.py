"""Regression tests for deterministic snapshot ingestion."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from projectscanner.ingest import ingest_snapshot


def _write_snapshot(
    snapshot_dir: Path,
    *,
    branch: str = "feature/test",
    workflow_run_id: str = "10",
    file_path: str = "a.py",
    issue_message: str = "first",
) -> None:
    snapshot_dir.mkdir(exist_ok=True)
    metadata = {
        "schema_version": "1.0",
        "commit_sha": "abc123def456",
        "branch": branch,
        "timestamp": "2026-09-10T12:00:00Z",
        "scanner_version": "0.1.0",
        "scan_mode": "pr",
        "duration_seconds": 3,
        "workflow_run_id": workflow_run_id,
    }
    analysis = {
        "schema_version": "1.0",
        "total_files": 1,
        "files": [
            {
                "path": file_path,
                "language": ".py",
                "hash": f"hash-{file_path}",
                "functions": 2,
                "classes": 1,
                "loc": 12,
            }
        ],
        "issues": [
            {
                "rule": "demo-rule",
                "severity": "warning",
                "file_path": file_path,
                "message": issue_message,
                "line_start": 4,
            }
        ],
    }
    (snapshot_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (snapshot_dir / "analysis.json").write_text(json.dumps(analysis), encoding="utf-8")


def test_duplicate_ingest_is_row_idempotent(tmp_path: Path) -> None:
    snapshot_dir = tmp_path / "snapshot"
    db_path = tmp_path / "history.db"
    _write_snapshot(snapshot_dir)

    first = ingest_snapshot(snapshot_dir, repo_name="demo", db_path=db_path)
    second = ingest_snapshot(snapshot_dir, repo_name="demo", db_path=db_path)

    assert first["files_written"] == second["files_written"] == 1
    assert first["issues_written"] == second["issues_written"] == 1

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM files").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM issues").fetchone()[0] == 1


def test_reingest_reconciles_metadata_files_and_issues(tmp_path: Path) -> None:
    snapshot_dir = tmp_path / "snapshot"
    db_path = tmp_path / "history.db"
    _write_snapshot(snapshot_dir)
    ingest_snapshot(snapshot_dir, repo_name="demo", db_path=db_path)

    _write_snapshot(
        snapshot_dir,
        branch="master",
        workflow_run_id="11",
        file_path="b.py",
        issue_message="replacement",
    )
    ingest_snapshot(snapshot_dir, repo_name="demo", db_path=db_path)

    with sqlite3.connect(db_path) as conn:
        snapshot = conn.execute(
            "SELECT branch, workflow_run_id, total_files FROM snapshots WHERE repo = ? AND commit_sha = ?",
            ("demo", "abc123def456"),
        ).fetchone()
        assert snapshot == ("master", "11", 1)

        files = conn.execute(
            "SELECT path, language, file_hash, functions_count, classes_count, loc_estimate FROM files"
        ).fetchall()
        assert files == [("b.py", ".py", "hash-b.py", 2, 1, 12)]

        issues = conn.execute(
            "SELECT rule, severity, file_path, message, line_start FROM issues"
        ).fetchall()
        assert issues == [("demo-rule", "warning", "b.py", "replacement", 4)]
