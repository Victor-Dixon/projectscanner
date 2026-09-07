# ProjectScanner Master Task List

Last synchronized: 2026-08-11

## Purpose

This file is the canonical backlog and strategic inventory: it answers **what work exists?** Completed history belongs in `MASTER_TASK_LOG.md`; no more than five immediate actions belong in `NEXT_UP.md`.

ProjectScanner produces repository-scanning and inventory evidence for cleanup, consolidation, promotion, and automation decisions. The scanner source of truth is `src/core/projectscanner/`; archived or removed implementations are not alternate engines.

## Canonical references

- Active handoff: `NEXT_UP.md`
- Completed history: `MASTER_TASK_LOG.md`
- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Requirements and roadmap: `PRD.md` and `ROADMAP.md`
- Operating rules: `AGENTS.md`

## Strategic inventory by domain

### Canonical scanner core

- [ ] Verify the current `src/core/projectscanner/` path against the regression suite and document which scanner behaviors have direct test coverage.
- [ ] Keep all scanner behavior changes in the canonical package; do not revive the standalone, enhanced, or archived overlay scanners as parallel engines.
- [ ] Decide whether dependency-graph output is supported; if retained, emit and test the required import data.
- [ ] Decide whether agent categorization is supported; if retained, emit and test the required class-detail data.
- [ ] Add focused coverage for `ProjectSnapshot` and stable scanner utilities where current behavior lacks regression tests.

### CLI, reporting, and export

- [ ] Verify public CLI flags, JSON report generation, context export, and chunking against tests and current documentation.
- [ ] Document supported report and context schemas, including compatibility expectations for downstream consumers.
- [ ] Add test-backed examples for the quality and contract CLIs before promoting them in user documentation.
- [ ] Verify GitHub inventory, bare-repository metadata, scan-target, and project-intelligence exports with external commands mocked where appropriate.

### RAG and knowledge activation

- [ ] Confirm the normalized RAG corpus export contract against current Dream Suite retrieval needs.
- [ ] Verify repository provenance, source digest, exported-content digest, normalization, and JSONL determinism end to end.
- [ ] Define which knowledge artifacts are durable inputs, reproducible outputs, or transient runtime data.
- [ ] Document ownership and handoff boundaries between ProjectScanner generation and downstream indexing or retrieval systems.

### Generated analysis asset policy

- [ ] Inventory committed and ignored analysis outputs and classify each family as source, promoted evidence, reproducible artifact, or cleanup candidate.
- [ ] Preserve generated/runtime scan outputs only when an explicit promotion rule identifies an owner, purpose, and refresh policy.
- [ ] Keep large historical generated datasets out of product-history claims unless their behavior is independently verified.
- [ ] Document retention, naming, and ignore rules for snapshots, reports, contexts, caches, and portfolio exports.

### Pipeline and CI verification

- [ ] Define and version the snapshot directory contract between `src/utils/run_scanner.py` and `ingest_snapshot.py`.
- [ ] Validate required `metadata.json` and `analysis.json` fields before database writes.
- [ ] Test missing or malformed files, duplicate ingestion, and file/issue row fidelity.
- [ ] Resolve or explicitly defer the missing `PipelineOrchestrator.analyze()` and `.quality()` integrations.
- [ ] Preserve incremental Ruff enforcement while establishing a deliberate plan for legacy lint debt.
- [ ] Decide and document the remote/upstream policy for the local `work` branch.
- [ ] `projectscanner_ci_cost_001`: Review and promote evidence-only CI runner/cost intelligence after broad regression, representative real-repo evidence, and authority checks. Focused implementation has 20 focused local tests passing; production acceptance remains unclaimed. Next governed lane: `ci_cost_fleet_reconciliation_001`.

### Removed legacy GUI and history

- [ ] Reconcile documentation and launch references that still imply the removed enhanced GUI is available.
- [ ] Decide whether ProjectScanner is intentionally headless or whether a new GUI is justified by current requirements.
- [ ] If a GUI is approved, design it against the canonical scanner API rather than restoring a parallel historical implementation.
- [ ] Keep legacy GUI, token wizard, portfolio-analysis, enhanced-scanner claims labeled historical or **Needs verification**.

### Documentation and planning standardization

- [ ] Keep `MASTER_TASK_LIST.md` as backlog, `MASTER_TASK_LOG.md` as completed history, and `NEXT_UP.md` as the immediate handoff.
- [ ] Review the seven **Needs verification** history lanes and record corrections append-only in the master task log.
- [ ] Keep `README.md`, `PRD.md`, `ROADMAP.md`, domain/audit docs, and agent instructions synchronized when contracts or support decisions change.
- [ ] Keep historical planning documents clearly labeled non-authoritative and pointing to the root canonical planning set.

### Dream.OS and Dream Suite integration

- [ ] Confirm current Dream.OS/Dream Suite consumers, required artifact formats, and transfer locations.
- [ ] Preserve the boundary that ProjectScanner generates repository evidence while durable portfolio governance is owned downstream.
- [ ] Define compatibility checks for Dream Suite ingestion before describing an integration as active.
- [ ] Reconcile legacy DreamVault terminology with the current Dream Suite architecture and ownership model.
