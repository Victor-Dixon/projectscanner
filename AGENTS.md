# ProjectScanner Agent Instructions

Last synchronized: 2026-08-13

## Project identity

ProjectScanner is repository scanning and inventory intelligence tooling. It belongs to the software repository analysis domain and exists to produce machine-readable evidence about local and GitHub repositories before cleanup, consolidation, promotion, or automation decisions.

## Source of truth

- Canonical scanner source: `src/core/projectscanner/`.
- Domain model: `docs/DOMAIN_MODEL.md`.
- Repository audit: `docs/REPOSITORY_AUDIT.md`.
- Requirements: `PRD.md`.
- Roadmap: `ROADMAP.md`.
- Canonical task list: `MASTER_TASK_LIST.md`.
- Verified completed history: `MASTER_TASK_LOG.md`.
- Current handoff: `NEXT_UP.md`.
- Historical overlay experiment: `archive/untracked_overlay_20260505/`.

## Working rules

- Do not create parallel scanner engines. Extend or fix `src/core/projectscanner/` for scanner behavior.
- Do not describe incomplete features as shipped. Mark uncertain items as Unknown.
- Keep documentation synchronized when behavior, contracts, or status change.
- Prefer tests before changing snapshot, ingestion, scanner output, or public CLI behavior.
- Preserve generated/runtime scan outputs only when explicitly promoted; otherwise treat them as disposable artifacts.
- Avoid editing archived overlay files unless the task explicitly asks for archive work.

## Verification

Current regression gate:

```bash
pytest -q
```

## Standard Repository Working Contract
1. Read `AGENTS.md`, `NEXT_UP.md`, `MASTER_TASK_LIST.md`, `MASTER_TASK_LOG.md`, any repo SSOT/state manifest, branch/HEAD, and relevant tests before editing.
2. Work one bounded lane with explicit **TARGET, ACTION, VERIFY, COMMIT**. Do not mix unrelated cleanup, features, migrations, or speculative rewrites.
3. Use Fast TDD: smallest acceptance/contract test, smallest safe change, targeted verification, then broad verification.
4. When repo state changes, update `NEXT_UP.md` and `MASTER_TASK_LIST.md` in the same lane, plus the execution-state SSOT when present.
5. Append `MASTER_TASK_LOG.md` only after verification proves closure. Never record planned or merely implemented work as completed.
6. For non-trivial work, create/update `runtime/tasks/*.yaml` with objective, scope, acceptance, verification, holds, and next lane when supported.
7. Trust but verify: targeted tests, repo validators, `git diff --check`, and final status/diff review. PASS/COMPLETE/promoted/merged claims require evidence.
8. Salvage before destructive cleanup. Classify variants/donor material before delete/reset/rewrite; preserve canonical scanner source unless evidence proves it stale.
9. End code or repo-structure work with a clean scoped commit. Planning-only work still requires synchronized task surfaces and verification.
10. Leave the next executable step in `NEXT_UP.md` with its verification gate so the next agent does not rediscover the lane.

### Canonical Planning Names
Fleet-standard root planning files are `NEXT_UP.md`, `MASTER_TASK_LIST.md`, and `MASTER_TASK_LOG.md`. Legacy aliases or nested policy notes must not become competing execution authorities.
