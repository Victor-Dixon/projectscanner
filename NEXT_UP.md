# projectscanner 

Baseline Dream.OS project artifact.

## Status

Seeded after dirty zero-score cleanup and full regression pass.

## Notes

- Canonical scanner source remains under src/core/projectscanner/.
- Overlay scanner experiment is archived under archive/untracked_overlay_20260505/.
- Current regression gate: pytest -q.

## Current documentation sync focus

1. Keep `docs/CODEBASE_OVERVIEW.md` as the architecture summary for scanner mechanics.
2. Keep root `README.md`, `PRD.md`, `PROJECT_STRUCTURE_TREE.md`, `TASK_LIST.md`, and `AGENTS.md` as the canonical operator documentation set.
3. Do not promote copied repository material from `github_library/`, `github_library_enhanced/`, `temp_repos/`, or archived overlays into canonical docs.
