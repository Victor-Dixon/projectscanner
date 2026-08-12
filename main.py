"""Deprecated entry point. Install and use ``projectscanner`` instead."""

from __future__ import annotations

import sys
import warnings

from projectscanner.cli import build_parser, main

warnings.warn(
    "main.py is deprecated; use the `projectscanner` command (pip install -e .).",
    DeprecationWarning,
    stacklevel=1,
)


def _map_legacy_args(argv: list[str]) -> list[str] | None:
    if not argv:
        return None

    if argv[0] == "--gui":
        return ["gui"]

    mapped: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--scan" and i + 1 < len(argv):
            return ["scan", argv[i + 1], *argv[i + 2 :]]
        if arg == "--quick-scan" and i + 1 < len(argv):
            return ["scan", argv[i + 1], *argv[i + 2 :]]
        if arg in {"--analyze", "--strategic"}:
            print(f"Error: {arg} is not available in v0.1. Use `projectscanner export`.", file=sys.stderr)
            return ["--help"]
        mapped.append(arg)
        i += 1

    if mapped and not mapped[0].startswith("-"):
        return ["scan", *mapped]
    return mapped


if __name__ == "__main__":
    legacy = _map_legacy_args(sys.argv[1:])
    if legacy is None:
        build_parser().print_help()
        raise SystemExit(0)
    raise SystemExit(main(legacy))
