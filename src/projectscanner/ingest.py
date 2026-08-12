"""Ingest scanner snapshot artifacts into SQLite for trend analysis."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from core.projectscanner.snapshot_contract import (
    SnapshotValidationError,
    validate_analysis_payload,
    validate_metadata_payload,
)

DEFAULT_DB_PATH = Path("scanner_history.db")


def init_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY,
            repo TEXT NOT NULL,
            commit_sha TEXT NOT NULL,
            branch TEXT,
            scanned_at DATETIME,
            total_files INTEGER,
            scanner_version TEXT,
            scan_mode TEXT,
            duration_seconds INTEGER,
            workflow_run_id TEXT,
            UNIQUE(repo, commit_sha)
        );

        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            snapshot_id INTEGER REFERENCES snapshots(id),
            path TEXT NOT NULL,
            language TEXT,
            file_hash TEXT,
            functions_count INTEGER,
            classes_count INTEGER,
            loc_estimate INTEGER,
            raw_json TEXT,
            UNIQUE(snapshot_id, path)
        );

        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY,
            snapshot_id INTEGER REFERENCES snapshots(id),
            rule TEXT NOT NULL,
            severity TEXT,
            file_path TEXT,
            message TEXT,
            line_start INTEGER
        );

        CREATE INDEX IF NOT EXISTS idx_files_hash ON files(file_hash);
        CREATE INDEX IF NOT EXISTS idx_snapshots_commit ON snapshots(commit_sha, branch);
        CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues(severity);
        """
    )
    return conn


def load_snapshot(snapshot_dir: Path) -> tuple[dict, dict]:
    metadata_path = snapshot_dir / "metadata.json"
    analysis_path = snapshot_dir / "analysis.json"

    if not metadata_path.exists() or not analysis_path.exists():
        raise FileNotFoundError(f"Missing metadata.json or analysis.json in {snapshot_dir}")

    with metadata_path.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    with analysis_path.open("r", encoding="utf-8") as handle:
        analysis = json.load(handle)

    validate_metadata_payload(metadata)
    validate_analysis_payload(analysis)
    return metadata, analysis


def ingest_snapshot(
    snapshot_dir: Path,
    repo_name: str = "default",
    db_path: Path | None = None,
) -> dict:
    metadata, analysis = load_snapshot(snapshot_dir)
    db = db_path or DEFAULT_DB_PATH
    conn = init_db(db)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO snapshots
        (repo, commit_sha, branch, scanned_at, total_files, scanner_version,
         scan_mode, duration_seconds, workflow_run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            repo_name,
            metadata["commit_sha"],
            metadata.get("branch"),
            metadata.get("timestamp"),
            analysis.get("total_files", len(analysis.get("files", []))),
            metadata.get("scanner_version"),
            metadata.get("scan_mode"),
            metadata.get("duration_seconds"),
            metadata.get("workflow_run_id"),
        ),
    )

    snapshot_id = cursor.lastrowid
    if not snapshot_id:
        cursor.execute(
            "SELECT id FROM snapshots WHERE repo = ? AND commit_sha = ?",
            (repo_name, metadata["commit_sha"]),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Unable to resolve snapshot id after insert.")
        snapshot_id = row[0]

    for file_data in analysis.get("files", []):
        cursor.execute(
            """
            INSERT OR REPLACE INTO files
            (snapshot_id, path, language, file_hash, functions_count,
             classes_count, loc_estimate, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                file_data.get("path"),
                file_data.get("language"),
                file_data.get("hash"),
                file_data.get("functions", 0),
                file_data.get("classes", 0),
                file_data.get("loc", 0),
                json.dumps(file_data),
            ),
        )

    for issue in analysis.get("issues", []):
        cursor.execute(
            """
            INSERT INTO issues
            (snapshot_id, rule, severity, file_path, message, line_start)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                issue.get("rule"),
                issue.get("severity"),
                issue.get("file_path"),
                issue.get("message"),
                issue.get("line_start"),
            ),
        )

    conn.commit()
    conn.close()

    return {
        "commit_sha": metadata["commit_sha"],
        "scan_mode": metadata.get("scan_mode"),
        "total_files": analysis.get("total_files", len(analysis.get("files", []))),
        "files_written": len(analysis.get("files", [])),
        "issues_written": len(analysis.get("issues", [])),
        "db_path": str(db),
    }


__all__ = [
    "DEFAULT_DB_PATH",
    "SnapshotValidationError",
    "ingest_snapshot",
    "init_db",
    "load_snapshot",
]
