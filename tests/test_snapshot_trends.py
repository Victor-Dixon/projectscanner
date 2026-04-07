import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import json

import pytest

import ingest_snapshot


@pytest.fixture()
def temp_db(monkeypatch, tmp_path):
    db_path = tmp_path / "history.db"
    monkeypatch.setattr(ingest_snapshot, "DB_PATH", db_path)
    return db_path


def _write_snapshot(snapshot_dir: Path, commit_sha: str, timestamp: str, total_files: int, issue_count: int):
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / "metadata.json").write_text(
        json.dumps(
            {
                "commit_sha": commit_sha,
                "timestamp": timestamp,
                "scan_mode": "main",
            }
        ),
        encoding="utf-8",
    )
    issues = [
        {"rule": f"R{i}", "severity": "low", "file_path": "src/a.py", "message": "m"}
        for i in range(issue_count)
    ]
    (snapshot_dir / "analysis.json").write_text(
        json.dumps({"total_files": total_files, "files": [{"path": "src/a.py"}], "issues": issues}),
        encoding="utf-8",
    )


def test_calculate_trend_delta_latest_two_snapshots(temp_db, tmp_path):
    _write_snapshot(tmp_path / "s1", "111111", "2026-04-05T00:00:00Z", 3, 1)
    _write_snapshot(tmp_path / "s2", "222222", "2026-04-06T00:00:00Z", 5, 4)

    ingest_snapshot.ingest_snapshot(tmp_path / "s1", repo_name="repo1")
    ingest_snapshot.ingest_snapshot(tmp_path / "s2", repo_name="repo1")

    trend = ingest_snapshot.calculate_trend_delta(repo_name="repo1")
    assert trend["current"]["commit_sha"] == "222222"
    assert trend["previous"]["commit_sha"] == "111111"
    assert trend["delta"]["total_files"] == 2
    assert trend["delta"]["issue_count"] == 3


def test_calculate_trend_delta_requires_two_snapshots(temp_db):
    with pytest.raises(ValueError, match="Need two snapshots"):
        ingest_snapshot.calculate_trend_delta(repo_name="repo1")
