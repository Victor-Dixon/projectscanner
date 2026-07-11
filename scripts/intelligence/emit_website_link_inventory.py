#!/usr/bin/env python3
"""Emit static website link inventory for repo-local nav/href triage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))

from core.intelligence.website_link_inventory import build_inventory, write_inventory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan websites repo for nav links and broken local href targets")
    parser.add_argument("repo", nargs="?", default=r"D:\websites", help="Websites repo root")
    parser.add_argument("--domain", help="Scan single domain folder only")
    parser.add_argument(
        "--output",
        help="Output JSON path (default: <repo>/runtime/state/website_link_inventory_latest.json)",
    )
    parser.add_argument("--print-summary", action="store_true", help="Print triage summary to stdout")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    if not repo_root.is_dir():
        print(f"ERROR: repo not found: {repo_root}")
        return 1

    out = Path(args.output) if args.output else None
    path = write_inventory(repo_root, output_path=out, domain_filter=args.domain)
    doc = build_inventory(repo_root, domain_filter=args.domain)

    summary = doc["summary"]
    print(f"website_link_inventory: {path}")
    print(
        f"WEBSITE_LINK_INVENTORY sites={summary['sites_scanned']} "
        f"nav={summary['nav_links']} broken_local={summary['broken_local_unique']} "
        f"orphans={summary['orphan_pages']}"
    )

    if args.print_summary or args.domain:
        for domain, site in doc.get("sites", {}).items():
            broken = site.get("broken_local") or []
            if not broken:
                continue
            print(f"\n[{domain}] broken_local={len(broken)}")
            seen: set[str] = set()
            for row in broken[:20]:
                key = row["normalized_path"]
                if key in seen:
                    continue
                seen.add(key)
                print(f"  FAIL {row['href']} -> {row['normalized_path']} (from {row['source_file']})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
