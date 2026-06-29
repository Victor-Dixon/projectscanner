# NEXT_UP — Productization Phase 1

**Active lane:** Productize ProjectScanner (Phase 1 — surgical amputation)  
**Blocked on:** None — Phase 0 definition docs landed in this PR  
**Regression gate:** `pytest -q`

## Why now

15,000 files in a portfolio is a governance problem. ~130 files in this repo with five entry points and stub docs is a **product** problem. The scanner engine works; the packaging does not. Phase 1 makes the repo look like the tool we want operators to trust.

## This slice (next PR)

### 1. Unified CLI skeleton

Create `src/projectscanner_cli.py` or package `cli.py` at install root with subcommands:

```
projectscanner scan <path> [--output DIR] [--export-context] [--generate-init]
projectscanner export --projects-root DIR --out-root DIR
projectscanner ingest <snapshot-dir> [--db PATH]
```

Delegate to existing implementations:

- `scan` → `core.projectscanner.ProjectScanner`
- `export` → `scripts/export_project_intelligence.py` logic (import, don't subprocess)
- `ingest` → `ingest_snapshot.py` logic

Wire in `pyproject.toml`:

```toml
[project.scripts]
projectscanner = "projectscanner.cli:main"
```

### 2. Thin `main.py` shim (one release cycle)

```python
# Deprecation notice + forward to projectscanner.cli:main
```

Update README quick start to use `projectscanner`, not `python main.py`.

### 3. Quarantine broken GUI paths

- Remove default-to-GUI behavior when no args (prints help instead)
- Move GUI behind `projectscanner gui` or `pip install projectscanner[gui]`
- Wire to `src/gui/demo_gui.py` if PyQt5 available; fail with clear message if not

### 4. Root cleanup (no behavior change)

| Action | Files |
|---|---|
| Move to `scripts/` | `ingest_snapshot.py`, `scan_targets.py`, `github_sources.py` |
| Delete (history only) | `final_comment_fix.py`, `mark_long_functions.py`, `show_long_functions.py` |
| Keep at root | `main.py` (shim), `README.md`, `pyproject.toml`, `pytest.ini`, `LICENSE` |

Target: root `.py` count ≤ 4 after this slice.

## Tests to add in same PR

- CLI `--help` smoke for each subcommand
- `scan ./src` integration writes `analysis.json`
- No import of `enhanced_gui` from default code paths

## Explicitly out of scope

- Scanner engine rewrite / unified_scanner.py (see TASK_LIST.md — defer)
- Deleting `archive/` (needs parity checklist — Phase 5)
- GUI feature work beyond quarantine
- `schema_version` field (Phase 3)

## Verification before merge

```bash
pip install -e ".[dev]"
projectscanner --help
projectscanner scan ./src --output /tmp/ps-test
pytest -q
```

## After this slice

1. Phase 3: add `schema_version` to `analysis.json`
2. Phase 4: ingest malformed fixture tests
3. Phase 5: tag `v0.1.0`
