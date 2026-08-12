#!/usr/bin/env python3
"""Backward-compatible portfolio export script."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

from projectscanner import export_intelligence as _export_intelligence

export_portfolio = _export_intelligence.export_portfolio
docs_score = _export_intelligence.docs_score
markers = _export_intelligence.markers
scan_repo = _export_intelligence.scan_repo
write_bundle = _export_intelligence.write_bundle

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


if __name__ == "__main__":
    raise SystemExit(main())
