# Dream.OS Fleet Planning Contract v1

Last synchronized: 2026-08-12

## Purpose

ProjectScanner normalizes repository planning state into machine-readable evidence. It does not silently rewrite repository authority files or make Notion an independent source of truth.

## Required authority files

Each active repository must provide:

- `MASTER_TASK_LIST.md` — canonical backlog and strategic inventory.
- `MASTER_TASK_LOG.md` — append-only completed history.
- `NEXT_UP.md` — immediate handoff, with no more than five numbered actions under `## Immediate actions`.
- `DOMAIN_MODEL.md` or `docs/DOMAIN_MODEL.md` — project domain, ownership, entities, boundaries, and supported behavior.

`PROJECT_STATUS.md` may be added by a repository when a separate current-state summary is useful, but it is not required by v1.

## Normalized record

`projectscanner planning <repo> --json` emits schema `dreamos.fleet-planning.v1` with:

- repository identity and path
- contract status: `PASS`, `WARN`, or `FAIL`
- required-file presence
- domain-model location
- synchronization dates when declared
- active lane derived from the first immediate action
- normalized immediate actions
- machine-readable findings

The portfolio exporter writes the same record to `planning_contract.json` and projects status, active lane, and findings into `chatgpt_context.json`.

## Findings

v1 detects:

- missing required planning files
- missing domain model
- missing immediate actions
- more than five immediate actions
- synchronization-date drift across authority documents

Missing authority is a `FAIL`. Structural drift is a `WARN`. A repository with the required planning set and no detected drift is `PASS`.

## Authority boundary

ProjectScanner is the evidence and normalization layer. Repository planning files remain authoritative for repository-local intent. Dream.OS portfolio state aggregates ProjectScanner records. Notion and public WeAreSwarm surfaces are downstream projections and must not overwrite repository authority without an explicit reconciliation workflow.

## Target data flow

```text
repository planning files
        |
        v
ProjectScanner planning contract
        |
        +--> planning_contract.json
        +--> portfolio chatgpt_context.json
        |
        v
Dream.OS portfolio aggregation
        |
        +--> Notion operational views
        +--> Dream.OS planner
        +--> verified WeAreSwarm proof/capability feeds
```

## Promotion rule

A downstream sync may publish normalized records automatically only when the contract result is `PASS` or when the consumer preserves `WARN`/`FAIL` as explicit state. Consumers must not reinterpret missing data as completion.
