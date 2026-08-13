#!/usr/bin/env python3
"""Emit intelligence packet and ecosystem repo graph for a target repo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running without package install
_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))

from core.intelligence.packet_builder import build_intelligence_packet  # noqa: E402
from core.intelligence.repo_graph import build_repo_graph  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit projectscanner observability artifacts")
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Target repo root to scan (default: cwd)",
    )
    parser.add_argument(
        "--projectscanner-root",
        default=str(_ROOT),
        help="projectscanner install root for repo_graph output",
    )
    parser.add_argument("--packet-only", action="store_true")
    parser.add_argument("--graph-only", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    ps_root = Path(args.projectscanner_root).resolve()

    if not args.graph_only:
        packet_path = build_intelligence_packet(repo_root)
        print(f"intelligence_packet: {packet_path}")

    if not args.packet_only:
        graph_path = build_repo_graph(ps_root)
        print(f"repo_graph: {graph_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
