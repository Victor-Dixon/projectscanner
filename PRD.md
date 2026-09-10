# ProjectScanner PRD

Last synchronized: 2026-09-10

## Product summary

ProjectScanner is a **headless repository scanning and inventory-intelligence tool**. It converts repository state into machine-readable evidence for cleanup, consolidation, promotion, and downstream automation decisions.

ProjectScanner is an evidence producer. It does not own DreamVault portfolio governance, planner ranking, or downstream mutation authority.

## Supported users

- Operators or agents scanning local repositories.
- Dream.OS/DreamVault workflows consuming repository evidence.
- Developers maintaining scanner, export, hygiene, snapshot, and history tooling.

## Supported capabilities

| Capability | Surface | Status |
| --- | --- | --- |
| Local source scan | `projectscanner scan` / `src/core/projectscanner/` | Supported |
| Python structure analysis | `LanguageAnalyzer` | Supported/tested |
| Lightweight JS/TS/Rust extraction | `LanguageAnalyzer` | Supported |
| JSON analysis output | `ReportGenerator` / snapshot contract | Supported |
| ChatGPT context export/chunking | `ReportGenerator` | Supported/tested |
| Bare repo metadata | `ReportGenerator` | Supported/tested |
| GitHub/local inventory helpers | `github_sources.py`, `scan_targets.py` | Supported |
| Portfolio intelligence export | `projectscanner export` | Supported/tested |
| Planning contract inspection | `projectscanner planning` | Supported/tested |
| Branch/worktree hygiene evidence | `projectscanner hygiene` | Supported/tested/read-only; requires the `[hygiene]` install extra |
| Snapshot validation | versioned metadata/analysis contract | Supported/tested |
| SQLite snapshot ingestion | `projectscanner ingest` | Supported/tested/idempotent |
| Snapshot history | `projectscanner history` | Supported/tested |
| HQ portfolio evidence v2 | `projectscanner.portfolio_index_v2` | Supported/tested/evidence-only |

## Installation contract

The base editable install supports scan/export/planning/ingest/history:

```bash
pip install -e .
```

The full supported headless surface, including branch/worktree hygiene evidence, requires the pinned AgentTools integration:

```bash
pip install -e '.[hygiene]'
```

Development/full-regression environments use:

```bash
pip install -e '.[dev,hygiene]'
```

## Functional requirements

### FR1 — Scan repositories deterministically

ProjectScanner must scan supported source/documentation files while honoring exclusions, file-size limits, and configured ignore paths.

### FR2 — Emit reviewable evidence

Generated analysis and context artifacts must be deterministic enough for regression testing and must preserve the boundary between observed evidence and downstream decisions. Re-scanning an unchanged current tree into the same output location must not erase cached file evidence, and deleted files must not persist in current artifacts.

### FR3 — Maintain a versioned snapshot contract

CI snapshot metadata and normalized analysis must declare supported schema versions. Ingestion must reject malformed or unsupported payloads before database mutation.

### FR4 — Reconcile repeated ingestion safely

A repeated `(repo, commit_sha)` ingestion must not accumulate duplicate child rows. Snapshot metadata, files, and issues must reconcile to the latest validated artifact as one transaction.

### FR5 — Keep hygiene observational

Branch/worktree hygiene output may classify current Git evidence but must not itself delete branches or mutate repositories. The command requires the `[hygiene]` dependency set; a base install is not claimed to provide this optional AgentTools-backed surface.

### FR6 — Keep portfolio v2 non-authoritative

The v2 index may normalize repository planning evidence and assignable projections, but DreamVault remains planner/governance authority.

### FR7 — Fail closed on planning drift

When recognized `NEXT_UP` task evidence conflicts with canonical repository task evidence, ProjectScanner must emit no assignable candidate replacement of its own.

### FR8 — Verify the whole supported repository

Implementation PRs must pass the full repository `pytest -q` gate plus Agent Enforcer at the exact PR head before merge.

## Explicit non-requirements

The following are preserved or deferred but are **not** part of the supported production product:

- legacy GUI availability;
- complete dependency-graph enrichment;
- agent categorization enrichment;
- `PipelineOrchestrator.analyze()` / `.quality()` enrichment;
- tree-sitter parsing;
- planner ranking or mutation authority.

These surfaces require a new explicit objective before implementation work is justified.

## Production status

The supported headless surface is production-ready as of 2026-09-10 when installed with the dependency set required for the invoked command. See `PRODUCTION_READINESS.md` for the verification boundary and `MASTER_TASK_LIST.md` / `NEXT_UP.md` for executable repository state.
