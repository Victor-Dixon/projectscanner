# Strategic Agent Policy Note

Last synchronized: 2026-08-13

This document is portfolio policy material and is not the primary ProjectScanner agent instruction file. For repository-specific agent instructions, use root `AGENTS.md`.

## Current ProjectScanner project

ProjectScanner is repository scanning and inventory intelligence tooling in the software repository analysis domain.

## Current policy-related implementation

- Repository instructions: `AGENTS.md`
- Deployment utility: `src/deployment/agents/deploy_agent_policy.py`
- Quality checker tools: `src/quality/`
- Contract engine and rules: `src/core/rules/`
- CI enforcement workflow: `.github/workflows/agent-enforcer.yml`
- Configured pre-commit file: `config/.pre-commit-config.yaml`

## Current product documentation

- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Active next work: `NEXT_UP.md`
- Strategic inventory: `MASTER_TASK_LIST.md`
- Verified completion history: `MASTER_TASK_LOG.md`

## Fleet working policy

The root `AGENTS.md` standard repository working contract is authoritative for execution behavior: read repo truth first, work one bounded TARGET/ACTION/VERIFY/COMMIT lane, use test-first verification, synchronize `NEXT_UP.md` and `MASTER_TASK_LIST.md` with state changes, append `MASTER_TASK_LOG.md` only after evidence proves closure, create `runtime/tasks/*.yaml` for non-trivial lanes when supported, salvage before destructive cleanup, and leave the next executable verification gate on closeout.

This strategic copy must not redefine or weaken that contract.

## Current next work

Stabilize the snapshot artifact contract between CI scanner output and `ingest_snapshot.py`.
