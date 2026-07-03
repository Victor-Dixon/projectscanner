# Strategic Agent Policy Note

Last synchronized: 2026-07-03

This document is portfolio policy material and is not the primary ProjectScanner agent instruction file. For repository-specific agent instructions, use root `AGENTS.md`.

## Current ProjectScanner project

ProjectScanner is repository scanning and inventory intelligence tooling in the software repository analysis domain.

## Current policy-related implementation

- Repository instructions: `AGENTS.md`
- Deployment utility: `src/deployment/agents/deploy_agent_policy.py`
- Quality checker tools: `src/quality/`
- Contract engine and rules: `src/core/rules/`
- CI enforcement workflow: `.github/workflows/agent-enforcer.yml`
- Configured pre-commit file in this repository: `config/.pre-commit-config.yaml`

## Important path correction

Older portfolio-policy material referenced quality checkers under `scripts/` and a root `.pre-commit-config.yaml`. Those are not the current paths in this repository.

## Current product documentation

- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Active next work: `NEXT_UP.md`

## Current next work

Stabilize the snapshot artifact contract between CI scanner output and `ingest_snapshot.py`.