# ProjectScanner — Product Requirements Document

## Problem

Dream.OS portfolios grow faster than governance. A typical workspace can reach **10,000–15,000+ files** across dozens of repos, experiments, overlays, and generated artifacts. That scale is not inherently wrong for a portfolio — but it is embarrassing when the **tool meant to tame the chaos looks like part of the chaos**.

ProjectScanner today has a capable core (`src/core/projectscanner/`) buried under:

- Multiple competing entry points (`main.py`, `run.py`, package CLI, GUI launchers)
- Stub strategic docs that read as placeholders
- Root-level one-off maintenance scripts
- Archived overlay code that duplicates the canonical scanner
- GUI paths that reference modules that no longer exist

A productized ProjectScanner must be **small, sharp, and contract-driven** while scanning arbitrarily large targets.

## Product vision

**One command to understand a repo or portfolio before you archive, promote, or delete anything.**

ProjectScanner is repo intelligence infrastructure for Dream.OS — not a runtime, not DreamVault, not a second portfolio.

## Target users

| User | Job to be done |
|---|---|
| Portfolio operator | Discover what exists, what is stale, what duplicates |
| Consolidation agent | Export machine-readable evidence for DreamVault decisions |
| Maintainer | Track scanner snapshots over time (CI + ingest) |
| Reviewer (optional) | Inspect scan output in a lightweight viewer |

## Non-goals (v0.1)

- Owning Dream.OS runtime or swarm execution
- Long-lived report storage (DreamVault owns that)
- Full IDE / code editor experience
- Scanning and committing outputs back into this repo

## Product principles

1. **Thin product, fat targets** — the tool stays lean; it reads large workspaces.
2. **One way in** — a single CLI with subcommands, not a maze of scripts.
3. **Outputs leave the repo** — intelligence lands in caller-specified directories (DreamVault, CI artifacts).
4. **Contracts over files** — versioned JSON schemas, not ad-hoc report sprawl.
5. **Evidence before deletion** — every cleanup recommendation must cite scan data.

## v0.1 scope (MVP)

### Must ship

| Capability | Acceptance criteria |
|---|---|
| `scan` | Scan a path; write `analysis.json` + optional ChatGPT context |
| `export` | Portfolio export via `scripts/export_project_intelligence.py` contract |
| `ingest` | Snapshot ingest to SQLite for trend queries |
| Package install | `pip install -e .` exposes `projectscanner` console script |
| Regression gate | `pytest -q` green on PR |
| CI snapshot | `.github/workflows/scanner-snapshot.yml` produces retained artifacts |

### Should ship

| Capability | Acceptance criteria |
|---|---|
| Query helper | Basic CLI/SQL queries over `scanner_history.db` |
| Schema version | `analysis.json` includes `schema_version` |
| README quick start | Install, scan, export in <5 minutes |

### Won't ship (v0.1)

- Enhanced GUI with missing module dependencies
- Strategic plan / portfolio analyze modules referenced by broken `main.py` paths
- New scanner engine rewrite (unify via presets on existing `ProjectScanner`)

## File budget (product hygiene)

The repo itself is the product packaging. Targets may have 15k files; **this repo should not**.

| Area | Current (approx.) | v0.1 target | v1.0 target |
|---|---:|---:|---:|
| Tracked files (excl. `.git`) | ~130 | ≤120 | ≤100 |
| Python modules in `src/` | ~80 | ≤60 | ≤50 |
| Root-level `.py` scripts | ~12 | ≤4 | ≤3 |
| Entry points | 5+ | 1 CLI + 1 module | 1 CLI |
| Stub/duplicate docs | many | 0 stubs | 0 |

**Rule:** generated scan output, runtime targets, and portfolio dumps never commit to this repo.

## Canonical boundaries

From `CONSOLIDATION_MANIFEST.md`:

- **projectscanner** — scan mechanics, inventory exports, local ingest
- **DreamVault** — portfolio governance, durable reports, decision records
- **AgentTools** — operator commands that consume scanner output
- **DreamOS** — runtime execution; does not absorb scanner UI or report logic

## Primary workflows

### 1. Quick repo scan

```bash
projectscanner scan /path/to/repo --output /tmp/scan-out
```

Produces `analysis.json` and optional context export.

### 2. Portfolio intelligence export

```bash
python scripts/export_project_intelligence.py \
  --projects-root "$HOME/projects" \
  --out-root "$HOME/projects/DreamVault/data/intelligence/repos_from_projectscanner"
```

Produces `repo_analysis.json`, `chatgpt_context.json`, `cleanup_recommendations.json`, `docs_gap_report.md`.

### 3. CI snapshot + history

1. Workflow runs scanner against `./src`
2. Artifacts uploaded to GitHub Actions
3. `ingest_snapshot.py` loads into `scanner_history.db` for deltas

## Success metrics

| Metric | v0.1 target |
|---|---|
| Time to first scan (new clone) | < 3 minutes |
| `pytest -q` | pass |
| Broken import paths from documented entry | 0 |
| Committed generated artifacts | 0 |
| Schema-documented export fields | 100% of required bundle |

## Open decisions

1. **GUI:** ship as optional extra (`pip install projectscanner[gui]`) or defer to v0.2?
2. **Archive:** delete `archive/untracked_overlay_20260505/` after parity check, or keep as git tag only?
3. **CLI name:** `projectscanner` (package) vs keep `python main.py` shim for one release cycle?

Default recommendation: optional GUI extra; archive moves to release tag not working tree; `projectscanner` CLI with `main.py` thin shim deprecated in README.
