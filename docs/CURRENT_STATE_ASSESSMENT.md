# Current State Assessment

Last synchronized: 2026-09-10

## Current verdict

ProjectScanner has a **production-ready bounded headless surface** for repository scanning and intelligence workflows.

That statement is intentionally scoped. It does not certify the legacy GUI, incomplete pipeline enrichment stages, or every historical utility as production-ready.

## Supported now

### Scanner CLI

The public `projectscanner` command supports:

- `scan`
- `export`
- `planning`
- `hygiene`
- `ingest`
- `history`

The GUI command is not part of the supported surface.

### Scan artifacts

Supported CLI scans emit current repository evidence rather than stale cache residue:

- unchanged cached files retain their analysis;
- deleted files are excluded from current artifacts;
- report/snapshot/context paths are emitted in canonical order;
- repeated unchanged scans against the same output directory are regression-tested for stable artifacts;
- optional context chunk membership is deterministic for the same current analysis set.

### Snapshot and history contract

- metadata schema version is enforced;
- analysis schema version is enforced;
- malformed or inconsistent payloads fail before database writes;
- repeated `(repo, commit_sha)` ingestion is idempotent;
- file and issue child rows are reconciled to current snapshot state;
- transaction failures roll back.

### Repository/fleet intelligence

- planning contracts are inspected without inventing tasks;
- branch/worktree hygiene evidence is observational only;
- portfolio intelligence export remains evidence generation;
- `dreamos.portfolio-index.v2` adds normalized task evidence and fail-closed NEXT_UP projection while preserving DreamVault as planner/governance authority.

## Verification state

The repository regression contract is:

```bash
pytest -q
```

Pull-request verification also requires:

```text
Scanner Snapshot = PASS
Agent Enforcer   = PASS
review findings  = resolved or affected claim removed
```

The full suite replaced the earlier curated-subset gate so dormant regressions are visible rather than silently excluded.

## Explicitly deferred / unsupported

The following remain outside the current production guarantee:

- legacy GUI implementation and launch experiments;
- complete dependency-graph semantics where analyzer import evidence is absent;
- agent categorization where analyzer class-detail evidence is absent;
- `PipelineOrchestrator.analyze()` and `.quality()` enrichment stages;
- speculative commercialization/revenue lanes without concrete validation.

These items are not READY work merely because code or historical documentation exists.

## Planning state

The canonical production-readiness lanes have been completed or reconciled. `NEXT_UP.md` intentionally contains no READY/ACTIVE ProjectScanner task.

This means:

```text
NO CANONICAL ASSIGNMENT
        -> STOP
```

A worker must not recreate completed snapshot work from older documents, closed PRs, or dormant branches.

## What should be worked on next

Nothing from existing ProjectScanner planning authority.

A next lane requires one of:

1. a new concrete objective explicitly promoted into canonical planning authority; or
2. unique branch work that is inspected, salvaged, verified against current master, and then explicitly promoted.
