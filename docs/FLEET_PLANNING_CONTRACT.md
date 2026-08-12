# Dream.OS Fleet Planning Contract v1

Last synchronized: 2026-08-12

## Purpose

ProjectScanner normalizes repository planning state into machine-readable evidence without silently rewriting repository authority. Repositories may preserve intentional filenames, compatibility pointers, and domain-specific queue vocabulary when those choices are declared explicitly.

## Default authority

Without a repository manifest, ProjectScanner looks for:

- `MASTER_TASK_LIST.md` — backlog and strategic inventory.
- `MASTER_TASK_LOG.md` — completed history.
- `NEXT_UP.md` — immediate execution handoff.
- `DOMAIN_MODEL.md`, `domain_model.md`, `docs/DOMAIN_MODEL.md`, or `docs/domain_model.md` — domain authority.

## Repository authority manifest

A repository may add `PLANNING_CONTRACT.json` when its intentional authority differs from the defaults. The manifest is declarative; it does not copy, rename, or replace authority files.

Example:

```json
{
  "schema_version": "dreamos.fleet-planning.v1",
  "repo_key": "github:victor-dixon/agenttools",
  "authority": {
    "master_task_list": "MASTER_TASK_LIST.md",
    "master_task_log": "docs/root/MASTER_TASK_LOG.md",
    "next_up": "NEXT_UP.md",
    "domain_model": "docs/architecture/DOMAIN_MODEL.md"
  },
  "next_up": {
    "action_headings": ["Immediate actions"]
  }
}
```

Manifest paths must be repository-relative and may not escape the repository root.

## Queue normalization

The validator accepts common fleet handoff headings such as `Immediate actions`, `Immediate queue`, `Immediate Next Work`, `Next actions`, `Next work`, `Work next`, `Queue`, `Priority actions`, and nested `Actions`. Numbered heading queues such as `### 1) Clarify product direction` are normalized as actions as well.

Active-lane detection prefers explicit declarations in this order:

1. `NEXT_LANE=...`
2. an `Active lane` section or configured lane heading
3. a `## NOW — ...` heading
4. `Current Priority` or `Current focus`
5. the first normalized immediate action

Repositories with more than five immediate actions remain `WARN`; normalization does not erase queue-size drift.

## Normalized record

`projectscanner planning <repo> --json` emits schema `dreamos.fleet-planning.v1` with:

- stable `repo_key`
- repository identity and path
- fleet state
- contract status: `PASS`, `WARN`, or `FAIL`
- selected authority paths
- synchronization dates when declared
- normalized active lane
- normalized immediate actions
- machine-readable findings

GitHub-backed repositories use `github:<owner>/<repo>` as the stable identity when no manifest key overrides it. Local-only repositories fall back to `local:<repo>`.

## Fleet portfolio index

`projectscanner export` writes per-repository bundles and one fleet-level `portfolio_index.json` using schema `dreamos.portfolio-index.v1`.

The index contains:

- deterministic repo ordering by `repo_key`
- active repository count
- `PASS` / `WARN` / `FAIL` counts
- branch and full HEAD SHA
- active lane and next actions
- authority paths and findings
- source URL when GitHub provenance is available

## Notion projection contract

ProjectScanner produces deterministic desired row properties for the Dream.OS repo portfolio. The projection key is `Repo Key`, not a display name or page ID.

The upsert planner:

- creates a row when a repo key does not exist
- updates the matching row when material properties changed
- returns `noop` when the row already matches
- adopts a legacy unkeyed row by unique repo-name match during migration
- returns a conflict instead of guessing when duplicate repo keys exist

Therefore a repeated run against unchanged portfolio state produces zero new rows and zero updates.

Notion remains a downstream projection. It does not become repository authority.

## Findings

The contract detects or preserves findings including:

- missing required planning authority
- invalid or unsafe manifest paths
- missing domain model
- missing immediate actions
- more than five immediate actions
- synchronization-date drift across the declared sync set
- selected authority files that are compatibility pointers

Missing or invalid authority is `FAIL`. Structural drift is `WARN`. A repository with valid declared authority and no findings is `PASS`.

## Authority boundary

Repository planning files remain authoritative for repository-local intent. ProjectScanner owns normalization and evidence. Dream.OS portfolio state aggregates ProjectScanner records. Notion is an operational projection.

Public WeAreSwarm `/projects/`, `/proof/`, and `/skill-tree/` integration remains blocked until fleet reconciliation and idempotent downstream projection are verified.

## Target data flow

```text
repository planning authority
        |
        v
ProjectScanner planning contract
        |
        +--> planning_contract.json
        |
        v
portfolio_index.json
        |
        +--> deterministic Notion upsert
        +--> Dream.OS planner
        |
        v
verified public projection (later gate)
```
