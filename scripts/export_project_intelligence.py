#!/usr/bin/env python3
"""Backward-compatible portfolio export script."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

from projectscanner.export_intelligence import export_portfolio

warnings.warn(
    "scripts/export_project_intelligence.py is deprecated; use `projectscanner export`.",
    DeprecationWarning,
    stacklevel=1,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects-root", default=str(Path.home() / "projects"))
    parser.add_argument("--out-root", required=True)
    parser.add_argument("--repos", nargs="*", default=None)
    args = parser.parse_args()

    result = export_portfolio(
        projects_root=Path(args.projects_root),
        out_root=Path(args.out_root),
        repos=args.repos,
    )
    print("PROJECTSCANNER_INTELLIGENCE_EXPORT=PASS")
    print(f"REPOS={result['repos']}")
    print(f"OUT_ROOT={result['out_root']}")
    return 0


# Re-export helpers used by tests
from projectscanner.export_intelligence import docs_score, markers, scan_repo, write_bundle  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
