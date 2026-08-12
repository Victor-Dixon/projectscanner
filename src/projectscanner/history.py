"""Query scanner history database for snapshot trends."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from projectscanner.ingest import DEFAULT_DB_PATH, init_db


def fetch_recent_snapshots(db_path: Path | None = None, limit: int = 10) -> list[dict]:
    db = db_path or DEFAULT_DB_PATH
    if not db.exists():
        return []

    conn = init_db(db)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT repo, commit_sha, branch, scanned_at, total_files, scan_mode, duration_seconds
        FROM snapshots
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "repo": row[0],
            "commit_sha": row[1],
            "branch": row[2],
            "scanned_at": row[3],
            "total_files": row[4],
            "scan_mode": row[5],
            "duration_seconds": row[6],
        }
        for row in rows
    ]


def format_history_table(rows: list[dict]) -> str:
    if not rows:
        return "No snapshots ingested yet."

    lines = [
        "commit     branch     files  mode      scanned_at",
        "---------  ---------  -----  --------  -------------------",
    ]
    for row in rows:
        commit = (row.get("commit_sha") or "")[:8]
        branch = (row.get("branch") or "-")[:9]
        files = str(row.get("total_files") or 0).rjust(5)
        mode = (row.get("scan_mode") or "-")[:8]
        scanned = row.get("scanned_at") or "-"
        lines.append(f"{commit:<9}  {branch:<9}  {files}  {mode:<8}  {scanned}")
    return "\n".join(lines)


def file_count_delta(db_path: Path | None = None) -> int | None:
    rows = fetch_recent_snapshots(db_path=db_path, limit=2)
    if len(rows) < 2:
        return None
    latest, previous = rows[0], rows[1]
    if latest.get("total_files") is None or previous.get("total_files") is None:
        return None
    return int(latest["total_files"]) - int(previous["total_files"])
