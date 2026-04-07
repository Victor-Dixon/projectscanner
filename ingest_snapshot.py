#!/usr/bin/env python3
"""Ingest scanner snapshot artifacts into SQLite for trend/history analysis."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Add src to path (SSOT runtime package root).
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from core.projectscanner.snapshot_contract import (
    validate_analysis_payload,
    validate_metadata_payload,
)

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


def _load_snapshot_payloads(snapshot_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    metadata_path = snapshot_dir / "metadata.json"
    analysis_path = snapshot_dir / "analysis.json"

    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing metadata.json in {snapshot_dir}")
    if not analysis_path.exists():
        raise FileNotFoundError(f"Missing analysis.json in {snapshot_dir}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))

    validated_metadata = validate_metadata_payload(metadata)
    validated_analysis = validate_analysis_payload(analysis)
    return validated_metadata, validated_analysis


def ingest_snapshot(snapshot_dir: Path, repo_name: str = "default") -> None:
    """Ingest one snapshot directory that contains metadata.json + analysis.json."""
    metadata, analysis = _load_snapshot_payloads(snapshot_dir)

    conn = init_db()
    cursor = conn.cursor()

    try:
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
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print(
        f"Ingested snapshot {metadata['commit_sha'][:8]} "
        f"({metadata.get('scan_mode')}) - {analysis.get('total_files', 0)} files"
    )


def _snapshot_with_issue_count(
    conn: sqlite3.Connection,
    repo_name: str,
    commit_sha: str | None,
    offset: int,
) -> sqlite3.Row | None:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if commit_sha:
        cursor.execute(
            """
            SELECT s.*, COUNT(i.id) AS issue_count
            FROM snapshots s
            LEFT JOIN issues i ON i.snapshot_id = s.id
            WHERE s.repo = ? AND s.commit_sha = ?
            GROUP BY s.id
            LIMIT 1
            """,
            (repo_name, commit_sha),
        )
    else:
        cursor.execute(
            """
            SELECT s.*, COUNT(i.id) AS issue_count
            FROM snapshots s
            LEFT JOIN issues i ON i.snapshot_id = s.id
            WHERE s.repo = ?
            GROUP BY s.id
            ORDER BY s.scanned_at DESC, s.id DESC
            LIMIT 1 OFFSET ?
            """,
            (repo_name, offset),
        )
    return cursor.fetchone()


def calculate_trend_delta(
    repo_name: str = "default",
    current_commit: str | None = None,
    previous_commit: str | None = None,
) -> dict[str, Any]:
    """Compute delta between two snapshots for key metrics."""
    conn = init_db()
    try:
        current = _snapshot_with_issue_count(conn, repo_name, current_commit, 0)
        previous = _snapshot_with_issue_count(conn, repo_name, previous_commit, 1)

        if current is None or previous is None:
            raise ValueError("Need two snapshots to compute trend delta")

        total_files_delta = (current["total_files"] or 0) - (previous["total_files"] or 0)
        issues_delta = (current["issue_count"] or 0) - (previous["issue_count"] or 0)

        return {
            "repo": repo_name,
            "current": {
                "commit_sha": current["commit_sha"],
                "scanned_at": current["scanned_at"],
                "scan_mode": current["scan_mode"],
                "total_files": current["total_files"] or 0,
                "issue_count": current["issue_count"] or 0,
            },
            "previous": {
                "commit_sha": previous["commit_sha"],
                "scanned_at": previous["scanned_at"],
                "scan_mode": previous["scan_mode"],
                "total_files": previous["total_files"] or 0,
                "issue_count": previous["issue_count"] or 0,
            },
            "delta": {
                "total_files": total_files_delta,
                "issue_count": issues_delta,
            },
        }
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest scanner snapshots into SQLite")
    parser.add_argument("snapshot_dir", nargs="?", help="Path to snapshot directory")
    parser.add_argument("--repo", default="default", help="Repository name")
    parser.add_argument("--trend", action="store_true", help="Print trend delta JSON")
    parser.add_argument("--current-commit", help="Current snapshot commit sha")
    parser.add_argument("--previous-commit", help="Previous snapshot commit sha")
    args = parser.parse_args()

    if args.trend:
        delta = calculate_trend_delta(
            repo_name=args.repo,
            current_commit=args.current_commit,
            previous_commit=args.previous_commit,
        )
        print(json.dumps(delta, indent=2))
        return

    if not args.snapshot_dir:
        parser.error("snapshot_dir is required unless --trend is used")

    ingest_snapshot(Path(args.snapshot_dir), args.repo)


if __name__ == "__main__":
    main()
