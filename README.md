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
- `src/utils/run_scanner.py` and `src/projectscanner/ingest.py` - CI scan runner and SQLite ingestor.

Archived overlay scanner experiments remain under:

```text
archive/untracked_overlay_20260505/
```

## Supported boundary and deferred surfaces

The production command surface is intentionally headless. The supported `projectscanner` CLI exposes scanning, export, planning inspection, branch/worktree hygiene inspection, snapshot ingestion, and history. The `hygiene` command requires the optional `[hygiene]` dependency set because it consumes the pinned AgentTools evidence library. Legacy GUI sources remain in the repository for historical salvage but are not advertised or supported by the production CLI.

The versioned snapshot path enforces schema version compatibility before database writes and reconciles repeated `(repo, commit_sha)` ingestion without accumulating stale file or issue rows. Supported CLI scans also reconcile cached unchanged files and deleted files against the current source set before emitting deterministic report, snapshot, and context artifacts.

The following remain explicitly unsupported/incomplete rather than being presented as working features:

- Dependency graph generation expects imports that the current analyzer does not emit.
- Agent categorization expects class detail dictionaries that the current analyzer does not emit.
- `PipelineOrchestrator.analyze()` and `.quality()` still reference incomplete enrichment integrations.

## Installation

For scanning, export, planning, ingestion, and history without branch/worktree hygiene support:

```bash
pip install -e .
```

For the full supported headless CLI, including `projectscanner hygiene`:

```bash
pip install -e '.[hygiene]'
```

The full CI/development verification environment is:

```bash
pip install -e '.[dev,hygiene]'
```

## Common usage

Run a local scan:

```bash
projectscanner scan /path/to/project --output ./scan-output
```

Inspect branch/worktree hygiene after installing the `[hygiene]` extra:

```bash
projectscanner hygiene /path/to/project --json
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

ProjectScanner is an active headless toolbelt repository with a working scanner, context/export path, branch/worktree evidence surface, versioned snapshot contract, idempotent SQLite ingestion, and portfolio evidence index. Unsupported legacy or enrichment surfaces are kept outside the production command contract until independently verified.
