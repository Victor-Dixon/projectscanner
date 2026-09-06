# Fleet Hygiene Snapshot v1

## Purpose

`projectscanner_fleet_hygiene_snapshot.v1` records branch and Git-worktree evidence for one repository.

ProjectScanner remains observational in this lane:

- ProjectScanner discovers and normalizes repository facts.
- DreamVault owns durable governance decisions and policy.
- CPC owns any later mutation or enforcement step.

The sensor must not delete branches, prune worktrees, rewrite refs, or decide promotion/retention policy solely because an implementation exists.

## Command

```bash
projectscanner hygiene /path/to/repo \
  --canonical-branch master \
  --output /tmp/projectscanner_fleet_hygiene.json
```

Use `--json` to print the complete snapshot to stdout.

If `--canonical-branch` is omitted, ProjectScanner resolves the branch from `origin/HEAD`, then `master`, then `main`, then the current branch.

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

### Branch sensor

The branch sensor records local branches and `origin/*` remote-tracking branches.

For each branch it can record:

- branch/ref name
- commit SHA and commit timestamp
- upstream for local branches
- whether it is current or canonical
- commits ahead of / behind the canonical ref
- whether the branch tip is already an ancestor of the canonical ref

The sensor intentionally does **not** infer PR ownership, task ownership, or deletion authorization in v1.

### Worktree sensor

The worktree sensor parses:

```bash
git worktree list --porcelain
```

For each worktree it records:

- absolute path
- HEAD SHA
- attached branch/ref or detached state
- bare / locked / prunable flags
- current dirty and untracked counts
- dirty-path classes from the existing ProjectScanner dirty classifier

The sensor does not call `git worktree prune`.

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

Cross-repository duplication/capability similarity remains a separate phase. Exact SHA matching, tree similarity, and model-assisted capability equivalence should be added only after this evidence contract is verified against the real VPS fleet.
