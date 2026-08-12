"""Backward-compatible wrapper for ``projectscanner ingest``."""

from __future__ import annotations

import warnings

from projectscanner.ingest import ingest_snapshot

warnings.warn(
    "ingest_snapshot.py is deprecated; use `projectscanner ingest`.",
    DeprecationWarning,
    stacklevel=1,
)

if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Ingest scanner snapshots into SQLite")
    parser.add_argument("snapshot_dir", help="Path to snapshot directory")
    parser.add_argument("--repo", default="default", help="Repository name")
    args = parser.parse_args()
    result = ingest_snapshot(Path(args.snapshot_dir), repo_name=args.repo)
    print(
        f"Ingested snapshot {result['commit_sha'][:8]} "
        f"({result.get('scan_mode')}) - {result['total_files']} files"
    )
