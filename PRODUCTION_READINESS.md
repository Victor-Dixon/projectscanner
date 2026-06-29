# ProjectScanner — Production Readiness Checklist

Honest assessment for productization. Updated as part of the Phase 0 product definition pass.

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
| `pip install -e .` works | ⚠️ | `pyproject.toml` exists but no console script or package discovery |
| Documented quick start | ⚠️ | README covers export; install path incomplete |
| Single canonical CLI | ❌ | `main.py`, `run.py`, `src/core/projectscanner/cli.py`, GUI launchers |
| No `sys.path` hacks required | ❌ | `main.py` inserts `src` manually |
| GUI optional and working | ❌ | `enhanced_gui` and analysis modules missing |

## Core functionality

| Item | Status | Notes |
|---|---|---|
| Directory scan + analysis | ✅ | `ProjectScanner` in `src/core/projectscanner/` |
| Incremental cache | ✅ | `file_processor.py` |
| Multi-language parse | ✅ | Python AST; optional tree-sitter paths |
| Report generation | ✅ | `report_generator.py` |
| Portfolio export | ✅ | `scripts/export_project_intelligence.py` |
| GitHub library scan | ✅ | `src/scanners/github_library_scanner.py` |
| Quality rules engine | ✅ | `src/core/rules/` |

## Data contracts

| Item | Status | Notes |
|---|---|---|
| `analysis.json` schema documented | ❌ | Implicit in code only |
| `schema_version` field | ❌ | Not emitted today |
| Ingest schema validation | ❌ | `ingest_snapshot.py` assumes shape; fails silently on drift |
| Export bundle contract tested | ⚠️ | `tests/test_export_project_intelligence.py` exists |
| Output never committed to product repo | ✅ | `.gitignore` + policy in PRD |

## Testing and CI

| Item | Status | Notes |
|---|---|---|
| Unit/integration tests | ✅ | 19 passed, 1 skipped |
| Regression gate documented | ✅ | `pytest -q` in README, AGENTS.md |
| CI snapshot workflow | ✅ | `.github/workflows/scanner-snapshot.yml` |
| CI tests on PR | ⚠️ | `agent-enforcer.yml` present; depth varies |
| Contract regression tests | ❌ | Ingest malformed payload cases not covered |

## Repository hygiene

| Item | Status | Notes |
|---|---|---|
| Root directory lean | ❌ | One-off fix scripts, duplicate launchers |
| No duplicate scanner implementations in tree | ❌ | `archive/untracked_overlay_20260505/` mirrors core |
| Strategic docs real (not stubs) | ✅ | PRD, ROADMAP, NEXT_UP, this file |
| Archive policy executed | ❌ | Overlay still in working tree |
| Dead import paths | ❌ | `main.py` → missing `enhanced_gui`, `analyze_portfolio`, `strategic_plan` |

## Security and operations

| Item | Status | Notes |
|---|---|---|
| No secrets in repo | ✅ | |
| Safe defaults for scan ignore | ✅ | venv, `node_modules`, `.git` skipped |
| Subprocess usage reviewed | ⚠️ | `export_project_intelligence.py` shells git |
| Dependency pinning | ⚠️ | `requirements.txt` present; not in pyproject optional groups |

## DreamVault integration

| Item | Status | Notes |
|---|---|---|
| Documented output path | ✅ | README + `docs/repo_role_20260613.md` |
| Machine-readable cleanup recommendations | ✅ | Export script contract |
| Portfolio README block | ✅ | Auto-generated section in README |

## Release readiness score

| Area | Weight | Score |
|---|---:|---:|
| Core scan engine | 25% | 90% |
| Packaging / CLI | 20% | 25% |
| Contracts / ingest | 20% | 40% |
| Tests / CI | 20% | 65% |
| Repo hygiene | 15% | 35% |
| **Weighted total** | | **~55%** |

**Verdict:** Engine is production-capable; **product packaging is not**. Safe for internal Dream.OS toolbelt use. Not ready for external operators until Phase 1–2 complete.

## Blockers for v0.1 (must fix)

1. Single CLI entry with working imports
2. `pip install -e .` + console script
3. Remove or fix broken GUI/default `main.py` paths
4. `schema_version` on scanner output
5. Root clutter reduction per file budget

## Recommended gate before tagging v0.1

```bash
pip install -e ".[dev]"
projectscanner scan ./src --output /tmp/ps-out
test -f /tmp/ps-out/analysis.json
pytest -q
```

All four commands must succeed on a clean clone.
