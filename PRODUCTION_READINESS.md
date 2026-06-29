# ProjectScanner — Production Readiness Checklist

Updated after Phases 1–4 productization implementation.

**Legend:** ✅ ready · ⚠️ partial · ❌ not ready

## Product identity

| Item | Status | Notes |
|---|---|---|
| Clear one-line purpose | ✅ | Repo intelligence for Dream.OS portfolios |
| Canonical boundaries documented | ✅ | `CONSOLIDATION_MANIFEST.md`, `docs/repo_role_20260613.md` |
| Non-goals explicit | ✅ | See `PRD.md` |
| File budget defined | ✅ | ≤120 tracked files for v0.1 |

## Install and run

| Item | Status | Notes |
|---|---|---|
| `pip install -e .` works | ✅ | Console script `projectscanner` installed |
| Documented quick start | ✅ | README quick start section |
| Single canonical CLI | ✅ | `projectscanner scan|export|ingest|history|gui` |
| No `sys.path` hacks required | ✅ | Installed package imports from `src/` |
| GUI optional and working | ⚠️ | Quarantined behind `[gui]` extra; `enhanced_gui` still missing |

## Core functionality

| Item | Status | Notes |
|---|---|---|
| Directory scan + analysis | ✅ | `ProjectScanner` in `src/core/projectscanner/` |
| Incremental cache | ✅ | `file_processor.py` |
| Multi-language parse | ✅ | Python AST; optional tree-sitter paths |
| Report generation | ✅ | `report_generator.py` + `analysis.json` contract |
| Portfolio export | ✅ | `projectscanner export` |
| GitHub library scan | ✅ | `src/scanners/github_library_scanner.py` |
| Quality rules engine | ✅ | `src/core/rules/` |

## Data contracts

| Item | Status | Notes |
|---|---|---|
| `analysis.json` schema documented | ⚠️ | `snapshot_contract.py` is SSOT; formal doc pending |
| `schema_version` field | ✅ | Emitted as `1.0` |
| Ingest schema validation | ✅ | `SnapshotValidationError` on malformed payloads |
| Export bundle contract tested | ✅ | `tests/test_export_project_intelligence.py` |
| Output never committed to product repo | ✅ | `.gitignore` + policy in PRD |

## Testing and CI

| Item | Status | Notes |
|---|---|---|
| Unit/integration tests | ✅ | 24 passed, 2 skipped |
| Regression gate documented | ✅ | `pytest -q` in README, AGENTS.md |
| CI snapshot workflow | ✅ | Uses `projectscanner scan` |
| CI tests on PR | ⚠️ | `agent-enforcer.yml` present; depth varies |
| Contract regression tests | ✅ | `tests/test_cli.py`, `tests/test_snapshot_contract.py` |

## Repository hygiene

| Item | Status | Notes |
|---|---|---|
| Root directory lean | ✅ | One-off fix scripts removed; 3 root `.py` shims |
| No duplicate scanner implementations in tree | ⚠️ | `archive/untracked_overlay_20260505/` still present |
| Strategic docs real (not stubs) | ✅ | PRD, ROADMAP, NEXT_UP, this file |
| Archive policy executed | ❌ | Overlay still in working tree (Phase 5) |
| Dead import paths | ✅ | `main.py` forwards to CLI; no missing default imports |

## Security and operations

| Item | Status | Notes |
|---|---|---|
| No secrets in repo | ✅ | |
| Safe defaults for scan ignore | ✅ | venv, `node_modules`, `.git` skipped |
| Subprocess usage reviewed | ⚠️ | Export shells git for repo metadata |
| Dependency pinning | ⚠️ | Optional groups in `pyproject.toml` |

## DreamVault integration

| Item | Status | Notes |
|---|---|---|
| Documented output path | ✅ | README + `docs/repo_role_20260613.md` |
| Machine-readable cleanup recommendations | ✅ | Export bundle contract |
| Portfolio README block | ✅ | Auto-generated section in README |

## Release readiness score

| Area | Weight | Score |
|---|---:|---:|
| Core scan engine | 25% | 90% |
| Packaging / CLI | 20% | 90% |
| Contracts / ingest | 20% | 85% |
| Tests / CI | 20% | 80% |
| Repo hygiene | 15% | 70% |
| **Weighted total** | | **~84%** |

**Verdict:** Ready for **v0.1 beta tag** after archive policy decision. Safe for internal Dream.OS toolbelt use today.

## Gate before tagging v0.1

```bash
pip install -e ".[dev]"
projectscanner scan ./src --output /tmp/ps-out
test -f /tmp/ps-out/analysis.json
pytest -q
```
