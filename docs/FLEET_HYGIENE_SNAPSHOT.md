# Fleet Hygiene Snapshot v1

## Purpose

`projectscanner_fleet_hygiene_snapshot.v1` records branch and Git-worktree intelligence for one repository.

The v1 boundary is deliberately split across systems:

- AgentTools `agent_tools.repo` owns deterministic Git inspection facts.
- ProjectScanner aggregates those facts into repository/fleet hygiene signals.
- DreamVault owns durable governance decisions and policy.
- CPC owns any later mutation or enforcement step.

ProjectScanner must not grow a second private Git plumbing layer in this lane, and neither AgentTools nor ProjectScanner may delete branches, prune worktrees, rewrite refs, or authorize cleanup.

## Install

The hygiene lane is optional so normal ProjectScanner scans do not need the AgentTools package:

```bash
pip install -e '.[hygiene]'
```

The current development extra is pinned to the AgentTools repo-toolbelt proof commit until that cross-repo contract is promoted.

## Command

```bash
projectscanner hygiene /path/to/repo \
  --canonical-branch master \
  --output /tmp/projectscanner_fleet_hygiene.json
```

Use `--json` to print the complete snapshot to stdout.

If `--canonical-branch` is omitted, ProjectScanner asks AgentTools for the configured remote default branch, then applies ProjectScanner's `master`, `main`, and current-branch fallbacks.

## Schema

Top-level fields:

```text
schema
generated_at
repo
branches
worktrees
signals
policy
```

### Repository evidence

`repo` records:

- repository name and absolute worktree root
- origin URL when configured
- HEAD SHA
- current branch
- canonical branch and the Git ref used for comparison

The Git toplevel comes from AgentTools. This prevents a nested folder that happens to be named after another project from being miscounted as a repository.

### Branch sensor

AgentTools supplies local and `origin/*` branch facts plus ref comparisons. The symbolic `origin/HEAD` ref is treated as default-branch metadata, not as a real branch count.

ProjectScanner adds:

- whether a branch is current or canonical
- commits ahead of / behind the canonical ref
- whether the branch tip is already an ancestor of the canonical ref
- local-only and merged-noncanonical counts

The sensor intentionally does **not** infer PR ownership, task ownership, or deletion authorization in v1.

### Worktree sensor

AgentTools parses:

```bash
git worktree list --porcelain
```

and supplies:

- absolute path
- HEAD SHA
- attached branch/ref or detached state
- bare / locked / prunable flags
- current dirty and untracked counts
- raw dirty paths

ProjectScanner applies its existing dirty-path classifier so the same raw Git status can be interpreted as source code, generated runtime, reports, documentation, configuration, and related categories.

A detached worktree is therefore a fact, not automatically a defect. The VPS acceptance case includes a healthy clean exact-SHA detached ProjectScanner runtime checkout.

## Signals

The snapshot includes deterministic counts that downstream governance can use, including:

- noncanonical local and remote branch counts
- local-only branch count
- merged noncanonical branch counts
- dirty worktree count
- detached worktree count
- prunable worktree count

These are evidence signals, not mutation decisions.

## Phase boundary

v1 covers **branch inventory** and **worktree inventory**.

Cross-repository duplication/capability similarity remains a separate phase. Exact SHA matching, tree similarity, and model-assisted capability equivalence should be added only after this evidence contract and AgentTools boundary are verified against the real VPS fleet.
