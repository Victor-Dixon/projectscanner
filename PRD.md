# ProjectScanner PRD

Last synchronized: 2026-07-03

## Product summary

ProjectScanner is repository scanning and inventory intelligence tooling. It scans local source trees and selected GitHub repositories, extracts lightweight code structure, writes JSON reports and ChatGPT-oriented context exports, and surfaces repository documentation/cleanup signals for downstream planning.

## Why it exists

ProjectScanner exists to provide evidence before repository cleanup, consolidation, promotion, or automation decisions. It reduces guesswork by turning repository contents and documentation markers into machine-readable artifacts.

## Domain

Core domain: software repository scanning and repository inventory intelligence.

Subdomains:

- Local project scanning.
- Language-level structure extraction.
- Report and LLM context generation.
- GitHub inventory and scan target generation.
- Portfolio documentation-gap export.
- Quality/rules checks.
- CI snapshot and SQLite history ingestion.

The full domain model is maintained in `docs/DOMAIN_MODEL.md`.

## Users

Evidence from repository documentation identifies these users:

- Operators or agents that need to scan local repositories.
- Dream.OS/DreamVault workflows that consume generated repository intelligence.
- Developers maintaining scanner, quality, target, and snapshot tooling.

Unknown:

- Any public end-user persona beyond repository operators/agents and maintainers.

## Problems solved

- Generate file-level analysis for supported source and documentation files.
- Export scanner results as JSON reports.
- Export ChatGPT-compatible context files and optional context chunks.
- Identify documentation marker gaps across repositories.
- Build GitHub/local scan target manifests.
- Check expected project artifact completeness.
- Provide quality/rules checks for repository source.
- Capture bare Git repository metadata when no working tree is available.

## Current product capabilities

| Capability | Implementation | Status |
| --- | --- | --- |
| Local source tree scan | `src/core/projectscanner/` | Implemented |
| Python functions/classes/routes/complexity | `LanguageAnalyzer` with `ast` | Implemented and tested |
| JS/TS/Rust lightweight extraction | `LanguageAnalyzer` regex analyzers | Implemented |
| File exclusions and cache | `FileProcessor` | Implemented |
| JSON analysis reports | `ReportGenerator.save_report()` | Implemented |
| ChatGPT context export/chunking | `ReportGenerator.export_chatgpt_context()` | Implemented and tested |
| Bare repo metadata export | `ReportGenerator.export_bare_repo_metadata()` | Implemented and tested |
| `__init__.py` generation | `ReportGenerator.generate_init_files()` | Implemented and tested |
| GitHub repository library scan | `GitHubLibraryScanner` | Implemented; summary tested |
| GitHub inventory/scan targets | `github_sources.py`, `scan_targets.py` | Implemented |
| Portfolio docs-gap export | `scripts/export_project_intelligence.py` | Implemented and tested |
| Quality contract rules | `src/core/rules/`, `src/quality/` | Implemented; limited tests |
| CI scanner wrapper | `src/utils/run_scanner.py` | Implemented |
| SQLite snapshot ingestion | `ingest_snapshot.py` | Implemented, schema alignment incomplete |

## Explicit Unknowns and non-requirements

The following are not currently product guarantees:

- Enhanced GUI availability. Current GUI entry points reference missing modules.
- A stable scanner-to-ingestor `analysis.json` contract. The ingestor expects a normalized schema that the scanner runner does not currently emit.
- Dependency graph completeness. The graph builder expects imports, but the analyzer does not emit imports.
- Agent categorization completeness. Categorization expects class details not emitted by the analyzer.
- Fully integrated `PipelineOrchestrator.analyze()` and `.quality()` stages.
- Tree-sitter parsing. Current analyzer uses Python `ast` and regex for JS/TS/Rust.

## Functional requirements

### FR1: Scan supported files in a local project

ProjectScanner must recursively scan supported file extensions while excluding virtual environments, `.git`, runtime outputs, scanner artifacts, and configured ignore directories.

### FR2: Produce deterministic lightweight analysis

The scanner must emit per-file analysis with at least:

- `language`
- `functions`
- `classes`
- `routes`
- `complexity`
- `lint`

### FR3: Generate reports and context

The scanner must write JSON analysis reports and optionally ChatGPT context exports. Context chunking must support current implemented modes: `directory`, `language`, and `none`.

### FR4: Handle bare Git repositories

When a bare Git repository is scanned, ProjectScanner must skip working-tree file analysis and emit bare repository metadata.

### FR5: Support repository inventory workflows

The project must support scan target manifests, GitHub inventory, artifact completeness checks, and portfolio docs-gap exports using the existing modules.

### FR6: Preserve Dream.OS/DreamVault boundaries

ProjectScanner emits evidence and reports. DreamVault remains the documented durable governance and decision-record system.

### FR7: Keep documentation synchronized

Required lifecycle docs must describe the current implementation, completed work, remaining work, and next work without inventing features.

## Non-functional requirements

- Verification gate: `pytest -q`.
- Canonical scanner source: `src/core/projectscanner/`.
- Avoid introducing parallel scanner engines.
- Keep generated/runtime scan outputs out of durable source unless explicitly promoted.
- Mark uncertain behavior as Unknown in documentation.

## Current completed work

- Core scanner, analyzer, file processor, report generator, and context export exist.
- Tests cover core analyzer behavior, exclusions, context export, context chunking, bare repo metadata, SSOT imports, portfolio export bundles, GitHub library summary, and workflow text checks.
- Required documentation has been synchronized around the current domain model and repository audit.

## Remaining work

- Define and test a stable snapshot artifact schema.
- Align CI scanner output with `ingest_snapshot.py`.
- Add validation for `metadata.json` and `analysis.json` before SQLite writes.
- Decide GUI support status and update code/docs accordingly.
- Add tests for currently untested stable utility surfaces.
- Resolve analyzer output gaps if dependency graph and agent categorization are intended to be supported features.

## Next work

See `NEXT_UP.md`. The active next slice is snapshot contract stabilization between CI scanner artifacts and SQLite ingestion.
