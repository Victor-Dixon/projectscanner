# ProjectScanner

ProjectScanner is a Python repository scanning and inventory intelligence tool. It scans local project folders and selected GitHub repositories, extracts lightweight file structure, exports JSON reports and ChatGPT-oriented context, and records repository documentation/cleanup signals for downstream planning.

Suggested GitHub repository description:

> Repository intelligence tooling for scanning local and GitHub projects, exporting code structure/context, and supporting Dream.OS/DreamVault cleanup and consolidation workflows.

## Why this exists

ProjectScanner exists to produce evidence before repository cleanup, consolidation, promotion, or follow-up automation. In the documented Dream.OS boundary, ProjectScanner is a generator: it emits scan and inventory artifacts, while DreamVault owns durable portfolio governance and decision records.

## Domain

Core domain: software repository scanning and repository inventory intelligence.

Subdomains:

- Local source tree scanning.
- Language-level structure extraction.
- Report and ChatGPT context generation.
- GitHub repository inventory and scan target generation.
- Portfolio docs-gap and cleanup signal export.
- Quality/rules checks.
- CI snapshot artifact generation and SQLite history ingestion.

See the complete domain model in [`docs/DOMAIN_MODEL.md`](docs/DOMAIN_MODEL.md).

## What it solves

ProjectScanner helps answer evidence-backed questions such as:

- What files, languages, functions, classes, routes, and complexity signals exist in a repository?
- What reports and LLM context can be generated from a source tree?
- Which repositories have required documentation markers?
- Which local or GitHub repositories are ready to be scanned?
- Which scan artifacts are present or missing?
- Which follow-up work is needed before scanner outputs can support trend analysis?

## Current implementation

Canonical scanner source:

```text
src/core/projectscanner/
```

Important supporting modules:

- `src/core/model/project_snapshot.py` - snapshot dataclass.
- `src/core/pipeline/orchestrator.py` - partial scan/analyze/quality orchestration.
- `src/core/rules/` and `src/quality/` - contract and quality checks.
- `scan_targets.py` and `github_sources.py` - scan target and GitHub inventory helpers.
- `src/scanners/github_library_scanner.py` - GitHub REST/clone/scan flow.
- `scripts/export_project_intelligence.py` - filesystem/git/docs-marker export.
- `src/utils/run_scanner.py` and `ingest_snapshot.py` - CI scan runner and SQLite ingestor.

Archived overlay scanner experiments remain under:

```text
archive/untracked_overlay_20260505/
```

## Known Unknowns and incomplete areas

These are intentionally not described as working features:

- Enhanced GUI launch paths reference missing modules.
- Scanner output and `ingest_snapshot.py` do not yet share a complete documented `analysis.json` schema.
- Dependency graph generation expects imports that the current analyzer does not emit.
- Agent categorization expects class detail dictionaries that the current analyzer does not emit.
- `PipelineOrchestrator.analyze()` and `.quality()` reference functions that are not currently present.

## Common usage

Install the package in editable mode:

```bash
pip install -e .
```

Run a local scan:

```bash
python main.py --scan /path/to/project --export-context
```

Run the CI-oriented scanner wrapper:

```bash
python src/utils/run_scanner.py --target ./src --output ./snapshots/manual
```

Export portfolio intelligence from a projects directory:

```bash
python scripts/export_project_intelligence.py \
  --projects-root "$HOME/projects" \
  --out-root "$HOME/projects/DreamVault/data/intelligence/repos_from_projectscanner"
```

Expected portfolio export files per repository:

```text
repo_analysis.json
chatgpt_context.json
cleanup_recommendations.json
docs_gap_report.md
```

## Verification

Current regression gate:

```bash
pytest -q
```

## Documentation map

- [`docs/DOMAIN_MODEL.md`](docs/DOMAIN_MODEL.md) - core domain, subdomains, entities, relationships, data flow, integrations, and feature mapping.
- [`docs/REPOSITORY_AUDIT.md`](docs/REPOSITORY_AUDIT.md) - architecture, folder structure, documentation audit, stale docs, naming issues, and gaps.
- [`PRD.md`](PRD.md) - requirements derived from current implementation.
- [`ROADMAP.md`](ROADMAP.md) - completed, current, and remaining work.
- [`MASTER_TASK_LIST.md`](MASTER_TASK_LIST.md) - canonical task inventory.
- [`MASTER_TASK_LOG.md`](MASTER_TASK_LOG.md) - chronological task log.
- [`NEXT_UP.md`](NEXT_UP.md) - active handoff for the next work slice.
- [`AGENTS.md`](AGENTS.md) - repository-specific agent operating rules.

## Current status

ProjectScanner is an active toolbelt repository with a working core scanner and context export path. `NEXT_UP.md` now limits the immediate handoff to five verification and policy actions; the complete strategic inventory remains in `MASTER_TASK_LIST.md`.
