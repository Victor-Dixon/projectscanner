# ProjectScanner Next Up

Last synchronized: 2026-09-09

## Purpose

This file is the immediate handoff only. The canonical backlog is `MASTER_TASK_LIST.md`, and completed history is recorded in `MASTER_TASK_LOG.md`.

The scanner source of truth is `src/core/projectscanner/`. Do not restore removed scanner or GUI implementations as parallel engines, and mark unverified behavior as Unknown.

## Immediate actions

1. **PSC-HYGIENE-001 — reconcile PR #22 as the canonical branch/worktree sensor foundation.** Do not create another branch inventory implementation. Preserve its observational boundary: ProjectScanner reports branch/worktree facts; it does not delete branches.
2. **PSC-INTEL-001 — reconcile PR #23 as the canonical portfolio evidence/artifact-role foundation.** Preserve the artifact hierarchy and the boundary that `chatgpt_context.json` is a compact model projection, not source of truth.
3. **PSC-RETIRE-001 — after the two foundations are accepted, add deterministic branch retirement classification.** Consume current branch/PR/containment/worktree/dependency facts and emit only `FAST_PATH`, `FORENSIC_PATH`, `KEEP`, or `UNKNOWN`. Do not add another standalone branch-cleanup JSON family.
4. **PSC-CONTEXT-001 — project branch retirement results through existing analysis/intelligence/context/RAG layers.** Extend `repo_analysis.json`, the ProjectScanner intelligence/portfolio packet, `chatgpt_context.json`, and the existing RAG corpus as appropriate rather than duplicating evidence.
5. **PSC-FLEET-001 — run the reconciled scanner across the governed repo fleet.** Produce a planning-drift and branch-retirement inventory for downstream DreamVault reconciliation; ProjectScanner remains evidence/classification, DreamVault remains governance/assignment authority.

## Branch retirement target policy

- `FAST_PATH`: no open PR, not default/protected, no unique forward history, no active worktree, no live dependency, and current exact branch/head evidence.
- `FORENSIC_PATH`: unique history, live dependency, or materially ambiguous evidence needs one bounded inspection/salvage decision.
- `KEEP`: active/open/protected/default or otherwise currently required.
- `UNKNOWN`: required evidence is missing or stale; do not infer deletion safety.

Heavy manifests and retention workflows are not required for ordinary merged/fully-contained branches. Reserve them for genuinely unique, live, or ambiguous cases.

## Artifact hierarchy

```text
project_analysis_<repo>.json / chatgpt_project_context_<repo>.json
    deep scan evidence / compatibility context

repo_analysis.json
    current repo/runtime facts

planning_contract.json
    repo planning authority

ProjectScanner intelligence packet / portfolio index
    normalized operational evidence

chatgpt_context.json
    compact model handoff

RAG corpus
    searchable detailed + historical evidence

DreamVault / Notion
    governance authority / human projection
```

## Exit criteria for this handoff

- PR #22 and PR #23 are treated as the existing foundations; no parallel implementation lanes are created for the same capabilities.
- Branch retirement classification is deterministic and fail-closed on missing/stale required evidence.
- Existing analysis/context/RAG layers are extended instead of proliferating new JSON artifact families.
- ProjectScanner never gains branch-deletion authority; mutation remains downstream and governed.
- Fleet output is sufficient to identify planning drift and fast-path cleanup candidates without requiring repeated manual forensic manifests.
- `pytest -q` remains the regression gate for later implementation changes.

## References

- Canonical task inventory: `MASTER_TASK_LIST.md`
- Completed history: `MASTER_TASK_LOG.md`
- Existing hygiene implementation: PR #22
- Existing portfolio evidence implementation: PR #23
- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Agent instructions: `AGENTS.md`
