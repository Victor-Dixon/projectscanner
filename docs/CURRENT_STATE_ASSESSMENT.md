# Current State Assessment (No-BS)

## Snapshot as of 2026-04-03

This document reflects the **current repository state** and enforces SSOT assumptions for scanner execution and handoff planning.

## What we have right now

### 1) SSOT scan target resolution is now implemented
- `src/utils/run_scanner.py` now resolves scan targets in this order:
  1. `--target` CLI override,
  2. `repo_root/src` (SSOT default),
  3. `repo_root` fallback.
- Relative `--target` values are resolved against git repo root.
- Non-existent targets fail fast with `FileNotFoundError`.
- Legacy positional target is still accepted for compatibility, but `--target` is now the preferred interface.

### 2) Artifact-first CI snapshot workflow exists
- `.github/workflows/scanner-snapshot.yml` is in place and runs on:
  - push to `main`,
  - pull requests to `main`,
  - nightly schedule,
  - manual dispatch.
- Workflow behavior:
  - determines scan mode from trigger,
  - runs scanner against SSOT target (`./src`),
  - writes `metadata.json`,
  - uploads `snapshots/` as retained artifacts (90 days),
  - posts PR comment summary for PR-triggered runs.

### 3) SQLite ingestor is available for history and trends
- `ingest_snapshot.py` ingests snapshot artifacts into `scanner_history.db`.
- Schema currently includes:
  - `snapshots` (commit/run metadata),
  - `files` (file-level rollup + raw JSON),
  - `issues` (rule/severity/file/message/line).
- Idempotency is handled using unique constraints plus `INSERT OR IGNORE`/`INSERT OR REPLACE` patterns.

### 4) Core architecture status
- Package SSOT remains `src/core/projectscanner/`.
- CLI + utility wrappers should continue to delegate to package internals rather than introduce parallel scanner implementations.
- Project has both operational and strategic docs, but execution and handoff must stay aligned to SSOT runtime paths.

## Risks / gaps still open

1. **Data contract hardening between scanner output and ingestor**
   - `ingest_snapshot.py` assumes `analysis.json` has `files` and optional `issues` arrays with expected keys.
   - Add explicit schema/version checks to avoid silent drift.

2. **CI confidence depth**
   - Workflow path is present, but more test coverage is needed for:
     - mode derivation,
     - metadata integrity,
     - PR comment safety when fields are absent.

3. **Trend query ergonomics**
   - Ingest path exists; no dedicated query/report utilities yet.

## Decision

- **Phase 1/2 bridge is now real**: we have SSOT scan targeting + artifact production + local historical ingestion.
- **Next phase should be TDD-first stabilization and query/report enablement**, not another scanner rewrite.

## Immediate handoff pointers

- Implementation details and operational sequence: `docs/NEXT_UP.md`.
- Usage and SSOT guidance: `docs/USING_UPDATED_SCANNER.md`.
