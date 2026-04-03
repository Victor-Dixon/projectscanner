#!/usr/bin/env python3
"""Ingest scanner snapshot artifacts into SQLite for trend/history analysis."""

import argparse
import json
import sqlite3
from pathlib import Path

DB_PATH = Path("scanner_history.db")


def init_db() -> sqlite3.Connection:
    """Initialize DB schema and indexes."""
    conn = sqlite3.connect(DB_PATH)
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


def ingest_snapshot(snapshot_dir: Path, repo_name: str = "default") -> None:
    """Ingest one snapshot directory that contains metadata.json + analysis.json."""
    metadata_path = snapshot_dir / "metadata.json"
    analysis_path = snapshot_dir / "analysis.json"

    if not metadata_path.exists() or not analysis_path.exists():
        raise FileNotFoundError(f"Missing metadata or analysis in {snapshot_dir}")

    with metadata_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    with analysis_path.open("r", encoding="utf-8") as f:
        analysis = json.load(f)

    conn = init_db()
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
            analysis.get("total_files", 0),
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
        existing = cursor.fetchone()
        if existing is None:
            raise RuntimeError("Unable to resolve snapshot id after insert.")
        snapshot_id = existing[0]

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

    print(
        f"Ingested snapshot {metadata['commit_sha'][:8]} "
        f"({metadata.get('scan_mode')}) - {analysis.get('total_files', 0)} files"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest scanner snapshots into SQLite")
    parser.add_argument("snapshot_dir", help="Path to snapshot directory")
    parser.add_argument("--repo", default="default", help="Repository name")
    args = parser.parse_args()

    ingest_snapshot(Path(args.snapshot_dir), args.repo)


if __name__ == "__main__":
    main()
