# ProjectScanner Repository Audit

Last synchronized: 2026-09-10

## Audit verdict

ProjectScanner now has a bounded, supportable **headless production surface**. The repository should not be described as a fully integrated scanner platform or GUI application; it should be described as repository-intelligence tooling with verified CLI scan/export/planning/hygiene/snapshot-history capabilities.

## Canonical architecture

| Layer | Authority / role |
| --- | --- |
| `src/core/projectscanner/` | canonical scanner engine |
| `src/projectscanner/` | supported package CLI, ingestion/history, planning/hygiene and portfolio evidence surfaces |
| `.github/workflows/scanner-snapshot.yml` | full repository pytest gate plus scanner snapshot proof |
| `.github/workflows/agent-enforcer.yml` | changed-code quality/policy enforcement |
| `MASTER_TASK_LIST.md` | canonical ProjectScanner task inventory |
| `NEXT_UP.md` | bounded immediate queue; empty is a valid terminal state |
| DreamVault | downstream governance/ranking authority |
| Dream.OS/CPC/runtime | authorized mutation/execution authority |

## Production-readiness findings closed

### Snapshot interchange

Closed.

- scanner output uses a versioned analysis contract;
- metadata and analysis schema versions are enforced before ingestion;
- malformed payloads fail closed;
- `analysis.total_files` must agree with the actual file rows;
- CI metadata emits the supported schema version.

### SQLite ingestion

Closed.

- one snapshot row is retained per `(repo, commit_sha)`;
- repeated ingestion refreshes metadata;
- file and issue rows are reconciled as current sets;
- repeated ingestion does not accumulate duplicate issues;
- transaction failure rolls back rather than leaving a partial reconciliation.

### Repeated scanner execution

Closed for the supported public CLI.

- unchanged cached files are hydrated from the prior current report before scanning;
- deleted files are filtered out of the current file set;
- emitted analysis/report/context artifacts use canonical path ordering;
- repeated scans against the same unchanged tree and output directory are regression-tested for stable artifacts;
- `--split-by none` chunk membership is driven from canonical ordering.

### GUI exposure

Closed by narrowing the support boundary.

The production CLI no longer advertises the missing enhanced GUI implementation or a GUI package extra. Legacy GUI source remains available for historical salvage, but it is not a supported product surface.

### Regression gate

Closed.

The Scanner Snapshot workflow runs the repository's stated `pytest -q` regression suite rather than a hand-picked subset. Agent Enforcer remains a separate changed-code policy/quality gate.

### Portfolio evidence v2

Closed as an additive evidence capability.

`dreamos.portfolio-index.v2` normalizes repository task evidence, validates NEXT_UP projection, classifies artifact roles, and preserves DreamVault as governance/planning authority. It does not rank, execute, or mutate tasks.

## Remaining code that is intentionally not production scope

These are deferred capabilities, not active defects in the supported headless product boundary:

- legacy GUI implementation experiments;
- dependency-graph completeness where import evidence is not emitted;
- agent categorization where class-detail evidence is not emitted;
- `PipelineOrchestrator.analyze()` and `.quality()` enrichment stages;
- historical wrappers and scripts that are superseded by package CLI commands;
- speculative revenue/productization documents without a concrete promoted objective.

Their presence does not create an autonomous assignment.

## Documentation authority

Current required sources are aligned around the same boundary:

- `README.md`
- `PRD.md`
- `ROADMAP.md`
- `PRODUCTION_READINESS.md`
- `docs/DOMAIN_MODEL.md`
- `docs/REPOSITORY_AUDIT.md`
- `docs/CURRENT_STATE_ASSESSMENT.md`
- `MASTER_TASK_LIST.md`
- `NEXT_UP.md`

Historical documentation may remain for provenance but cannot override these current sources.

## Verification

Required code-change gate:

```bash
pytest -q
```

Required PR evidence additionally includes Scanner Snapshot and Agent Enforcer on the exact candidate head. Review findings must be resolved or the affected capability must be removed from the supported claim before merge.

## Current planning state

There is no canonical READY/ACTIVE ProjectScanner task after the production-readiness reconciliation represented by the current authority set.

`NEXT_UP.md` is intentionally empty. Future automation must stop at that boundary rather than deriving assignments from old prose, closed PRs, dormant branches, or deferred code.

## Next recommended work

None from existing ProjectScanner planning authority.

A future lane should begin only from a new concrete objective or from explicitly salvaged unique branch work that is reviewed and promoted into canonical planning authority.
