# Dream.OS Portfolio Index v2

## Purpose

`dreamos.portfolio-index.v2` is the ProjectScanner evidence projection intended for the always-on Dream.OS headquarters state compiler.

It does **not** become governance authority and it does **not** rank or execute tasks.

The boundary is:

```text
repository files / Git / scanner evidence
                |
                v
          ProjectScanner
                |
      portfolio_index_v2.json
                |
                v
      Dream.OS HQ state compiler
        /        |         \
       /         |          \
Git/CPC events  runtime   DreamVault decisions
       \         |          /
        \        |         /
             HQ state
                |
                v
         DreamVault planner
                |
                v
        model/passdown views
```

## Existing capability reused

This lane is intentionally an extension of existing ProjectScanner and DreamVault behavior rather than a new parallel planner.

ProjectScanner already provides:

- `planning_contract.json`
- `repo_analysis.json`
- `chatgpt_context.json`
- `cleanup_recommendations.json`
- `docs_gap_report.md`
- fleet-level `portfolio_index.json` (`dreamos.portfolio-index.v1`)

DreamVault already provides:

- `runtime/scripts/planner_registry.py`, which inventories planner fragments and event/proof surfaces
- `dreamvault/portfolio_planner.py`, which validates canonical `MASTER_TASK_LIST.md` / `NEXT_UP.md` task rows and ranks eligible candidates
- `runtime/scripts/portfolio_next_task.py`, which currently reads repository planning surfaces directly

The migration target is to make ProjectScanner the normalized repository-planning evidence producer, then make DreamVault consume that normalized evidence. The existing DreamVault direct-file parser is retained until parity is proven; it must not be silently deleted during migration.

## What v2 adds

The v1 export remains intact for compatibility. v2 is generated alongside it as `portfolio_index_v2.json`.

For each repository, v2 adds:

1. A fleet-standard task inventory parsed from the planning authority paths already selected by `planning_contract.json`.
2. Fail-closed validation that `NEXT_UP` is a bounded projection of `MASTER_TASK_LIST` for recognized structured task rows.
3. Explicit assignable task evidence (`READY` / `ACTIVE`) only when projection validation passes.
4. An artifact catalog that records the role of each generated ProjectScanner bundle artifact.
5. Optional references into the deeper ProjectScanner analysis/context library.

## Task inventory

Structured fleet task rows normalize both of these presentation forms:

```text
TASK-001 | P0 | ACTIVE | Implement the state bridge
`TASK-001 | P0 | ACTIVE` — Implement the state bridge
```

Normalized fields are:

```text
task_id
priority
status
title
line
```

The inventory preserves three surfaces separately:

- `master` — recognized rows from `MASTER_TASK_LIST.md`
- `next_up` — recognized rows from `NEXT_UP.md`
- `log` — recognized rows from `MASTER_TASK_LOG.md`

`MASTER_TASK_LOG.md` remains historical evidence. Presence in the log does not independently authorize execution.

### Fail-closed projection checks

v2 records errors for:

- more than five recognized `NEXT_UP` tasks
- duplicate task IDs in master or next-up
- a next-up task absent from master
- priority drift
- status drift
- an `ACTIVE` master task missing from next-up

If any projection error exists:

```text
projection.valid = false
projection.assignable = []
```

ProjectScanner does not choose a replacement task.

## Artifact roles

Generated artifacts are explicitly typed so downstream systems do not accidentally promote a projection into authority.

| Artifact | Role |
|---|---|
| `repo_analysis.json` | repository evidence |
| `planning_contract.json` | normalized planning evidence |
| `chatgpt_context.json` | model projection |
| `cleanup_recommendations.json` | recommendation projection |
| `docs_gap_report.md` | operator projection |
| `project_analysis_<repo>.json` | deep project evidence |
| `chatgpt_project_context_<repo>.json` | deep model projection |

All ProjectScanner-generated artifacts remain evidence/projections. Repository planning files remain repository-local intent authority; DreamVault remains portfolio governance/planner authority.

## Deep analysis library

When `--analysis-library-root` is supplied, v2 records matching:

```text
project_analysis_<repo>.json
chatgpt_project_context_<repo>.json
```

under the declared library root.

This makes the deep ProjectScanner library discoverable from the HQ index without copying its contents into every planner packet.

## Command

```bash
python -m projectscanner.portfolio_index_v2 \
  --projects-root /path/to/projects \
  --out-root /path/to/projectscanner-export \
  --analysis-library-root /path/to/projectscanner-analysis-library
```

Outputs include the existing v1 bundle plus:

```text
portfolio_index_v2.json
```

## Authority contract

The v2 top level declares:

```text
authority=projectscanner_evidence_not_execution_state
```

and the projection contract declares:

```text
planner_candidate_source=repos[].task_inventory.projection.assignable
planner_authority=DreamVault
model_context_role=projection_only
generated_artifacts_override_repository_authority=false
```

## What does not belong in ProjectScanner v2

ProjectScanner should not absorb the whole VPS control plane.

These remain downstream HQ-state inputs:

- GitHub event stream / Git watcher events
- CPC closeout events
- agent/session events
- deployment/runtime state
- DreamVault authorization and decisions
- planner ranking/scoring
- mutation/enforcement

The downstream HQ compiler reconciles those sources with `portfolio_index_v2.json`.

## Migration sequence

```text
1. ProjectScanner v2 emits normalized task/evidence records.
2. Prove v2 against representative real repositories.
3. Add a DreamVault planner adapter that consumes v2 assignable records.
4. Run old direct-file planner and v2-backed planner in parity mode.
5. Only after parity, retire duplicate direct repository parsing from the planner path.
6. Add Git/CPC/runtime/decision projections in the HQ state compiler.
7. Generate ChatGPT/passdown context from compiled HQ state rather than treating context JSON as a source of truth.
```

No branch deletion, task mutation, planner ranking, or execution authorization is performed by this contract.
