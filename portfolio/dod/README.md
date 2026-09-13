# Portfolio Definition of Done and MVP Registry

ProjectScanner is the evidence producer for this registry. It does not become portfolio governance or mutation authority.

## Contract

Each repository profile defines two different things:

- **MVP** — the smallest useful product outcome supported by the repository's purpose and evidence.
- **Definition of Done** — the evidence required to declare that repository complete for its current product boundary.

ProjectScanner evaluates evidence against these definitions. DreamVault/CPC remain responsible for portfolio governance, ranking, and authorized mutation.

## Files

- `schema.json` — machine-readable contract for one repository's MVP/DoD.
- `repository_keys.json` — the 25-repository portfolio membership list.
- `profiles.json` — initial MVP statements and evidence-source status.

Profiles marked `needs current repo review` are not treated as authoritative product definitions until the repository's own PRD, roadmap, status SSOT, task list, and live implementation are reviewed.

## Common completion evidence

1. Canonical repository state is verified.
2. Portfolio identity is verified.
3. Planning authority is reconciled.
4. Non-default refs are classified.
5. Unique work is accounted for.
6. Semantic supersession is checked when needed.
7. Relevant tests are green.
8. Runtime/deployment evidence is satisfied when applicable.
9. Planner state is reconciled.
10. A durable completion receipt is written.

Missing or contradictory evidence never becomes an implicit pass.

## Evidence rules

1. Repository-local PRD/ROADMAP/PROJECT_STATUS/task artifacts are the primary intent sources.
2. GitHub, CI, tests, deployment, and runtime evidence prove execution reality.
3. Closed-unmerged PR state is never proof that work did not reach the default branch.
4. Semantic/content comparison may be required when independently implemented work supersedes another branch.
5. Unknown or currently unresolvable repositories are never treated as empty or done.
6. Existing repository safety boundaries remain authoritative and cannot be weakened by this registry.
