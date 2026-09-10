# ProjectScanner Master Task List

Last synchronized: 2026-09-10

## Authority

This file is the canonical repository task inventory. `NEXT_UP.md` is the bounded executable projection. `MASTER_TASK_LOG.md` remains historical evidence.

ProjectScanner is a **headless repository-intelligence producer**. It scans and normalizes evidence; DreamVault owns portfolio governance/ranking and downstream authorized mutation remains outside ProjectScanner.

## Canonical task inventory

- PSC-HYGIENE-001 | P0 | COMPLETE | Branch/worktree evidence sensor foundation landed in PR #22.
- PSC-SNAPSHOT-001 | P0 | COMPLETE | Versioned scanner-to-ingestor snapshot contract enforced in PR #26.
- PSC-INGEST-001 | P0 | COMPLETE | Snapshot ingestion made idempotent with row-fidelity regression coverage in PR #27.
- PSC-SURFACE-001 | P0 | COMPLETE | Supported headless CLI boundary established and full `pytest -q` promoted to CI in PR #31.
- PSC-PORTFOLIO-001 | P0 | COMPLETE | HQ-ready portfolio evidence index v2 salvaged onto current master in PR #32.
- PSC-PIPELINE-001 | P2 | BACKLOG | Legacy `PipelineOrchestrator` enrichment remains outside the supported production surface; promote only with a concrete consumer requirement.
- PSC-GUI-001 | P2 | BACKLOG | Legacy GUI source is preserved for salvage but is not a supported production feature.
- PSC-GRAPH-001 | P2 | BACKLOG | Dependency-graph enrichment is unsupported until analyzer import evidence and tests justify it.
- PSC-AGENTCAT-001 | P2 | BACKLOG | Agent categorization is unsupported until analyzer class-detail evidence and tests justify it.

## Execution policy

- `COMPLETE` rows are terminal historical/current-state records and must not be re-assigned.
- `BACKLOG` rows are non-executable until explicitly promoted to `READY` or `ACTIVE` by a concrete requirement.
- Do not recreate GUI, pipeline, graph, or categorization work merely to make dormant code look complete.
- Any future implementation change must pass the full `pytest -q` Scanner Snapshot gate and Agent Enforcer at the exact PR head.

## Current terminal state

There are no canonical `READY` or `ACTIVE` ProjectScanner tasks after the 2026-09-10 production-readiness reconciliation. Future work begins from a new explicit objective, not from stale prose inventory.
