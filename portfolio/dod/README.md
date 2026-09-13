# Portfolio Definition of Done and MVP Registry

ProjectScanner is the evidence producer for this registry. It does not become portfolio governance or mutation authority.

## Contract

Each repository profile defines two different things:

- **MVP** — the smallest useful product outcome supported by the repository's purpose and evidence.
- **Definition of Done** — the evidence required to declare that repository complete for its current product boundary.

ProjectScanner evaluates evidence against these definitions. DreamVault/CPC remain responsible for portfolio governance, ranking, and authorized mutation.

## Evidence rules

1. Repository-local PRD/ROADMAP/PROJECT_STATUS/task artifacts are the primary intent sources.
2. GitHub, CI, tests, deployment/runtime evidence prove execution reality.
3. Closed-unmerged PR state is never proof that work did not reach the default branch.
4. Semantic/content comparison may be required when independently implemented work supersedes another branch.
5. Unknown or currently unresolvable repositories are never treated as empty or done.
6. A protected/no-go repository boundary remains authoritative and cannot be weakened by this registry.

## Status model

`DONE`, `DONE_WITH_INTENTIONAL_KEEP`, `BLOCKED`, `HOLD`, `NOT_READY`.

A repository cannot be `DONE` while required evidence is unknown, contradictory, or unaccounted for.
