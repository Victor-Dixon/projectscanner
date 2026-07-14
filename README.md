# projectscanner 

Baseline Dream.OS project artifact.

## Status

Seeded after dirty zero-score cleanup and full regression pass.

## Notes

- Canonical scanner source remains under `src/core/projectscanner/`.
- **One scanner:** portfolio repos must not host a duplicate core; DreamVault and control-plane repos invoke this repo via subprocess.
- **Run intelligence packet:** `python scripts/intelligence/emit_intelligence.py <repo_root> --packet-only`
- **Run full scan:** `python src/utils/run_scanner.py --target <repo_root>`
- Overlay experiment is archived under `archive/untracked_overlay_20260505/` (historical only).
- Regression gate: `pytest -q`
- File cache: `.projectscanner_cache.json` (legacy `dependency_cache.json` at repo root is auto-quarantined).

## Canonical documentation

This repository treats the root documentation files as the operator entry points and `docs/CODEBASE_OVERVIEW.md` as the current architecture summary. Do not use generated snapshots under `github_library/`, `temp_repos/`, or archived overlays as canonical project documentation.

| Need | Canonical document |
|---|---|
| Product purpose | `PRD.md` |
| Architecture / code ownership | `docs/CODEBASE_OVERVIEW.md` |
| Source tree summary | `PROJECT_STRUCTURE_TREE.md` |
| Current work | `NEXT_UP.md` |
| Task inventory | `TASK_LIST.md` |
| Agent guidance | `AGENTS.md` |

## Architecture boundary

ProjectScanner owns scanning mechanics and intelligence export. DreamVault consumes the emitted reports as portfolio intelligence, and AgentTools may call ProjectScanner as a toolbelt dependency. The scanner should not become the canonical store for governance decisions, promotion manifests, or repository documentation repairs.


## Project Intelligence Export

python scripts/export_project_intelligence.py \
  --projects-root "$HOME/projects" \
  --out-root "$HOME/projects/DreamVault/data/intelligence/repos_from_projectscanner"

Outputs:

- repo_analysis.json
- chatgpt_context.json
- cleanup_recommendations.json
- docs_gap_report.md

Agents should consult these before cleanup, consolidation, or docs refresh.
