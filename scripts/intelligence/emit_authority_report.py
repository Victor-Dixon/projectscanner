#!/usr/bin/env python3
"""Emit a read-only portfolio authority report for one or more repo paths.

Example (four-target controlled scan; pass local roots as CLI args):

  python scripts/intelligence/emit_authority_report.py \\
    --out runtime/reports/authority_slice \\
    /path/to/Dream.os-Core \\
    /path/to/Dream.os \\
    /path/to/agent-tools \\
    /path/to/projectscanner

Classifications are scoped to the supplied path set (host-local controlled scan).
A "canonical" label here is not portfolio-wide authority promotion.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "src"))

from scan_targets import (  # noqa: E402
    as_target_dict,
    make_local_target,
    target_summary,
    write_target_manifest,
)
from project_artifact_standards import expected_dir_for_target  # noqa: E402
from core.intelligence.authority_report import write_authority_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Repository roots to inspect (read-only)")
    parser.add_argument(
        "--out",
        default=str(_ROOT / "runtime" / "reports" / "authority_slice"),
        help="Output directory for JSON + Markdown reports",
    )
    parser.add_argument(
        "--write-targets",
        action="store_true",
        help="Also write runtime/targets/local_scan_targets_latest.json for the slice",
    )
    args = parser.parse_args()

    paths = [Path(p).expanduser().resolve() for p in args.paths]
    targets = [make_local_target(p) for p in paths]

    # Exercise the four-target ScanTarget↔dict boundary (was AttributeError).
    for target in targets:
        _ = expected_dir_for_target(target)
        _ = expected_dir_for_target(as_target_dict(target))
        _ = target_summary(target)
        _ = target_summary(as_target_dict(target))

    if args.write_targets:
        manifest = write_target_manifest(
            targets, _ROOT / "runtime" / "targets" / "local_scan_targets_latest.json"
        )
        print(f"targets_manifest: {manifest}")

    json_path, md_path, report = write_authority_report(paths, out_dir=args.out)
    print(f"authority_report_json: {json_path}")
    print(f"authority_report_md: {md_path}")
    print(f"repo_count: {report.get('repo_count')}")
    print(f"summary: {json.dumps(report.get('summary'), sort_keys=True)}")
    print("AUTHORITY_REPORT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
