#!/usr/bin/env python3
"""Resolve GitHub workflow context to canonical scan mode."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add src to path (SSOT runtime package root).
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.projectscanner.workflow_mode import derive_workflow_mode


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve scan mode from GitHub workflow context")
    parser.add_argument("--event-name", default="")
    parser.add_argument("--ref-type", default="")
    parser.add_argument("--ref-name", default="")
    args = parser.parse_args()

    print(derive_workflow_mode(args.event_name, args.ref_type, args.ref_name))


if __name__ == "__main__":
    main()
