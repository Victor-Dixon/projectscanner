# ProjectScanner Next Up

Last synchronized: 2026-08-11

## Purpose

This file is the immediate handoff only. The canonical backlog is `MASTER_TASK_LIST.md`, and completed history is recorded in `MASTER_TASK_LOG.md`.

The scanner source of truth is `src/core/projectscanner/`. Do not restore removed scanner or GUI implementations as parallel engines, and mark unverified behavior as Unknown.

## Immediate actions

1. **Verify the canonical scanner path.** Run the current tests against `src/core/projectscanner/`, map tested behavior to the supported scanner surface, and record gaps without changing scanner behavior during the verification pass.
2. **Classify generated analysis assets.** Inventory representative committed and ignored outputs, then classify each family as source, promoted evidence, reproducible artifact, or cleanup candidate.
3. **Confirm RAG and export integration.** Compare the normalized corpus and project-intelligence exports with current Dream Suite needs, including provenance, digest, schema, ownership, and handoff expectations.
4. **Reconcile removed legacy GUI references.** Find documentation and entry points that imply the removed enhanced GUI is shipped; label them historical, remove stale claims, or record a support decision.
5. **Decide local branch provenance policy.** Determine whether `work` should track a remote branch and document the upstream, push, and pull-request policy without changing remote state during the decision pass.

## Exit criteria for this handoff

- Each action produces evidence, a documented decision, or a scoped backlog update.
- No removed legacy implementation is presented as currently shipped.
- Generated assets and Dream Suite integration claims have explicit ownership and verification status.
- Any discovered work is added to `MASTER_TASK_LIST.md`; completed work is appended to `MASTER_TASK_LOG.md`.
- `pytest -q` remains the regression gate for any later implementation change.

## References

- Canonical task inventory: `MASTER_TASK_LIST.md`
- Completed history: `MASTER_TASK_LOG.md`
- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Agent instructions: `AGENTS.md`
