# Agent Policy Deployment Guide

Last synchronized: 2026-07-03

This guide is portfolio policy material, not the primary ProjectScanner product documentation.

## Current ProjectScanner context

ProjectScanner is repository scanning and inventory intelligence tooling. It belongs to the software repository analysis domain and emits evidence for cleanup, consolidation, promotion, and automation workflows.

## Current in-repository policy files

- Repository-specific agent instructions: `AGENTS.md`
- Portfolio policy note: `docs/strategic/AGENTS.md`
- Deployment utility: `src/deployment/agents/deploy_agent_policy.py`
- Quality checkers: `src/quality/`
- CI enforcement workflow: `.github/workflows/agent-enforcer.yml`
- Pre-commit config location in this repository: `config/.pre-commit-config.yaml`

## Important path correction

Older versions of this guide referenced root-level `deploy_agent_policy.py`, root `.pre-commit-config.yaml`, and `scripts/*_checker.py`. Those paths are not current for this repository.

## Current product documentation

- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Codebase overview: `docs/CODEBASE_OVERVIEW.md`
- Active next work: `NEXT_UP.md`

## What remains

If policy deployment is made an active ProjectScanner feature, update this guide with tested commands and exact supported targets. Until then, treat it as supporting portfolio material.