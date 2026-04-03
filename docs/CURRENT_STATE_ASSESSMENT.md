# Current State Assessment (No-BS)

## What we have right now

### 1) Entrypoints are fragmented and inconsistent
- `main.py` is the top-level entrypoint and offers GUI/scan/analyze/strategic modes, but it imports modules that are not present (for example `src.core.scanner.unified_scanner` and `scripts.scanners.quick_scanner`).
- `src/core/projectscanner/cli.py` is a second CLI path that imports `ProjectScanner` from `core.projectscanner.scanner`, but `scanner.py` is not present in that package.

### 2) A partial package exists, but key modules are missing
- Existing modules in `src/core/projectscanner/` are:
  - `__init__.py`
  - `bots.py`
  - `cli.py`
  - `file_processor.py`
  - `report_generator.py`
- `__init__.py` exports `ProjectScanner` and `LanguageAnalyzer`, but both are imported from files that do not exist (`scanner.py`, `language_analyzer.py`).

### 3) Scanning support code is already somewhat modular
You already have reusable building blocks:
- File hashing/exclusion/cache touchpoints in `FileProcessor`.
- Thread worker management in `bots.py`.
- Report/context writing in `ReportGenerator`.

This means the project is **not** a pure single-file scanner anymore; it is a **partially extracted package missing the orchestration core**.

### 4) GitHub library scanner exists and depends on missing core scanner
- `src/scanners/github_library_scanner.py` orchestrates clone + scan + summary behavior.
- It imports `core.projectscanner.scanner.ProjectScanner` (missing), so this currently fails as soon as imports are resolved.

### 5) Tests confirm package contract exists but implementation is incomplete
- `tests/test_analyzer.py` expects:
  - `LanguageAnalyzer`
  - `ProjectScanner`
  - scanner methods like `_maturity_level`, `_agent_type`, `scan_project`, context export.
- Current `pytest` run fails during collection with `ModuleNotFoundError` for `core.projectscanner.scanner`.

## Straight answer: do we need to restructure for your proposed package split?

**Yes — but this should be framed as a completion + cleanup restructure, not a from-scratch rewrite.**

You already have a package shell and some extracted responsibilities. The immediate problem is:
1. Missing SSOT scanner core modules.
2. Conflicting/obsolete entrypoints.
3. Imports and tests targeting interfaces that are currently absent.

## Practical migration path (minimum disruption)

1. **Stabilize SSOT package path first**
   - Keep `src/core/projectscanner/` as SSOT for scanner engine internals.
   - Add missing `scanner.py` and `language_analyzer.py` there first to restore current test/API contract.

2. **Then align module boundaries to your target design**
   - Keep thin CLI wrapper.
   - Move internals into submodules (`analyzers/`, `cache/`, `git/`, `reports/`) once behavior parity exists.

3. **Unify entrypoints after core is stable**
   - Decide one canonical runtime path (`python -m ...` or `main.py` wrapper).
   - Make all other launchers call that one path only.

4. **Batch wrapper should stay orchestration-only**
   - Wrapper loops over targets and aggregates output.
   - Scanner package remains reusable engine.

## Decision

- If you want fast progress with minimal risk: **restructure now**, but in phases.
- Do **not** build another parallel scanner script.
- Do **not** rewrite everything before restoring missing core modules.


## Next up

- Handoff plan and Phase 2 checklist: `docs/NEXT_UP.md`.
- Operational usage + SSOT guardrails: `docs/USING_UPDATED_SCANNER.md`.
