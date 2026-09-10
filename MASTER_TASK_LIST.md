# ProjectScanner Master Task List

Last synchronized: 2026-09-09

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

## Assignment-ready execution lanes

Task shape:

`- [ ] TASK_ID | PRIORITY | STATUS | Title`

Statuses: `READY`, `ACTIVE`, `BLOCKED`, `COMPLETE`.

- [ ] PSC-HYGIENE-001 | P0 | ACTIVE | Land the existing fleet branch/worktree sensor lane from PR #22 as the canonical observational foundation for branch retirement evidence; do not create a duplicate branch inventory implementation.
- [ ] PSC-INTEL-001 | P0 | ACTIVE | Land the existing portfolio evidence/artifact-role lane from PR #23 so ProjectScanner normalizes repo planning evidence and defines artifact authority without becoming planner authority.
- [ ] PSC-RETIRE-001 | P0 | BLOCKED | Add deterministic branch retirement classification consuming canonical sensor facts and emitting `FAST_PATH`, `FORENSIC_PATH`, `KEEP`, or `UNKNOWN`; blocked on accepted PSC-HYGIENE-001 and PSC-INTEL-001 foundations.
- [ ] PSC-CONTEXT-001 | P0 | BLOCKED | Extend existing repo analysis, intelligence packet, ChatGPT context, and RAG projection with branch-retirement summaries without creating another standalone branch-cleanup JSON family; blocked on PSC-RETIRE-001.
- [ ] PSC-FLEET-001 | P1 | BLOCKED | Run ProjectScanner across the governed repo fleet to produce planning-drift and branch-retirement evidence for downstream DreamVault reconciliation; blocked on PSC-CONTEXT-001.

### Artifact authority hierarchy

Use existing artifacts as layers rather than peers:

1. `project_analysis_<repo>.json` / `chatgpt_project_context_<repo>.json` — deep scanner evidence and compatibility context.
2. `repo_analysis.json` — current repo/runtime facts; extend this layer with branch telemetry where appropriate.
3. `planning_contract.json` — repository planning/NEXT_UP authority.
4. ProjectScanner intelligence packet / portfolio index — normalized operational evidence.
5. `chatgpt_context.json` — compact model-facing projection, never source of truth.
6. RAG corpus — searchable detailed and historical evidence.
7. Notion/DreamVault — human projection and downstream governance/assignment authority respectively.

Do not introduce `branch_cleanup.json`, `branch_manifest.json`, or equivalent new artifact families unless a concrete machine boundary later proves they are necessary.

### Branch retirement policy target

ProjectScanner observes and classifies; it does not delete branches.

- `FAST_PATH`: no open PR, not default/protected, no unique forward history, no active worktree, no live dependency, and exact branch/head evidence is current.
- `FORENSIC_PATH`: unique history, live dependency, or materially ambiguous evidence requires one bounded inspection/salvage decision.
- `KEEP`: active/open/protected/default or otherwise currently required branch.
- `UNKNOWN`: required evidence is unavailable or stale; do not infer deletion safety.

Heavy manifests and retention workflows are reserved for genuinely unique/live/ambiguous branches rather than ordinary merged or fully-contained branches.

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

### Removed legacy GUI and history

- [ ] Reconcile documentation and launch references that still imply the removed enhanced GUI is available.
- [ ] Decide whether ProjectScanner is intentionally headless or whether a new GUI is justified by current requirements.
- [ ] If a GUI is approved, design it against the canonical scanner API rather than restoring a parallel historical implementation.
- [ ] Keep legacy GUI, token wizard, portfolio-analysis, and enhanced-scanner claims labeled historical or **Needs verification**.

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
