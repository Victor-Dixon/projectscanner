# ProjectScanner

ProjectScanner is a repo intelligence and cleanup tool for Dream.OS.

It scans local project folders, classifies repositories, exports structured intelligence, and generates cleanup recommendations before destructive repo changes happen.

## What This Proves

- Repo discovery and classification
- Cleanup planning before deletion
- Machine-readable project intelligence exports
- DreamVault integration
- Regression-gated automation workflows

## Core Use Case

Use ProjectScanner when a workspace has too many repos, duplicate variants, stale experiments, or unclear promotion candidates.

The scanner helps answer:

- Which repos are active?
- Which repos are stale?
- Which repos are variants of the same system?
- Which repos should be archived, promoted, or reviewed?
- What documentation or verification is missing?

## Export Project Intelligence

```bash
python scripts/export_project_intelligence.py \
  --projects-root "$HOME/projects" \
  --out-root "$HOME/projects/DreamVault/data/intelligence/repos_from_projectscanner"
```

Expected outputs:

```text
repo_analysis.json
chatgpt_context.json
cleanup_recommendations.json
docs_gap_report.md
```

## Verification

Run the regression gate:

```bash
pytest -q
```

## Dream.OS Role

ProjectScanner is a generator.

It writes repo intelligence into DreamVault, where other tools and agents can consume the results for planning, cleanup, promotion, and status reporting.

## Current Status

Baseline scanner source remains under:

```text
src/core/projectscanner/
```

Archived overlay experiments remain under:

```text
archive/untracked_overlay_20260505/
```

The current regression gate is:

```bash
pytest -q
```