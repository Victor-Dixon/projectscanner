# projectscanner 

Baseline Dream.OS project artifact.

## Status

Seeded after dirty zero-score cleanup and full regression pass.

## Notes

- Canonical scanner source remains under src/core/projectscanner/.
- Overlay scanner experiment is archived under archive/untracked_overlay_20260505/.
- Current regression gate: pytest -q.


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

