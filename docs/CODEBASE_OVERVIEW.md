# ProjectScanner Codebase Overview

Last synchronized: 2026-07-03

## What this project is

ProjectScanner is repository scanning and inventory intelligence tooling. It belongs to the software repository analysis domain and exists to generate evidence about local and GitHub repositories for cleanup, consolidation, promotion, and automation workflows.

For the complete domain model, see `docs/DOMAIN_MODEL.md`.

## Current architecture

### Core scanner

`src/core/projectscanner/` is the canonical scanner package.

- `scanner.py` - `ProjectScanner`, the main scan orchestrator.
- `file_processor.py` - exclusions, size checks, cache validation, file reads, and decode handling.
- `language_analyzer.py` - lightweight structure extraction for Python, JS/TS, Rust, and fallback file types.
- `report_generator.py` - report JSON, ChatGPT context exports, context chunks, bare repo metadata, and `__init__.py` generation.
- `scan_utils.py` - file walking, parallel processing, and agent categorization helpers.
- `cli.py` - scanner-specific CLI.
- `bots.py` - queue worker classes retained in the package; the current main scan path uses thread pool helpers in `scan_utils.py`.

### Snapshot model and pipeline

- `src/core/model/project_snapshot.py` defines `ProjectSnapshot`.
- `src/core/pipeline/orchestrator.py` wraps `ProjectScanner` output into a snapshot.

Known gap: `PipelineOrchestrator.analyze()` and `.quality()` reference functions that are not present as implemented module-level APIs.

### Rules and quality

- `src/core/rules/` contains `BaseRule`, rule implementations, and `ContractEngine`.
- `src/quality/` contains standalone quality checker CLIs for AGENTS.md presence, complexity, LOC, and contract execution.

### GitHub and scan targets

- `github_sources.py` uses the GitHub CLI to generate repository inventories and scan target manifests.
- `scan_targets.py` defines `ScanTarget`, local/GitHub target creation, clone/fetch plans, and artifact paths.
- `src/scanners/github_library_scanner.py` uses the GitHub REST API, clones repositories, delegates to `ProjectScanner`, and writes a library summary.

### Portfolio export

- `scripts/export_project_intelligence.py` scans repositories using filesystem, git, and documentation marker signals. It writes `repo_analysis.json`, `chatgpt_context.json`, `cleanup_recommendations.json`, and `docs_gap_report.md`.

### CI and history

- `src/utils/run_scanner.py` is the CI-oriented scanner runner.
- `.github/workflows/scanner-snapshot.yml` runs the scanner and uploads snapshot artifacts.
- `ingest_snapshot.py` ingests `metadata.json` and `analysis.json` into SQLite.

Known gap: the ingestor expects a normalized `analysis.json` schema that the scanner runner does not currently emit directly.

### GUI

`main.py` and files under `src/gui/` include GUI launch surfaces, but referenced modules such as `src.gui.main.enhanced_gui` and `core.projectscanner.gui` are missing. GUI behavior is therefore Unknown/incomplete from the current repository.

### Archive

`archive/untracked_overlay_20260505/` contains an archived scanner overlay experiment. It is not the active scanner source.

## Primary data flow

```text
CLI / workflow / Python caller
  -> ProjectScanner
  -> iter_scan_files + FileProcessor exclusions/cache
  -> LanguageAnalyzer
  -> ProjectScanner.analysis
  -> ReportGenerator
  -> project_analysis_<name>.json
  -> optional chatgpt_project_context_<name>.json and runtime/reports chunks
```

## Verification

Run:

```bash
pytest -q
```

## Current completed work

- Core scanner/report/context behavior is implemented.
- Portfolio export, GitHub inventory helpers, scan targets, and quality tooling exist.
- Required lifecycle docs are synchronized with the implementation.

## What remains

- Snapshot schema stabilization.
- GUI status resolution.
- Tests for untested utility surfaces.
- Analyzer/graph/categorization contract decisions.

## What should be worked on next

Follow `NEXT_UP.md`: stabilize the CI scanner artifact and SQLite ingestion contract.

