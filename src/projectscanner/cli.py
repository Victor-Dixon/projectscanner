"""Unified ProjectScanner command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from core.projectscanner import ProjectScanner, build_snapshot_analysis
from projectscanner.export_intelligence import export_portfolio
from projectscanner.history import fetch_recent_snapshots, file_count_delta, format_history_table
from projectscanner.ingest import SnapshotValidationError, ingest_snapshot


def _cmd_scan(args: argparse.Namespace) -> int:
    target = Path(args.path).resolve()
    if not target.exists():
        print(f"Error: scan path does not exist: {target}", file=sys.stderr)
        return 1

    output_dir = Path(args.output).resolve() if args.output else None
    scanner = ProjectScanner(project_root=target, output_dir=output_dir)
    scanner.scan_project(
        export_context=args.export_context,
        split_output_by=args.split_by,
        max_files_per_chunk=args.max_files_per_chunk,
    )
    if args.generate_init:
        scanner.generate_init_files()

    contract_path = scanner.output_dir / "analysis.json"
    contract_path.write_text(
        json.dumps(build_snapshot_analysis(scanner.analysis), indent=2),
        encoding="utf-8",
    )

    out = scanner.output_dir
    print(f"Scan complete. Results saved to: {out}")
    print(f"  - {scanner.report_generator.analysis_file}")
    print("  - analysis.json")
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    result = export_portfolio(
        projects_root=Path(args.projects_root),
        out_root=Path(args.out_root),
        repos=args.repos,
    )
    print("PROJECTSCANNER_INTELLIGENCE_EXPORT=PASS")
    print(f"REPOS={result['repos']}")
    print(f"OUT_ROOT={result['out_root']}")
    return 0


def _cmd_ingest(args: argparse.Namespace) -> int:
    try:
        result = ingest_snapshot(
            Path(args.snapshot_dir),
            repo_name=args.repo,
            db_path=Path(args.db) if args.db else None,
        )
    except (FileNotFoundError, SnapshotValidationError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Ingested snapshot {result['commit_sha'][:8]} "
        f"({result.get('scan_mode')}) - {result['total_files']} files"
    )
    return 0


def _cmd_history(args: argparse.Namespace) -> int:
    db_path = Path(args.db) if args.db else None
    rows = fetch_recent_snapshots(db_path=db_path, limit=args.last)
    print(format_history_table(rows))
    delta = file_count_delta(db_path=db_path)
    if delta is not None:
        sign = "+" if delta >= 0 else ""
        print(f"\nFile count delta vs previous snapshot: {sign}{delta}")
    return 0


def _cmd_gui(_: argparse.Namespace) -> int:
    try:
        import PyQt5  # noqa: F401
    except ImportError:
        print(
            "GUI requires optional dependencies. Install with:\n"
            "  pip install 'projectscanner[gui]'",
            file=sys.stderr,
        )
        return 1

    try:
        from gui.main import run_gui
    except ImportError:
        try:
            from gui.main.run_gui import main as run_gui_main

            run_gui_main()
            return 0
        except ImportError as exc:
            print(f"GUI module unavailable: {exc}", file=sys.stderr)
            return 1

    if hasattr(run_gui, "main"):
        run_gui.main()
    else:
        print("GUI launcher found but exposes no main() entry point.", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="projectscanner",
        description="Repo intelligence scanner for Dream.OS portfolios",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan a project directory")
    scan.add_argument("path", help="Path to scan")
    scan.add_argument("--output", "-o", help="Output directory for reports")
    scan.add_argument("--export-context", action="store_true", help="Export ChatGPT context")
    scan.add_argument("--generate-init", action="store_true", help="Generate __init__.py files")
    scan.add_argument(
        "--split-by",
        choices=["directory", "language", "none"],
        default="directory",
        help="Context chunking strategy",
    )
    scan.add_argument("--max-files-per-chunk", type=int, default=100)
    scan.set_defaults(func=_cmd_scan)

    export = subparsers.add_parser("export", help="Export portfolio intelligence bundle")
    export.add_argument("--projects-root", default=str(Path.home() / "projects"))
    export.add_argument("--out-root", required=True)
    export.add_argument("--repos", nargs="*", default=None)
    export.set_defaults(func=_cmd_export)

    ingest = subparsers.add_parser("ingest", help="Ingest a CI snapshot into SQLite history")
    ingest.add_argument("snapshot_dir", help="Directory with metadata.json and analysis.json")
    ingest.add_argument("--repo", default="default")
    ingest.add_argument("--db", default=None, help="SQLite database path")
    ingest.set_defaults(func=_cmd_ingest)

    history = subparsers.add_parser("history", help="Show recent ingested snapshots")
    history.add_argument("--db", default=None, help="SQLite database path")
    history.add_argument("--last", type=int, default=10)
    history.set_defaults(func=_cmd_history)

    gui = subparsers.add_parser("gui", help="Launch optional GUI (requires [gui] extra)")
    gui.set_defaults(func=_cmd_gui)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
