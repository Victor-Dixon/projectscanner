# ProjectScanner Roadmap

Last synchronized: 2026-07-03

## What this project is

ProjectScanner is repository scanning and inventory intelligence tooling for local and GitHub projects. It belongs to the software repository analysis domain and produces machine-readable evidence for cleanup, consolidation, promotion, and automation workflows.

## Why it exists

The project exists so operators and agents can reason from scan artifacts instead of assumptions when reviewing repositories.

## Completed

### Core scanner baseline

- Canonical scanner source established under `src/core/projectscanner/`.
- Local project scanning implemented through `ProjectScanner`.
- File exclusion, size limit, and cache handling implemented in `FileProcessor`.
- Python analysis implemented with `ast`.
- Lightweight JS/TS and Rust extraction implemented with regex.
- JSON report generation implemented.
- ChatGPT context export and context chunking implemented.
- Bare Git repository metadata export implemented.
- `__init__.py` generation implemented.

### Inventory and portfolio support

- GitHub repository library scan flow implemented in `src/scanners/github_library_scanner.py`.
- GitHub CLI inventory and scan target manifest helpers implemented in `github_sources.py` and `scan_targets.py`.
- Artifact standard checks implemented in `project_artifact_standards.py`.
- Filesystem/git/docs-marker portfolio export implemented in `scripts/export_project_intelligence.py`.

### Quality and automation support

- Contract rule engine and rule subclasses implemented under `src/core/rules/`.
- Standalone quality checkers implemented under `src/quality/`.
- CI scanner wrapper implemented in `src/utils/run_scanner.py`.
- SQLite snapshot ingestor implemented in `ingest_snapshot.py`.
- GitHub Actions workflows exist for scanner snapshots and agent enforcement.

### Documentation synchronization

- Domain model documented in `docs/DOMAIN_MODEL.md`.
- Repository audit documented in `docs/REPOSITORY_AUDIT.md`.
- Required lifecycle docs updated: `PRD.md`, `ROADMAP.md`, `MASTER_TASK_LIST.md`, `MASTER_TASK_LOG.md`, `NEXT_UP.md`, and `AGENTS.md`.

## Current state

The working core is the local scanner/report/context path. The repository also contains inventory, quality, and snapshot-history utilities, but some integration seams are incomplete.

Known incomplete areas:

- Snapshot artifact schema mismatch between scanner output and `ingest_snapshot.py`.
- GUI launch paths reference missing modules.
- Dependency graph and agent categorization expect analyzer fields that are not currently emitted.
- `PipelineOrchestrator.analyze()` and `.quality()` reference missing module-level functions.

## Roadmap

### Phase 1: Snapshot contract stabilization

- Define the expected snapshot directory schema.
- Add validation for `metadata.json`.
- Add validation for `analysis.json`.
- Align CI scanner output with the ingest schema or add a documented normalization step.
- Add tests for missing files, malformed payloads, duplicate snapshots, and file/issue row fidelity.

### Phase 2: Coverage for stable utility surfaces

- Add tests for `ProjectSnapshot` and `PipelineOrchestrator.scan()`.
- Add tests for `ContractEngine` default rule loading and scoring.
- Add tests for `scan_targets.py` and `project_artifact_standards.py`.
- Add tests for `github_sources.py` with command calls mocked.

### Phase 3: Resolve incomplete feature seams

- Decide whether dependency graph and agent categorization should become supported scanner outputs.
- If supported, enrich analyzer output and tests accordingly.
- If not supported, remove or clearly mark unsupported code paths.
- Decide GUI support status; either restore missing GUI modules or document GUI as unsupported.

### Phase 4: Contributor and operations polish

- Add a dedicated contributor guide if maintainers need one.
- Add examples for quality and contract CLI usage after tests stabilize expected output.
- Keep root lifecycle docs synchronized with domain and audit docs.

## What remains

The highest-risk remaining work is not a new scanner engine. It is stabilizing contracts between existing components, especially CI scan artifacts and SQLite ingestion.

## What should be worked on next

Follow `NEXT_UP.md`: snapshot contract stabilization with tests first.
