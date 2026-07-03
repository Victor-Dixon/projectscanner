# ProjectScanner Next Up

Last synchronized: 2026-07-03

## What this project is

ProjectScanner is repository scanning and inventory intelligence tooling. It scans local and selected GitHub repositories, exports code-structure/context artifacts, and supports Dream.OS/DreamVault cleanup and consolidation workflows with evidence.

## Why it exists

It exists to replace repository cleanup guesswork with machine-readable scan, documentation, target, quality, and artifact signals.

## Domain

Core domain: software repository scanning and repository inventory intelligence.

See `docs/DOMAIN_MODEL.md` for the full domain model.

## Current status

Completed:

- Core scanner source is under `src/core/projectscanner/`.
- JSON report and ChatGPT context export paths exist.
- Bare Git repository metadata export exists.
- Portfolio docs-gap export exists.
- GitHub inventory/scan target utilities exist.
- Quality/rules tooling exists.
- CI scanner wrapper and SQLite ingestor exist.
- Required documentation has been synchronized with the implementation.

Known incomplete/Unknown:

- GUI launch paths reference missing modules.
- Scanner output and `ingest_snapshot.py` do not yet share a stable `analysis.json` schema.
- Dependency graph and agent categorization expect analyzer fields that current analyzer output does not provide.
- Pipeline analyze/quality enrichment references missing functions.

## Work next

Stabilize the snapshot artifact contract between CI scanner output and SQLite ingestion.

### Required outcomes

1. Define the snapshot directory contract:
   - required files,
   - required metadata fields,
   - required analysis fields,
   - versioning behavior if needed.
2. Add tests for `ingest_snapshot.py`:
   - missing `metadata.json`,
   - missing `analysis.json`,
   - missing required metadata fields,
   - malformed analysis payload,
   - duplicate snapshot ingest,
   - file and issue row fidelity.
3. Align `src/utils/run_scanner.py` output with the ingest contract, or add a documented normalization step before ingestion.
4. Update docs if the snapshot contract changes.
5. Run `pytest -q`.

## Suggested first tests

- `test_ingest_requires_metadata_file`
- `test_ingest_requires_analysis_file`
- `test_ingest_rejects_metadata_without_commit_sha`
- `test_ingest_rejects_analysis_without_files_list`
- `test_ingest_is_idempotent_for_same_repo_and_commit`
- `test_ingest_preserves_file_and_issue_counts`

## Guardrails

- Do not create a parallel scanner engine.
- Keep scanner changes under `src/core/projectscanner/` unless the work is specifically about wrappers or ingestion.
- Preserve the current local scan behavior unless tests prove a contract needs to change.
- Mark uncertain behavior as Unknown in docs.
- Regression gate: `pytest -q`.

## References

- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Requirements: `PRD.md`
- Roadmap: `ROADMAP.md`
- Master task list: `MASTER_TASK_LIST.md`
