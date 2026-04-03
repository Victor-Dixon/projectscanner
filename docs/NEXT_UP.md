# Next Up (Agent Handoff)

## Current status
Phase 1 (contract restoration + SSOT path recovery) is complete:
- `ProjectScanner` and `LanguageAnalyzer` are restored under `src/core/projectscanner/`.
- Entry points now use SSOT imports.
- Scanner core now includes performance upgrades (parallel scan, cheap cache checks, bare-repo metadata mode, context chunk exports).

See: [`docs/CURRENT_STATE_ASSESSMENT.md`](./CURRENT_STATE_ASSESSMENT.md)
See: [`docs/USING_UPDATED_SCANNER.md`](./USING_UPDATED_SCANNER.md)

## What was added now for Phase 2 readiness
- New tests in `tests/test_phase2_handoff.py` validating:
  1. context chunk export behavior,
  2. bare repo metadata output,
  3. `main.py` SSOT import usage.

## Next agent priorities (Phase 2)
1. **Canonicalize imports everywhere**
   - Ensure all scanner consumers import from package root:
     - `from core.projectscanner import ProjectScanner, LanguageAnalyzer`
   - Remove any remaining direct-module or legacy-path imports.

2. **Unify CLI surface area**
   - Keep one canonical scanner CLI.
   - Ensure wrappers call the SSOT scanner and only orchestrate targets.

3. **Add batch wrapper tests**
   - Multi-target scan execution.
   - Aggregated summary generation.
   - Failure isolation (one target failing does not stop remaining targets).

4. **Compatibility checks before deeper refactor**
   - Preserve current report filenames and key JSON fields.
   - Verify context index/chunk schema remains stable for downstream tools.

## Definition of done for next phase
- No legacy scanner import paths remain.
- Batch wrapper behavior is covered by tests.
- Existing scanner contract remains green in pytest.
