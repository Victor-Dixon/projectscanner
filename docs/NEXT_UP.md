# Next Up (Agent Handoff)

## Current status
The project now has the minimum SSOT operational chain in place:
- scanner target resolution from repo root with CLI override support,
- artifact-first CI snapshots with metadata,
- normalized `analysis.json` snapshot output,
- SQLite ingestion for historical storage with preflight contract validation and duplicate-ingest refresh behavior.

See: [`docs/CURRENT_STATE_ASSESSMENT.md`](./CURRENT_STATE_ASSESSMENT.md)
See: [`docs/USING_UPDATED_SCANNER.md`](./USING_UPDATED_SCANNER.md)

## SSOT rules for the next agent
1. **Scanner engine SSOT**: `src/core/projectscanner/`.
2. **Default scan scope SSOT**: `repo_root/src` unless explicit override is provided.
3. **Artifact contract SSOT**: snapshot directory must contain `analysis.json` + `metadata.json`; `analysis.json.schema` must be `projectscanner.snapshot.v1`.
4. **No parallel scanner implementations**: wrappers orchestrate only.

---

## Next Agent Prompt (ready to paste)

You are continuing Phase 3 stabilization for ProjectScanner.

### Mission
Continue Phase 3 stabilization by expanding CI confidence and adding trend/query ergonomics, while preserving SSOT behavior.

### Constraints
- Enforce SSOT paths and avoid introducing alternate scanner engines.
- Keep touched Python files under 400 LOC.
- Backward compatibility: existing scanner CLI behavior should remain valid where feasible.

### Required outcomes
1. Add tests for workflow metadata mode mapping logic (extract helper or scriptable unit where needed).
2. Add one lightweight query utility/report command that returns trend deltas across snapshots.
3. Extend normalized analysis only if downstream consumers prove they need more fields.

---

## TDD set for next phase

### TDD-1: CI mode mapping contract
**Red**
- Add tests that event/ref combinations map to expected mode (`nightly`, `pr`, `release`, `main`, `manual`).

**Green**
- Extract mode resolution into a testable script/helper consumed by workflow.

**Refactor**
- Keep logic single-source and documented.

### TDD-2: Trend query smoke utility
**Red**
- Add test for command/query returning latest N snapshots and basic deltas (e.g., total_files change).

**Green**
- Implement utility using existing DB schema.

**Refactor**
- Keep output stable JSON for downstream automation.

---

## Recommended execution order
1. Extract and test mode mapping helper used by workflow.
2. Add trend query utility + tests.
3. Run full test suite and update docs with any contract changes.

## Definition of done
- Mode mapping contract is test-covered and single-sourced.
- One trend query/report command exists with tests.
- SSOT path behavior remains intact.
- Updated docs reflect any schema changes.
