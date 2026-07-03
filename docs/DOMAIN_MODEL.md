# ProjectScanner Domain Model

Last synchronized: 2026-07-03

## What this project is

ProjectScanner is Python tooling for repository intelligence and inventory. It scans local source trees and selected GitHub repositories, extracts lightweight structure from files, writes JSON reports and ChatGPT-oriented context exports, and provides supporting quality, target-manifest, and snapshot-ingestion utilities.

## Why it exists

The repository exists to turn repository contents into machine-readable evidence before cleanup, consolidation, promotion, or follow-up automation decisions are made. In the Dream.OS ecosystem documented in this repository, ProjectScanner is a generator: it emits scan and inventory artifacts for other systems, especially DreamVault, to consume.

## Domain

Core domain: software repository scanning and repository inventory intelligence.

Adjacent domains represented in code:

- Code quality rule evaluation.
- GitHub repository discovery and cloning.
- CI snapshot artifact generation.
- SQLite history ingestion for scanner snapshots.
- GUI launch surfaces, currently incomplete.

## Unknowns

The following cannot be determined as working behavior from the repository alone:

- A functioning enhanced GUI implementation. Several launchers import `src.gui.main.enhanced_gui` or `core.projectscanner.gui`, but those modules are not present.
- A complete scanner-to-ingestor snapshot schema. The CI runner writes scanner output, while `ingest_snapshot.py` expects an `analysis.json` schema with top-level `files`, `issues`, and `total_files` fields.
- A fully wired dependency graph. `ProjectScanner` builds a reverse import graph from `imports`, but `LanguageAnalyzer` does not currently emit `imports`.
- A fully wired agent categorization pass on real analyzer output. Categorization expects class detail dictionaries, while current analyzer output lists class names.
- Product ownership beyond the documented Dream.OS/DreamVault boundary. The repository documents ProjectScanner as a generator and DreamVault as the durable governance/reporting layer; any broader ownership is Unknown.

## Subdomains

| Subdomain | Implementation | Responsibility | Status |
| --- | --- | --- | --- |
| Core scanning | `src/core/projectscanner/` | Walk supported files, analyze file structure, cache work, write reports and context exports | Implemented and test-covered in core paths |
| Language analysis | `src/core/projectscanner/language_analyzer.py` | Extract Python functions/classes/routes/complexity with `ast`; extract JS/TS and Rust functions/classes with regex | Implemented, lightweight |
| Report generation | `src/core/projectscanner/report_generator.py` | Merge report JSON, export ChatGPT context, split context chunks, emit bare repo metadata, generate `__init__.py` files | Implemented and partly test-covered |
| Snapshot model | `src/core/model/project_snapshot.py`, `src/core/pipeline/orchestrator.py` | Represent scan snapshots and orchestrate scan/analyze/quality stages | Partially implemented; integration gaps documented |
| Quality/contracts | `src/core/rules/`, `src/quality/` | Run rule objects and standalone quality checkers for headers, comments, naming, function length, complexity, LOC, and AGENTS.md presence | Implemented as tools; limited pytest coverage |
| GitHub inventory | `github_sources.py`, `scan_targets.py`, `src/scanners/github_library_scanner.py` | Discover GitHub repositories, build scan target manifests, clone and scan GitHub repositories | Implemented; summary behavior tested |
| Portfolio export | `scripts/export_project_intelligence.py` | Export repo inventory, docs markers, cleanup recommendations, and ChatGPT context from filesystem/git metadata | Implemented and test-covered |
| CI snapshots | `.github/workflows/scanner-snapshot.yml`, `src/utils/run_scanner.py`, `ingest_snapshot.py` | Run scans in CI, upload artifacts, ingest snapshots into SQLite | Workflow and ingestor exist; schema alignment remains incomplete |
| GUI | `main.py`, `src/gui/` | Launch GUI-oriented workflows | Incomplete from current tree |

## Major entities

| Entity | Type | Defined in | Meaning |
| --- | --- | --- | --- |
| `ProjectScanner` | Service/orchestrator | `src/core/projectscanner/scanner.py` | Main scan coordinator for project roots and bare Git repositories |
| `LanguageAnalyzer` | Service | `src/core/projectscanner/language_analyzer.py` | Produces per-file language, function, class, route, complexity, and lint fields |
| `FileProcessor` | Service | `src/core/projectscanner/file_processor.py` | Applies exclusions, size limits, cache checks, decoding, and file reads |
| `ReportGenerator` | Service | `src/core/projectscanner/report_generator.py` | Writes analysis reports, context exports, context chunks, bare repo metadata, and init files |
| `ProjectSnapshot` | Data model | `src/core/model/project_snapshot.py` | Dataclass for unified scan results, metrics, quality, reports, insights, and future embeddings |
| `PipelineOrchestrator` | Service | `src/core/pipeline/orchestrator.py` | Wraps `ProjectScanner` into `ProjectSnapshot` and attempts analysis/quality enrichment |
| `BaseRule` and rule subclasses | Services/strategies | `src/core/rules/` | Pluggable rules that emit standardized violations |
| `ContractEngine` | Service | `src/core/rules/contract_engine.py` | Runs rules against files/directories and computes compliance scores |
| `ScanTarget` | Data model | `scan_targets.py` | Frozen dataclass describing local or GitHub repositories to scan |
| `GitHubLibraryScanner` | Service | `src/scanners/github_library_scanner.py` | Fetches GitHub repos, clones them, scans them, and exports a library summary |
| `ArtifactStandardResult` | Data model | `project_artifact_standards.py` | Reports whether expected per-target artifact files exist |

## Value objects

| Value object | Shape | Source |
| --- | --- | --- |
| Per-file analysis | `language`, `functions`, `classes`, `routes`, `complexity`, `lint` | `LanguageAnalyzer.analyze_file()` |
| Route | `function`, `path`, `method` | `LanguageAnalyzer._extract_routes()` |
| Cache entry | `mtime`, `size`, optional `hash` | `FileProcessor.process_file()` |
| Contract violation | `rule_id`, `rule_name`, `severity`, `line`, `message`, `fix_suggestion` | `BaseRule.violation()` and `ContractEngine` |
| GitHub inventory repository | `name`, `name_with_owner`, `url`, `is_private`, `updated_at`, `default_branch` | `github_sources.normalize_repos()` |
| Artifact standard result | `project`, `source_type`, `expected_dir`, `missing_files`, `present_files`, `complete` | `project_artifact_standards.py` |

## Relationships

- `ProjectScanner` owns the scan lifecycle and composes `FileProcessor`, `LanguageAnalyzer`, and `ReportGenerator`.
- `FileProcessor` calls `LanguageAnalyzer` only after exclusion, file-size, cache, and decoding checks pass.
- `ReportGenerator` consumes `ProjectScanner.analysis` and writes JSON artifacts.
- `PipelineOrchestrator` wraps `ProjectScanner.scan_project()` results in a `ProjectSnapshot`.
- `ContractEngine` composes rule subclasses and produces quality reports independent of the primary scanner pipeline.
- `GitHubLibraryScanner` obtains remote repository metadata, clones repositories, and delegates per-repository analysis to `ProjectScanner`.
- `scan_targets.py`, `github_sources.py`, and `project_artifact_standards.py` model scan target discovery and artifact completeness outside the core scanner package.
- `scripts/export_project_intelligence.py` performs a separate filesystem/git/docs-marker inventory flow and does not call `ProjectScanner`.
- `ingest_snapshot.py` expects a normalized snapshot artifact directory and writes history to SQLite.

## Data flow

### Local project scan

1. User or workflow calls `ProjectScanner` directly, `main.py --scan`, `src/core/projectscanner/cli.py`, or `src/utils/run_scanner.py`.
2. `ProjectScanner` resolves output paths and cache.
3. `iter_scan_files()` walks supported extensions and applies `FileProcessor.should_exclude()`.
4. `process_files_parallel()` runs file processing with worker threads.
5. `LanguageAnalyzer` emits per-file analysis.
6. `ProjectScanner` merges results into `analysis` and optionally inserts `__dependency_graph__`.
7. `ReportGenerator.save_report()` writes `project_analysis_<name>.json`.
8. Optional context export writes `chatgpt_project_context_<name>.json` and chunks under `runtime/reports/`.
9. Cache writes to `.projectscanner_cache.json`.

### Bare Git repository scan

1. `ProjectScanner` detects a bare repository with `git rev-parse --is-bare-repository`.
2. It skips working-tree file analysis.
3. `ReportGenerator.export_bare_repo_metadata()` writes `bare_repo_metadata.json` with commit count, last commit, branches, and a bare-repo note.

### GitHub library scan

1. `GitHubLibraryScanner` fetches public repository metadata with the GitHub REST API.
2. It clones each repository into a temporary local directory.
3. It delegates analysis and context export to `ProjectScanner`.
4. It writes repository analysis/context into `github_library_enhanced.json`, `scan_log.json`, and per-repository report directories.

### GitHub target manifest flow

1. `github_sources.py` uses the GitHub CLI to list repositories.
2. Repositories are normalized into inventory JSON/Markdown under `runtime/targets/`.
3. `scan_targets.py` converts them into `ScanTarget` manifests and clone/fetch plans.

### Portfolio intelligence export

1. `scripts/export_project_intelligence.py` scans repositories under a projects root.
2. It records git state, file/directory counts, and presence of required documentation markers.
3. It writes `repo_analysis.json`, `chatgpt_context.json`, `cleanup_recommendations.json`, and `docs_gap_report.md` for each repo.

### Snapshot history ingestion

1. `ingest_snapshot.py` expects a snapshot directory with `metadata.json` and `analysis.json`.
2. It inserts snapshot metadata, file rows, and issue rows into `scanner_history.db`.
3. Current scanner output does not yet match this ingest schema without a normalization step.

## User interactions

| Interaction | Entry point | Current behavior |
| --- | --- | --- |
| Scan a project | `python main.py --scan /path/to/project` | Runs `ProjectScanner` and optionally exports context/generates `__init__.py` |
| Quick scan | `python main.py --quick-scan /path/to/project` | Runs `ProjectScanner.scan_project()` with defaults |
| Package CLI scan | `python -m core.projectscanner.cli` or file invocation | Supports project root, ignores, agent categorization, context toggle, init generation, and output dir |
| CI scan runner | `python src/utils/run_scanner.py --target ./src --output <dir>` | Resolves target from repo root and runs `ProjectScanner` |
| Export portfolio intelligence | `python scripts/export_project_intelligence.py --projects-root ... --out-root ...` | Writes docs/cleanup/context bundles from filesystem/git metadata |
| GitHub inventory refresh | `github_sources.refresh_github_sources()` | Uses `gh repo list` to write inventory and scan target manifests |
| GitHub library scan | `python src/scanners/github_library_scanner.py <username> [output_dir]` | Uses GitHub REST API, clones repos, and scans each one |
| Quality contract check | `python src/quality/contract_cli.py <path>` | Runs `ContractEngine` and reports compliance |
| Snapshot ingest | `python ingest_snapshot.py <snapshot_dir> --repo <name>` | Loads metadata/analysis JSON into SQLite |
| GUI launch | `python main.py --gui` | Intended, but current implementation imports missing GUI modules |

## External integrations

| Integration | Evidence in repository | Purpose |
| --- | --- | --- |
| Git | `scanner.py`, `scan_targets.py`, `github_sources.py`, `ingest_snapshot.py`, workflows | Bare repo metadata, repo root discovery, clone/fetch plans, metadata |
| GitHub REST API | `src/scanners/github_library_scanner.py` | Public repository listing |
| GitHub CLI | `github_sources.py` | Authenticated repository inventory |
| GitHub Actions | `.github/workflows/` | Scanner snapshot and agent-enforcer workflows |
| Jinja2 | `report_generator.py` | Optional templated context export |
| PyQt5 | `src/gui/`, GUI tests | Intended GUI dependency; working GUI status Unknown |
| SQLite | `ingest_snapshot.py` | Snapshot history database |
| Ruff/Radon | `.github/workflows/agent-enforcer.yml` | CI quality enforcement |

## Feature-to-domain mapping

| Feature | Domain/subdomain | Implementation | Status |
| --- | --- | --- | --- |
| Local repository file scan | Core scanning | `ProjectScanner`, `FileProcessor`, `LanguageAnalyzer` | Implemented |
| Python function/class/route extraction | Language analysis | `LanguageAnalyzer._analyze_python()` | Implemented and tested |
| JS/TS/Rust structural extraction | Language analysis | Regex analyzers in `LanguageAnalyzer` | Implemented, lightweight |
| Exclusion of virtualenvs, `.git`, runtime, reports | Core scanning | `FileProcessor.should_exclude()` | Implemented |
| Incremental cache | Core scanning | `.projectscanner_cache.json` with `mtime`/`size` | Implemented |
| JSON report generation | Report generation | `ReportGenerator.save_report()` | Implemented |
| ChatGPT context export and chunking | Report generation | `ReportGenerator.export_chatgpt_context()` | Implemented and tested |
| Bare Git repository metadata | Report generation/Git integration | `ProjectScanner.is_bare`, `export_bare_repo_metadata()` | Implemented and tested |
| `__init__.py` generation | Report generation | `ReportGenerator.generate_init_files()` | Implemented and tested |
| Dependency graph | Core scanning | `ProjectScanner._build_global_dependency_graph()` | Partially implemented; analyzer does not emit imports |
| Agent categorization | Scanner intelligence | `ProjectScanner.categorize_agents()` and scan utils | Partially implemented; analyzer output mismatch |
| Unified snapshot object | Snapshot model | `ProjectSnapshot`, `PipelineOrchestrator.scan()` | Partially implemented |
| Snapshot analyze/quality enrichment | Snapshot model/quality | `PipelineOrchestrator.analyze()` and `.quality()` | Incomplete imports/functions |
| Contract rule evaluation | Quality/contracts | `ContractEngine` and rules | Implemented, limited tests |
| LOC/complexity/AGENTS checks | Quality/contracts | `src/quality/` | Implemented as tools |
| GitHub library scanning | GitHub inventory | `GitHubLibraryScanner` | Implemented; summary tested |
| GitHub source inventory | GitHub inventory | `github_sources.py`, `scan_targets.py` | Implemented |
| Artifact standard checks | Artifact governance | `project_artifact_standards.py` | Implemented |
| Portfolio docs-gap export | Portfolio export | `scripts/export_project_intelligence.py` | Implemented and tested |
| CI snapshot workflow | CI snapshots | `.github/workflows/scanner-snapshot.yml`, `run_scanner.py` | Implemented; schema gap remains |
| SQLite snapshot history | CI snapshots | `ingest_snapshot.py` | Implemented; needs validation and schema alignment |
| Enhanced GUI | GUI | `main.py`, `src/gui/` | Unknown/incomplete |

## Current completed work

- Canonical scanner source consolidated under `src/core/projectscanner/`.
- Regression gate is `pytest -q`.
- Core analyzer tests cover Python extraction, route extraction, exclusions, context export, and init generation.
- Phase 2 tests cover context chunking, bare repo metadata, and single-source scanner imports.
- Portfolio intelligence export has tests for expected output bundles.
- GitHub library summary arithmetic is tested.
- Scanner snapshot workflow presence and timestamp safety are tested.

## Remaining work

- Align scanner output, CI artifacts, and `ingest_snapshot.py` schema.
- Add validation tests for snapshot metadata and analysis payloads.
- Decide whether GUI is active, then either implement missing modules or mark GUI entry points as unsupported.
- Either enrich analyzer output with imports/class details or mark dependency graph and agent categorization as future/unsupported in code-level docs.
- Add tests for `ProjectSnapshot`, `PipelineOrchestrator`, `ContractEngine`, quality checkers, scan targets, artifact standards, and GitHub source inventory where behavior is intended to remain stable.

## Next recommended work

See `NEXT_UP.md` for the active handoff. The current next slice is snapshot contract stabilization: define and validate the artifact schema connecting CI scanner output to SQLite ingestion.
