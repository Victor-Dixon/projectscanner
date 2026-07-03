# ProjectScanner Master Task List

Last synchronized: 2026-07-03

## Project

ProjectScanner is repository scanning and inventory intelligence tooling in the software repository analysis domain. It exists to generate evidence about local and GitHub repositories before cleanup, consolidation, promotion, or automation decisions.

## Canonical references

- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- PRD: `PRD.md`
- Roadmap: `ROADMAP.md`
- Active handoff: `NEXT_UP.md`
- Agent instructions: `AGENTS.md`

## Completed

- [x] Preserve canonical scanner source under `src/core/projectscanner/`.
- [x] Document archived overlay experiment under `archive/untracked_overlay_20260505/`.
- [x] Verify regression gate is `pytest -q`.
- [x] Implement local scanner, file processor, language analyzer, and report generator.
- [x] Implement JSON reports and ChatGPT context export/chunking.
- [x] Implement bare Git repository metadata export.
- [x] Implement filesystem/git/docs-marker portfolio export.
- [x] Implement GitHub inventory, scan target, and GitHub library scanner utilities.
- [x] Implement contract rules and quality checker tools.
- [x] Implement CI scanner runner and SQLite snapshot ingestor.
- [x] Audit repository documentation against implementation.
- [x] Create complete domain model.
- [x] Synchronize required lifecycle docs.
- [x] Mark incomplete/Unknown feature areas explicitly.

## In progress

- [ ] Stabilize snapshot artifact contract between CI scanner output and `ingest_snapshot.py`.

## Open tasks

### Snapshot contract

- [ ] Define the expected snapshot directory contents.
- [ ] Define required `metadata.json` fields.
- [ ] Define required `analysis.json` fields.
- [ ] Add metadata validation before database writes.
- [ ] Add analysis payload validation before database writes.
- [ ] Align `src/utils/run_scanner.py` output with the ingest schema or add a documented normalization step.
- [ ] Add tests for missing metadata and analysis files.
- [ ] Add tests for malformed metadata.
- [ ] Add tests for malformed analysis payloads.
- [ ] Add tests for duplicate snapshot ingest behavior.
- [ ] Add tests for file and issue row fidelity.

### Coverage for stable utilities

- [ ] Add tests for `ProjectSnapshot`.
- [ ] Add tests for `PipelineOrchestrator.scan()`.
- [ ] Add tests for `ContractEngine` default rules and scoring.
- [ ] Add tests for `scan_targets.py`.
- [ ] Add tests for `project_artifact_standards.py`.
- [ ] Add tests for `github_sources.py` with command execution mocked.

### Incomplete feature decisions

- [ ] Decide whether enhanced GUI is supported.
- [ ] If GUI is supported, restore or implement missing GUI modules.
- [ ] If GUI is not supported, update entry points and docs accordingly.
- [ ] Decide whether dependency graph output is supported.
- [ ] Decide whether agent categorization on real scan output is supported.
- [ ] Resolve `PipelineOrchestrator.analyze()` missing `run_analysis` integration.
- [ ] Resolve `PipelineOrchestrator.quality()` missing quality function integrations.

### Documentation maintenance

- [ ] Keep historical docs clearly labeled as non-authoritative.
- [ ] Add quality/contract CLI examples after expected output is test-covered.
- [ ] Add contributor guide if repository workflow needs expand beyond current `AGENTS.md`.

## What should be worked on next

Run the `NEXT_UP.md` handoff: stabilize the snapshot artifact contract and add validation tests before changing downstream behavior.
