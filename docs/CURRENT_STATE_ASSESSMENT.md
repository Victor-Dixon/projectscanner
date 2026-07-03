# Current State Assessment

Last synchronized: 2026-07-03

## What this project is

ProjectScanner is repository scanning and inventory intelligence tooling. It scans local and selected GitHub repositories, exports code structure/context artifacts, and supports Dream.OS/DreamVault cleanup and consolidation workflows with evidence.

## Domain

Core domain: software repository scanning and repository inventory intelligence.

See `docs/DOMAIN_MODEL.md` for the full domain model.

## What we have right now

### 1) Canonical scanner package

- Source of truth: `src/core/projectscanner/`.
- `ProjectScanner` composes `FileProcessor`, `LanguageAnalyzer`, and `ReportGenerator`.
- Supported scan outputs include JSON analysis reports and optional ChatGPT context exports.
- Current regression coverage verifies analyzer behavior, exclusions, context export, chunking, bare repo metadata, and SSOT imports.

### 2) Repository inventory and portfolio utilities

- `github_sources.py` and `scan_targets.py` model GitHub/local scan target discovery and manifests.
- `src/scanners/github_library_scanner.py` can fetch public GitHub repo metadata, clone repositories, and delegate analysis to `ProjectScanner`.
- `scripts/export_project_intelligence.py` exports filesystem/git/docs-marker intelligence bundles and is covered by tests.
- `project_artifact_standards.py` checks for expected artifact bundle files.

### 3) Quality and contract tooling

- `src/core/rules/` contains the contract engine and rule strategies.
- `src/quality/` contains standalone AGENTS.md, complexity, LOC, and contract CLI tooling.
- These tools exist, but much of this surface has limited pytest coverage.

### 4) CI and snapshot history

- `.github/workflows/scanner-snapshot.yml` and `src/utils/run_scanner.py` provide a CI-oriented scan path.
- `ingest_snapshot.py` ingests `metadata.json` and `analysis.json` into SQLite.
- Current gap: the scanner runner and ingestor do not yet share a fully aligned, documented artifact schema.

### 5) GUI status

- GUI-related entry points exist.
- Referenced enhanced GUI modules are missing from the current tree.
- GUI behavior is Unknown/incomplete and should not be documented as a working feature until code and tests support it.

## Current risks and gaps

1. Snapshot data contract drift between scanner output and SQLite ingestion.
2. Missing validation for snapshot metadata and analysis payloads.
3. GUI entry points reference missing modules.
4. Dependency graph and agent categorization expect analyzer fields that are not currently emitted.
5. Pipeline analyze/quality methods reference missing functions.
6. Several stable utility modules need tests before stronger guarantees are made.

## What has been completed

- Documentation-first domain model and repository audit.
- Required lifecycle doc synchronization.
- Explicit Unknowns for incomplete features.
- Current authoritative documentation map.

## What remains

- Snapshot schema stabilization.
- Additional tests for ingestion and stable utilities.
- GUI support decision.
- Analyzer enrichment/support decision for graph and categorization features.

## What should be worked on next

Follow root `NEXT_UP.md`: stabilize the snapshot artifact contract between CI scanner output and `ingest_snapshot.py`.
