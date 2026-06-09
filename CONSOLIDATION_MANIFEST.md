# projectscanner Consolidation Manifest

## Classification
canonical_project_inventory_scanner

## Purpose
projectscanner is the canonical local/GitHub project discovery, scan target, artifact-standard, and repo inventory tooling repo.

## Current Source of Truth
- Canonical scanner source: `src/core/projectscanner/`
- **Primary CLI (intelligence packet):** `python scripts/intelligence/emit_intelligence.py <repo> [--packet-only]`
- **Primary CLI (full scan):** `python src/utils/run_scanner.py --target <repo>`
- Quality checks: `src/quality/`
- GitHub/local scan target tooling: `github_sources.py`, `scan_targets.py`, `src/scanners/`
- Runtime scan outputs: `runtime/targets/`, `runtime/reports/`, `runtime/tasks/`
- Archived overlay experiment: `archive/untracked_overlay_20260505/` (not a second scanner; do not import)

## One Scanner Policy
- **SSOT repo:** `D:\projectscanner` only. No duplicate `ProjectScanner` core in DreamVault, github-architect-bot, or other portfolio repos.
- **DreamVault:** governance wrappers only (`dreamsync_projectscanner_gate.py`, `run_projectscanner_ssot_scan_001.py`, report scripts). They subprocess-invoke `D:\projectscanner\scripts\intelligence\emit_intelligence.py` (override via `PROJECTSCANNER_EMIT` / `PROJECTSCANNER_REPO`).
- **github-architect-bot:** orchestration only; calls scanner via `PROJECTSCANNER_CMD` / `PROJECTSCANNER_REPO`.
- **Legacy entry points:** `run.py`, `main.py` remain thin compatibility shims; prefer the primary CLIs above.
- **Cache:** canonical on-disk cache is `.projectscanner_cache.json` at scan output root. Legacy `dependency_cache.json` / `config/dependency_cache.json` are quarantined without parsing; safe to delete empty/stale root copies.

## Canonical Boundaries
- projectscanner owns scanning and inventory mechanics.
- DreamVault owns portfolio governance, long-lived reports, and decision records.
- AgentTools owns operator/control-plane tooling that may call scanner outputs.
- DreamOS owns runtime/swarm execution and should not absorb scanner UI or report generation logic.

## Promotion Policy
Reusable scanner output should flow into DreamVault as inventory artifacts.
Reusable operator commands should promote to AgentTools only through manifests.
Runtime/generated scan outputs should not be treated as durable source unless explicitly promoted.

## Cleanup Policy
Do not delete runtime/project_artifacts, runtime/targets, or archive material until a report classifies them as:
- preserve
- promote_to_dreamvault
- generated_runtime_noise
- archive_after_review

## Verification
Primary gate: `pytest -q`
