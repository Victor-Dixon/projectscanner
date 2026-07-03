# ProjectScanner Consolidation Manifest

Last synchronized: 2026-07-03

## Classification

`canonical_project_inventory_scanner`

## Purpose

ProjectScanner is the canonical local/GitHub project scanning, scan target, artifact-standard, and repository inventory tooling repo in this workspace.

## Domain

Software repository scanning and repository inventory intelligence.

## Current source of truth

- Canonical scanner source: `src/core/projectscanner/`
- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Quality checks: `src/quality/`
- Contract rules: `src/core/rules/`
- GitHub/local scan target tooling: `github_sources.py`, `scan_targets.py`, `src/scanners/`
- Portfolio export: `scripts/export_project_intelligence.py`
- Snapshot ingestion: `ingest_snapshot.py`
- Runtime scan outputs, when generated: `runtime/targets/`, `runtime/reports/`, `runtime/project_artifacts/`
- Archived overlay experiment: `archive/untracked_overlay_20260505/`

## Canonical boundaries

- ProjectScanner owns scanning, inventory, context export, target manifests, and scanner artifact mechanics.
- DreamVault owns durable portfolio governance, long-lived reports, and decision records.
- AgentTools owns operator/control-plane tooling that may call scanner outputs.
- Dream.OS owns runtime/swarm execution and should not absorb scanner UI or report generation logic.

Unknown:

- Any additional ownership or product boundary not documented in this repository.

## Promotion policy

- Reusable scanner output should flow into DreamVault as inventory artifacts.
- Reusable operator commands should promote to AgentTools only through manifests.
- Runtime/generated scan outputs should not be treated as durable source unless explicitly promoted.

## Cleanup policy

Do not delete runtime/project artifacts, scan targets, or archive material until a report classifies them as one of:

- preserve
- promote_to_dreamvault
- generated_runtime_noise
- archive_after_review

## Completed

- Canonical scanner package exists.
- Repository domain model and audit are documented.
- Required lifecycle docs are synchronized.

## Remaining

- Stabilize snapshot artifact schema.
- Resolve incomplete GUI/schema/dependency graph/agent categorization seams.

## Next work

Follow `NEXT_UP.md`.

## Verification

Primary gate:

```bash
pytest -q
```
