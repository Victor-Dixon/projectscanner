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

## Quick start

```bash
pip install -e ".[dev]"
projectscanner scan ./src --output /tmp/ps-out
test -f /tmp/ps-out/analysis.json
pytest -q
```

### Commands

```bash
# Scan a repo (writes project_analysis_*.json + analysis.json contract)
projectscanner scan /path/to/repo --output /tmp/scan-out

# Export portfolio intelligence for DreamVault
projectscanner export \
  --projects-root "$HOME/projects" \
  --out-root "$HOME/projects/DreamVault/data/intelligence/repos_from_projectscanner"

# Ingest a CI snapshot into local history
projectscanner ingest ./snapshots/some-run --repo projectscanner

# View recent ingested snapshots
projectscanner history --last 10

# Optional GUI (requires PyQt5)
pip install -e ".[gui]"
projectscanner gui
```

`main.py` remains as a deprecated shim for one release cycle.

## Export Project Intelligence

```bash
projectscanner export \
  --projects-root "$HOME/projects" \
  --out-root "$HOME/projects/DreamVault/data/intelligence/repos_from_projectscanner"
```

Legacy script (deprecated):

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

<!-- DREAMVAULT_PORTFOLIO_README:BEGIN schema=v1 generated="2026-06-29T02:03:43Z" -->
## Portfolio status

**Portfolio scanner and authority graph** — Toolbelt scanner for repo discovery, authority graphs, duplicate detection, and portfolio/consolidation intelligence.

| Field | Value |
|---|---|
| **Canonical ID** | `projectscanner` |
| **Bucket** | toolbelt |
| **Action** | keep_as_toolbelt |
| **GitHub** | [projectscanner](https://github.com/Victor-Dixon/projectscanner) |

### Repository inventory

*Filesystem scan at `2026-06-29T02:03:43Z` — regenerate via `python runtime/scripts/sync_portfolio_readmes_001.py`.*

| Signal | Value |
|---|---|
| Python files | 80 |
| Test files | 8 |
| CI workflows | 2 |
| runtime/tasks YAML | 0 |
| pyproject.toml | yes |
| package.json | no |
| tests/ directory | yes |
| Git branch | master |
| Working tree | dirty |

**Top-level directories:** .github, archive, config, docs, projectscanner, scripts, src, tests

**Top-level files:** .gitignore, AGENTS.md, CONSOLIDATION_MANIFEST.md, LICENSE, MASTER_TASK_LIST.md, MASTER_TASK_LOG.md, NEXT_UP.md, PRD.md, PRODUCTION_READINESS.md, PROJECT_STRUCTURE_TREE.md, README.md, ROADMAP.md, TASK_LIST.md, __init__.py, build_project_artifacts.py, final_comment_fix.py, fix_bad_names.sh, github_sources.py, ingest_snapshot.py, launch_gui.bat, launch_gui.sh, main.py, mark_long_functions.py, project_artifact_standards.py

### Consolidation signals

- No consolidation flags from inventory.

### Run / verify

- `pip install -e .` then `pytest -q` (if tests present).
<!-- DREAMVAULT_PORTFOLIO_README:END schema=v1 generated="2026-06-29T02:03:43Z" -->
