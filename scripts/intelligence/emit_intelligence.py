#!/usr/bin/env python3
"""Emit intelligence packet and ecosystem repo graph for a target repo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running without package install
_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))

from core.intelligence.packet_builder import build_intelligence_packet  # noqa: E402
from core.intelligence.repo_graph import build_repo_graph  # noqa: E402
from core.intelligence.packet_validation import (  # noqa: E402
    intelligence_packet_canonical_sha256,
    validate_intelligence_packet,
)


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
    parser.add_argument(
        "--proof-log",
        action="store_true",
        help="Append an emission proof record (NDJSON) under runtime/state/.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    ps_root = Path(args.projectscanner_root).resolve()

    if not args.graph_only:
        packet_path = build_intelligence_packet(repo_root)
        print(f"intelligence_packet: {packet_path}")
        if args.proof_log:
            data = json.loads(packet_path.read_text(encoding="utf-8"))
            validate_intelligence_packet(data)
            canonical = intelligence_packet_canonical_sha256(data)
            proof = {
                "schema": "projectscanner.intelligence_packet.proof.v1",
                "generated_at": data.get("generated_at"),
                "repo": data.get("repo"),
                "packet_path": str(packet_path),
                "canonical_sha256": canonical,
                "dirty_count": (data.get("git") or {}).get("dirty_count"),
                "untracked_count": (data.get("git") or {}).get("untracked_count"),
            }
            proof_path = repo_root / "runtime" / "state" / "intelligence_packet_proof.ndjson"
            proof_path.parent.mkdir(parents=True, exist_ok=True)
            with proof_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(proof, sort_keys=True) + "\n")
            print(f"proof_log: {proof_path}")

    if not args.packet_only:
        graph_path = build_repo_graph(ps_root)
        print(f"repo_graph: {graph_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
