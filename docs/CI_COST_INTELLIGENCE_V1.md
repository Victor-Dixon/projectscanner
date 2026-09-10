# CI cost and runner intelligence V1

ProjectScanner produces observational evidence about GitHub Actions configuration. It does not own CI policy, runner administration, workflow execution, billing, or merge authority. This feature extends the existing intelligence package and public CLI; it is not a new scanner engine.

## Use

Install the optional parser dependency in an isolated environment: `python -m pip install '.[ci,dev]'`. Run `projectscanner ci-cost /path/to/repo --output /path/to/ci_cost.json`, or `projectscanner ci-cost --projects-root /path/to/projects --repos AgentTools projectscanner --output /path/to/portfolio_ci.json`. The command reads the supplied checkout only. The public CLI also supports `--json` and `--usage-json /path/to/measured_usage.json`.

For a reproducible scan, verify the repository's Git HEAD and origin provenance separately, then record the exact source revision in the acceptance record. The static sensor does not fetch repositories or assert that a checkout is current. Its per-file SHA-256 digests identify the inspected bytes. Run a fresh scan if workflow files change.

## Evidence contract

The single-repo output uses `projectscanner.ci-cost.v1`; portfolio output uses `projectscanner.ci-portfolio.v1`. Each includes source paths, source hashes, runner classifications, findings, and an evidence-only governance declaration. Existing intelligence packets, planning contracts, portfolio indexes, and HQ adapters remain unchanged. No existing v1 consumer is required to read this optional report.

The sensor records workflow triggers, concurrency, job definitions, static matrix runner labels, reusable workflow references, permissions, containers, environments, advisory jobs, and possible duplicate execution. Literal GitHub-hosted labels are classified separately from self-hosted labels. Expressions, unresolved matrices, and delegated jobs remain unknown. A declared self-hosted label does not prove a runner is online, registered, safe, or available. Job counts are configuration counts, not actual executions or billable minutes.

Potential duplicate findings are review signals, not proof of waste. Path/branch filters, conditions, matrix exclusions, reusable workflows, and dynamic expressions may prevent execution. The scanner retains uncertainty rather than guessing. It never deletes or disables checks. A malformed or unreadable workflow makes the inventory incomplete; missing evidence must not be interpreted as zero hosted usage.

## Measured billing evidence

Actual billed dollars and minutes are unavailable unless supplied explicitly. The optional input is:

```json
{
  "schema": "projectscanner.ci-usage.v1",
  "source": "github.actions.billing",
  "billing_source": "operator-reviewed-billing-export",
  "period": "2026-09",
  "billable_minutes": 42,
  "billed_usd": 0.0
}
```

Values must be nonnegative, finite, measured numbers. A dollar amount requires billing provenance. The sensor does not multiply job counts by assumed minutes, infer rates from runner labels, or claim savings from a configuration change. Credits, free allowances, storage, runner costs, and billing adjustments require separate authoritative evidence. Usage is an optional aggregate and is not automatically attributed to individual jobs.

## Migration boundaries

ProjectScanner can recommend investigation of hosted placement, repeated advisory work, overlapping triggers, excessive permissions, and unsafe self-hosted PR execution. DreamVault owns the decision and approval; AgentTools supplies reusable inspection and execution primitives; the managed runtime owns runner health and execution. ProjectScanner does not duplicate those systems.

Before any migration, verify exact-head required-check names and branch protection, runner registration and capacity, supported toolchains, dependency isolation, fork/untrusted-code policy, secrets and token permissions, release/deployment gates, and representative parity tests. Self-hosted runners are not automatically safer or less expensive. Release publishing and privileged workflows must retain their security boundaries. No runner re-registration, service restart, workflow rewrite, CI rerun, merge, or deployment is part of this feature.

## Acceptance and remaining work

The local V1 contract gate is `pytest -q tests/test_ci_cost.py tests/test_ci_cost_cli.py`; broader repository verification remains required before promotion. The source uses Python 3.11+ and optional PyYAML 6.x. No production fleet scan, billing reconciliation, runner migration, or HQ integration is claimed. The next governed lane consumes these reports and separately resolves current remote authority, actual usage, and required-check policy. Preserve existing ProjectScanner PRs #22 and #23; do not merge their branches wholesale into this feature.
