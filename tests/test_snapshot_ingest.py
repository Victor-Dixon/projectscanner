import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import json
import sqlite3

import pytest

import ingest_snapshot


@pytest.fixture()
def temp_db(monkeypatch, tmp_path):
    db_path = tmp_path / "history.db"
    monkeypatch.setattr(ingest_snapshot, "DB_PATH", db_path)
    return db_path


def _write_snapshot(snapshot_dir: Path, metadata: dict, analysis: dict) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (snapshot_dir / "analysis.json").write_text(json.dumps(analysis), encoding="utf-8")


def test_first_insert_and_duplicate_insert_deterministic(temp_db, tmp_path):
    snapshot_dir = tmp_path / "snapshot-a"
    _write_snapshot(
        snapshot_dir,
        {
            "commit_sha": "abc123",
            "timestamp": "2026-04-06T00:00:00Z",
            "scan_mode": "pull_request",
        },
        {
            "total_files": 1,
            "files": [{"path": "src/a.py", "loc": 10}],
            "issues": [{"rule": "R1", "severity": "low", "file_path": "src/a.py"}],
        },
    )

    ingest_snapshot.ingest_snapshot(snapshot_dir, repo_name="repo1")
    ingest_snapshot.ingest_snapshot(snapshot_dir, repo_name="repo1")

    conn = sqlite3.connect(temp_db)
    snapshot_count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    file_count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    issue_count = conn.execute("SELECT COUNT(*) FROM issues").fetchone()[0]
    scan_mode = conn.execute("SELECT scan_mode FROM snapshots LIMIT 1").fetchone()[0]
    conn.close()

    assert snapshot_count == 1
    assert file_count == 1
    assert issue_count == 2
    assert scan_mode == "pr"


def test_missing_snapshot_files_fail_clearly(temp_db, tmp_path):
    snapshot_dir = tmp_path / "snapshot-missing"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    with pytest.raises(FileNotFoundError, match="metadata.json"):
        ingest_snapshot.ingest_snapshot(snapshot_dir)

    (snapshot_dir / "metadata.json").write_text(
        json.dumps(
            {
                "commit_sha": "abc123",
                "timestamp": "2026-04-06T00:00:00Z",
                "scan_mode": "main",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="analysis.json"):
        ingest_snapshot.ingest_snapshot(snapshot_dir)


def test_missing_required_fields_fail_before_write(temp_db, tmp_path):
    snapshot_dir = tmp_path / "snapshot-invalid"
    _write_snapshot(
        snapshot_dir,
        {
            "timestamp": "2026-04-06T00:00:00Z",
            "scan_mode": "main",
        },
        {
            "files": [{"path": "src/a.py"}],
        },
    )

    with pytest.raises(ValueError, match="commit_sha"):
        ingest_snapshot.ingest_snapshot(snapshot_dir)

    conn = ingest_snapshot.init_db()
    snapshot_count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    conn.close()
    assert snapshot_count == 0


def test_invalid_analysis_structure_fails_before_write(temp_db, tmp_path):
    snapshot_dir = tmp_path / "snapshot-invalid-analysis"
    _write_snapshot(
        snapshot_dir,
        {
            "commit_sha": "abc123",
            "timestamp": "2026-04-06T00:00:00Z",
            "scan_mode": "main",
        },
        {
            "files": "not-a-list",
        },
    )

    with pytest.raises(ValueError, match="files"):
        ingest_snapshot.ingest_snapshot(snapshot_dir)

    conn = ingest_snapshot.init_db()
    snapshot_count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    conn.close()
    assert snapshot_count == 0
