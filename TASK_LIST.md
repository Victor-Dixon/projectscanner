# Historical Task List

Last synchronized: 2026-07-03

This file is retained as a historical pointer only. The canonical task inventory is [`MASTER_TASK_LIST.md`](MASTER_TASK_LIST.md), and the active handoff is [`NEXT_UP.md`](NEXT_UP.md).

## Why this file is not authoritative

The previous contents described a planned `src/core/scanner/unified_scanner.py` and `scripts/scanners/*` wrappers. Current tests and documentation establish `src/core/projectscanner/` as the scanner source of truth and explicitly avoid parallel scanner implementations.

## Current project summary

ProjectScanner is repository scanning and inventory intelligence tooling in the software repository analysis domain. It exists to produce machine-readable evidence about local and GitHub repositories before cleanup, consolidation, promotion, or automation decisions.

## Completed

- Core scanner/report/context path exists under `src/core/projectscanner/`.
- Required lifecycle docs have been synchronized.
- Domain model and repository audit have been added.

## What remains

See `MASTER_TASK_LIST.md`.

## What should be worked on next

See `NEXT_UP.md`.
