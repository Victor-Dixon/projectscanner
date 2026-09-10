# ProjectScanner Domain Model

Last synchronized: 2026-09-10

## Purpose

ProjectScanner is the repository-intelligence producer for Dream.OS. It converts repository source, Git state, planning files, and scanner observations into machine-readable evidence for downstream governance and automation.

ProjectScanner does **not** own portfolio ranking, autonomous mutation, branch deletion, deployment authority, or DreamVault governance.

## Supported product boundary

The supported production surface is intentionally headless.

### Public CLI

`projectscanner` supports:

- `scan` — scan a local repository and emit deterministic analysis artifacts;
- `export` — emit repository/portfolio intelligence bundles;
- `planning` — inspect normalized repository planning contracts;
- `hygiene` — inspect branch/worktree evidence without mutation;
- `ingest` — ingest validated scanner snapshots into SQLite history;
- `history` — query recent ingested snapshot history.

The legacy GUI is not part of the supported production command surface.

## Core entities

| Entity | Responsibility |
| --- | --- |
| `ProjectScanner` | Coordinates local file discovery, analysis, caching, report generation, and optional branch/dependency evidence. |
| `FileProcessor` | Applies exclusions, size limits, cache checks, decoding, and file reads. |
| `LanguageAnalyzer` | Produces lightweight Python/JS/TS/Rust structural analysis. |
| `ReportGenerator` | Writes analysis reports, model-context exports, chunks, and bare-repository metadata. |
| snapshot contract | Defines the versioned `metadata.json` + `analysis.json` interchange used by CI and ingestion. |
| SQLite ingestor | Reconciles one snapshot row per `(repo, commit_sha)` and replaces child file/issue state idempotently. |
| planning contract | Normalizes repository-owned task authority without inventing work. |
| fleet hygiene snapshot | Produces branch/worktree observational evidence without deletion authority. |
| portfolio index v2 | Produces normalized portfolio/task evidence for downstream DreamVault/HQ consumers. |

## Artifact contracts

### Scan artifacts

A supported CLI scan emits:

```text
project_analysis_<repo>.json
analysis.json
chatgpt_project_context_<repo>.json   # when requested
runtime/reports/project_context_*.json # when requested
```

The CLI reconciles the current source-file set before serialization. Unchanged cached files retain their prior analysis, deleted files are excluded from current artifacts, and path ordering is canonicalized before report/snapshot/context emission.

### Snapshot contract

The supported snapshot interchange requires schema version `1.0` for metadata and analysis payloads. Validation occurs before SQLite writes. Unsupported schema versions, malformed file arrays, and inconsistent `total_files` values fail closed.

Repeated ingestion for the same `(repo, commit_sha)` is idempotent: snapshot metadata is refreshed and file/issue children are reconciled rather than accumulated.

### Portfolio evidence

ProjectScanner emits evidence/projections, not planner authority:

```text
repository evidence
  -> planning_contract.json
  -> projectscanner intelligence / portfolio index
  -> model/RAG/operator projections
  -> DreamVault governance and ranking
```

`dreamos.portfolio-index.v2` normalizes structured task rows, validates bounded NEXT_UP projection, fails closed on planning drift, and exposes READY/ACTIVE evidence only when the projection is valid.

## Authority boundaries

| Concern | Authority |
| --- | --- |
| Repository source and repo-local planning intent | repository |
| Repository scanning and normalized evidence | ProjectScanner |
| Durable portfolio governance/ranking | DreamVault |
| Authorized mutation/execution | Dream.OS/CPC/runtime executor |
| Model-facing context | projection only; never source of truth |

## Supported versus deferred behavior

### Supported

- local source scanning;
- deterministic current-file analysis emission through the public CLI;
- context export/chunking;
- bare Git metadata export;
- GitHub/local repository inventory helpers;
- portfolio intelligence export;
- branch/worktree observational evidence;
- planning-contract inspection;
- versioned snapshot validation;
- idempotent SQLite snapshot ingestion;
- portfolio index v2 evidence normalization;
- full repository pytest regression gate.

### Deferred / non-production

The following code may remain for historical salvage or future promotion but is not a current product guarantee:

- legacy GUI launch/source experiments;
- complete dependency-graph semantics where analyzer import evidence is unavailable;
- agent categorization where analyzer class-detail evidence is unavailable;
- `PipelineOrchestrator.analyze()` / `.quality()` enrichment stages;
- speculative product/revenue packaging not backed by a concrete objective.

Deferred surfaces are not executable backlog merely because code exists.

## Verification contract

The repository verification gate is:

```bash
pytest -q
```

GitHub pull requests also run Scanner Snapshot and Agent Enforcer. A green curated subset is not sufficient when the full suite is available.

## Planning terminal state

`MASTER_TASK_LIST.md` contains the stable canonical task records. `NEXT_UP.md` is intentionally empty when no READY/ACTIVE ProjectScanner lane remains.

An empty `NEXT_UP.md` is a terminal state, not permission to rediscover historical prose as work. New work requires a concrete objective and explicit promotion into canonical planning authority.
