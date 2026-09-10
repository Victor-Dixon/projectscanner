# ProjectScanner Production Readiness

Last synchronized: 2026-09-10

## Verdict

`SUPPORTED_HEADLESS_SURFACE=PRODUCTION_READY`

This verdict is intentionally scoped. ProjectScanner is production-ready for its supported headless repository-intelligence surface when the dependency set required by the invoked command is installed; preserved legacy GUI and speculative enrichment modules are not included in that support claim.

## Supported production surface

- Local project scanning through `ProjectScanner` and `projectscanner scan`.
- Lightweight Python, JS/TS, and Rust structure analysis.
- Deterministic current-file JSON report and ChatGPT-context export/chunking, including repeated-scan cache reconciliation.
- Bare Git repository metadata export.
- GitHub inventory and scan-target helpers.
- Planning-contract inspection.
- Read-only branch/worktree hygiene evidence when installed with `[hygiene]`.
- Versioned `analysis.json` / `metadata.json` snapshot contract.
- Fail-closed snapshot validation before SQLite writes.
- Idempotent SQLite ingestion keyed by `(repo, commit_sha)` with exact child-row reconciliation.
- Snapshot history queries.
- Portfolio evidence index v1 and additive HQ-ready v2 evidence projection.

## Installation boundary

Base supported commands:

```bash
pip install -e .
```

Full supported headless surface including `projectscanner hygiene`:

```bash
pip install -e '.[hygiene]'
```

Full development/CI dependency set:

```bash
pip install -e '.[dev,hygiene]'
```

The AgentTools dependency remains an explicit optional integration rather than being silently required for scan/export/planning/ingest/history users.

## Production verification gate

Scanner Snapshot CI runs the repository's full gate:

```bash
pytest -q
```

Agent Enforcer is the second exact-head merge gate. Review findings are also closure criteria: a capability cannot be certified merely because CI is green when an unresolved review finding contradicts the production claim.

## Closed readiness requirements

- [x] Snapshot schema is versioned, emitted by CI, and validated before ingestion.
- [x] CI scanner output and SQLite ingestion share the same contract.
- [x] Malformed payload, duplicate-ingest, and row-fidelity behavior have regression coverage.
- [x] Repeated same-output scans retain unchanged cached file evidence, discard deleted-file residue, and emit deterministic path/chunk ordering.
- [x] GUI status is resolved: ProjectScanner production is intentionally headless; legacy GUI source is preserved but unsupported.
- [x] Dependency graph and agent categorization are removed from the supported-feature claim and remain deferred backlog only.
- [x] The supported repository surface is covered by the full regression suite rather than a curated CI subset.
- [x] Portfolio evidence v2 is additive and explicitly non-authoritative for planning/execution.
- [x] Hygiene installation requirements are explicit; the command is supported with the `[hygiene]` extra.

## Explicitly unsupported / deferred

These are not production guarantees and do not block the supported headless release:

- legacy GUI source under `src/gui/`;
- `PipelineOrchestrator.analyze()` / `.quality()` enrichment;
- dependency-graph completeness;
- agent categorization completeness;
- tree-sitter parsing.

They must not be advertised as supported without a new requirement and focused verification.

## Operational rule

`MASTER_TASK_LIST.md` and `NEXT_UP.md` define executable repository work. `MASTER_TASK_LOG.md` records verified closure history. As of this synchronization, there is no `READY` or `ACTIVE` ProjectScanner task. Workers must not manufacture follow-up implementation merely because dormant legacy code exists.
