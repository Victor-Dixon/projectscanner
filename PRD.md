# projectscanner 

Baseline Dream.OS project artifact.

## Status

Seeded after dirty zero-score cleanup and full regression pass.

## Notes

- Canonical scanner source remains under src/core/projectscanner/.
- Overlay scanner experiment is archived under archive/untracked_overlay_20260505/.
- Current regression gate: pytest -q.

## Documentation and architecture status

- Canonical architecture summary: `docs/CODEBASE_OVERVIEW.md`.
- Canonical source tree summary: `PROJECT_STRUCTURE_TREE.md`.
- Canonical operator entry point: `README.md`.
- Generated or copied repository material under `github_library/`, `github_library_enhanced/`, `temp_repos/`, and archived overlays is not canonical product documentation.

ProjectScanner owns scanning mechanics and report generation only. DreamVault remains the source of truth for portfolio governance and durable intelligence.
