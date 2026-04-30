"""
MODULE: run_scanner
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""Project Scanner CLI runner with repo-root SSOT target resolution."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add src to path (SSOT: repo-root/src)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.projectscanner import ProjectScanner


# Concept: TODO - Explain the core idea behind get_repo_root
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def get_repo_root() -> str:
# Concept: TODO
# Trade-off: TODO
# Execution: TODO
    """Return absolute path to git repo root, or fallback to current working directory."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return os.getcwd()


# Concept: TODO - Explain the core idea behind resolve_target_path
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def resolve_target_path(args_target: str | None = None) -> str:
    """
    Resolve scan target path with the following priority:
    1. CLI --target override
    2. repo_root/src (SSOT default)
    3. repo_root fallback
    """
# Concept: TODO - Purpose of resolve_target_path
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    repo_root = get_repo_root()

    if args_target:
        target = (
            os.path.join(repo_root, args_target)
            if not os.path.isabs(args_target)
            else args_target
        )
    else:
        default_src = os.path.join(repo_root, "src")
        target = default_src if os.path.exists(default_src) else repo_root

    target = os.path.abspath(target)
    if not os.path.exists(target):
        raise FileNotFoundError(f"Target path does not exist: {target}")

    return target


# Concept: TODO - Explain the core idea behind main
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 46 lines > 30 limit)
def main() -> None:
# Concept: TODO - Purpose of main
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    parser = argparse.ArgumentParser(description="Project Scanner CLI")
    parser.add_argument(
        "project_path",
        nargs="?",
        default=None,
        help="Legacy positional target path (deprecated; use --target)",
    )
    parser.add_argument(
        "--target",
        help="Override scan target (relative to repo root or absolute)",
    )
    parser.add_argument("--output", "-o", help="Output directory", default=".")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--mode",
        choices=["pr", "main", "nightly", "release", "manual"],
        default="pr",
        help="Execution mode for CI/metadata labeling.",
    )

    args = parser.parse_args()

    requested_target = args.target or args.project_path
    scan_target = resolve_target_path(requested_target)
    print(f"Scanning: {scan_target} (mode={args.mode})")

    scanner = ProjectScanner(project_root=scan_target, output_dir=args.output)

    # Concept: TODO - Explain the core idea behind progress_callback
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def progress_callback(message: str) -> None:
    # Concept: TODO - Purpose of progress_callback
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        if args.verbose:
            print(message)

    scanner.scan_project(progress_callback=progress_callback)
    print("Scan completed successfully!")


if __name__ == "__main__":
    main()
