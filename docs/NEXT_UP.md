# Next Up (Agent Handoff)

## Current status
The project now has the minimum SSOT operational chain in place:
- scanner target resolution from repo root with CLI override support,
- artifact-first CI snapshots with metadata,
- SQLite ingestion for historical storage.

See: [`docs/CURRENT_STATE_ASSESSMENT.md`](./CURRENT_STATE_ASSESSMENT.md)
See: [`docs/USING_UPDATED_SCANNER.md`](./USING_UPDATED_SCANNER.md)

## SSOT rules for the next agent
1. **Scanner engine SSOT**: `src/core/projectscanner/`.
2. **Default scan scope SSOT**: `repo_root/src` unless explicit override is provided.
3. **Artifact contract SSOT**: snapshot directory must contain `analysis.json` + `metadata.json`.
4. **No parallel scanner implementations**: wrappers orchestrate only.

---

## Next Agent Prompt (ready to paste)

You are continuing Phase 3 stabilization for ProjectScanner.

### Mission
Harden the snapshot data contract and build TDD-backed confidence around CI artifact generation and SQLite ingestion, while preserving SSOT behavior.

### Constraints
- Enforce SSOT paths and avoid introducing alternate scanner engines.
- Keep touched Python files under 400 LOC.
- Backward compatibility: existing scanner CLI behavior should remain valid where feasible.

### Required outcomes
1. Add schema validation for snapshot inputs (`analysis.json` and `metadata.json`) before DB writes.
2. Add tests for workflow metadata mode mapping logic (extract helper or scriptable unit where needed).
3. Add ingestion tests for:
   - first insert,
   - duplicate snapshot insert,
   - missing required fields,
   - missing files in snapshot dir.
4. Add one lightweight query utility/report command that returns trend deltas across snapshots.

---

## TDD set for next phase

### TDD-1: Snapshot metadata validator
**Red**
- Write tests asserting ingest fails with clear error when required metadata keys are missing (`commit_sha`, `timestamp`, `scan_mode`).

**Green**
- Implement validator used by ingestor prior to DB operations.

**Refactor**
- Keep validator reusable and isolated from DB side effects.

### TDD-2: Analysis payload validator
**Red**
- Write tests for malformed `analysis.json` (non-object, missing `files`, wrong `files` type).

**Green**
- Implement minimal schema checks and actionable error messages.

**Refactor**
- Centralize key names/constants to reduce drift.

### TDD-3: Idempotent ingest behavior
**Red**
- Test ingesting same `repo + commit_sha` twice does not duplicate `snapshots` rows.

**Green**
- Confirm current insert/select fallback behavior and tighten where needed.

**Refactor**
- Simplify snapshot-id resolution path.

### TDD-4: Issue/file ingestion fidelity
**Red**
- Test that files/issues counts in DB match payload counts for a fixture snapshot.

**Green**
- Ensure inserts map fields exactly and preserve raw file JSON.

**Refactor**
- Add tiny helper functions for row mapping to improve readability.

### TDD-5: CI mode mapping contract
**Red**
- Add tests that event/ref combinations map to expected mode (`nightly`, `pr`, `release`, `main`, `manual`).

**Green**
- Extract mode resolution into a testable script/helper consumed by workflow.

**Refactor**
- Keep logic single-source and documented.

### TDD-6: Trend query smoke utility
**Red**
- Add test for command/query returning latest N snapshots and basic deltas (e.g., total_files change).

**Green**
- Implement utility using existing DB schema.

**Refactor**
- Keep output stable JSON for downstream automation.

---

## Recommended execution order
1. Build fixture snapshots for tests.
2. Implement validators (metadata + analysis).
3. Add/lock idempotency and fidelity tests.
4. Extract and test mode mapping helper used by workflow.
5. Add trend query utility + tests.
6. Run full test suite and update docs with any contract changes.

## Definition of done
- New validation and ingest tests pass.
- Mode mapping contract is test-covered and single-sourced.
- One trend query/report command exists with tests.
- SSOT path behavior remains intact.
- Updated docs reflect any schema changes.
