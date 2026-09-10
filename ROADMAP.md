# ProjectScanner Roadmap

Last synchronized: 2026-09-10

## Mission

ProjectScanner is headless repository-intelligence tooling. Its supported job is to produce tested, machine-readable evidence; it is not a planner, governance system, mutation executor, or GUI product.

## Completed production baseline

### Scanner and reporting

- Canonical scanner source under `src/core/projectscanner/`.
- Local scanning with file exclusion, size, and cache handling.
- Python structure analysis plus lightweight JS/TS/Rust extraction.
- JSON reports and ChatGPT-context export/chunking.
- Bare Git metadata and init-file generation.
- GitHub/local inventory and scan-target helpers.

### Snapshot and history contract

- Versioned `metadata.json` and `analysis.json` contract.
- Schema-version enforcement before database writes.
- CI metadata version emission.
- Malformed-input regression coverage.
- Idempotent `(repo, commit_sha)` ingestion.
- Exact file/issue row reconciliation and transactional rollback.

### Repository intelligence

- Planning-contract inspection.
- Read-only branch/worktree hygiene evidence.
- Portfolio intelligence v1 export.
- Additive `dreamos.portfolio-index.v2` with normalized task inventory, fail-closed projection checks, typed artifact roles, and explicit DreamVault authority boundary.

### Production discipline

- Supported product boundary is intentionally headless.
- Broken GUI command/extra removed from the production CLI/package surface while legacy source remains available for salvage.
- Full `pytest -q` is now the Scanner Snapshot CI regression gate.
- Agent Enforcer remains the second exact-head gate.
- Stale snapshot, planner, productization, revenue, and portfolio PRs were either reconstructed on current master or closed without blind merge.

## Deferred — not executable by default

These are possible future product decisions, not current readiness blockers:

- legacy GUI restoration;
- PipelineOrchestrator analysis/quality enrichment;
- dependency-graph enrichment;
- agent categorization enrichment;
- tree-sitter parsing;
- additional commercial packaging.

A deferred item must not become active merely because code or historical documentation exists. It requires a concrete user/operator objective and promotion to `READY` or `ACTIVE` in `MASTER_TASK_LIST.md`.

## Next work

There is currently **no executable ProjectScanner lane**. `NEXT_UP.md` is intentionally empty after the 2026-09-10 production-readiness closure.

Future work should begin with a new bounded objective rather than another repository-wide cleanup pass.
