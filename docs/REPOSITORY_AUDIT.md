# ProjectScanner Repository Audit

Last synchronized: 2026-07-03

## Audit scope

This audit covers the repository architecture, folder structure, documentation set, naming, undocumented features, and known implementation/documentation mismatches. Findings are derived from files in this repository only.

## What this project is

ProjectScanner is a repository scanning and inventory intelligence tool. It belongs to the software repository analysis domain. It solves the problem of producing machine-readable evidence about repository contents, documentation markers, scan targets, and quality signals before cleanup, consolidation, promotion, or downstream automation.

## Architecture

Current architecture is a Python package plus supporting top-level utilities.

| Layer | Paths | Notes |
| --- | --- | --- |
| Core scanner package | `src/core/projectscanner/` | Canonical scanner implementation. Wrappers should delegate here. |
| Canonical model/pipeline | `src/core/model/`, `src/core/pipeline/` | Snapshot dataclass and orchestrator exist, but some enrichment paths are incomplete. |
| Rules and quality | `src/core/rules/`, `src/quality/` | Contract rules and standalone quality checkers. |
| External repo scanning | `src/scanners/`, `github_sources.py`, `scan_targets.py` | GitHub REST/CLI inventory and scan target generation. |
| Portfolio export | `scripts/export_project_intelligence.py` | Separate filesystem/git/docs-marker export path. |
| CI/snapshot history | `.github/workflows/`, `src/utils/run_scanner.py`, `ingest_snapshot.py` | CI scan runner and SQLite ingestor; schema alignment remains incomplete. |
| GUI | `src/gui/`, `main.py` | GUI launch surface exists, but referenced enhanced GUI modules are missing. |
| Tests | `tests/` | Regression coverage for analyzer, context export, GitHub library summary, export bundles, phase handoff, GUI import expectations, and workflow text checks. |
| Archive | `archive/untracked_overlay_20260505/` | Archived scanner overlay experiment; not active source. |

## Folder structure

Authoritative high-level structure:

```text
.
├── .github/workflows/          # CI workflows
├── archive/                    # Archived overlay experiment
├── config/                     # Supporting config files
├── docs/                       # Domain, audit, usage, and historical docs
├── scripts/                    # Portfolio intelligence export script
├── src/
│   ├── core/projectscanner/    # Canonical scanner
│   ├── core/model/             # ProjectSnapshot data model
│   ├── core/pipeline/          # PipelineOrchestrator
│   ├── core/rules/             # Contract rules
│   ├── deployment/agents/      # Agent policy deployment utility
│   ├── gui/                    # GUI launch/test surfaces; incomplete
│   ├── quality/                # Quality checker CLIs
│   ├── scanners/               # GitHub library scanner
│   └── utils/                  # Scanner runner utilities
├── tests/                      # Pytest regression tests
├── github_sources.py           # GitHub CLI inventory helper
├── ingest_snapshot.py          # SQLite snapshot ingestor
├── main.py                     # Top-level CLI/GUI entry point
├── project_artifact_standards.py
├── scan_targets.py
└── run.py
```

## Existing documentation

Authoritative current documentation:

- `README.md` - repository entry point.
- `docs/DOMAIN_MODEL.md` - complete domain model.
- `docs/REPOSITORY_AUDIT.md` - this audit.
- `PRD.md` - product requirements and implementation-backed scope.
- `ROADMAP.md` - completed/current/remaining roadmap.
- `MASTER_TASK_LIST.md` - canonical task inventory.
- `MASTER_TASK_LOG.md` - chronological task log.
- `NEXT_UP.md` - active handoff.
- `AGENTS.md` - repository-specific agent instructions.
- `docs/CODEBASE_OVERVIEW.md` - implementation map.
- `docs/USING_UPDATED_SCANNER.md` - usage guide.
- `docs/CURRENT_STATE_ASSESSMENT.md` - current status snapshot.
- `CONSOLIDATION_MANIFEST.md` - project boundaries in the Dream.OS/DreamVault context.

Historical or non-authoritative documentation:

- `TASK_LIST.md` - superseded by `MASTER_TASK_LIST.md`.
- `docs/ROADMAP.md` and `docs/NEXT_UP.md` - pointers to root canonical docs.
- `docs/DARK_MODE_ENHANCEMENT.md`, `docs/ORGANIZATION_SUMMARY.md`, `docs/FINAL_ORGANIZATION_SUMMARY.md`, and `docs/validation_report.md` - historical notes, not current implementation evidence.
- `docs/strategic/AGENTS.md`, `docs/guides/AGENT_POLICY_DEPLOYMENT_GUIDE.md`, and `docs/template-agent-repo/README.md` - portfolio policy/template material, not ProjectScanner runtime documentation.

## Missing or incomplete documentation

| Gap | Current status | Required next action |
| --- | --- | --- |
| Snapshot artifact schema | Current docs now identify scanner/ingestor mismatch | Define schema and add validation tests before documenting as stable |
| GUI status | Current docs now mark GUI as incomplete/Unknown | Decide whether to restore GUI implementation or document it as unsupported |
| ContractEngine/quality usage examples | Mentioned in domain model and overview | Add focused examples after tests define expected CLI output |
| Analyzer enrichment contract | Current docs mark imports/class details mismatch | Either implement analyzer fields or remove unsupported claims from code docstrings |
| Contributor guide | No dedicated `CONTRIBUTING.md` | Optional future doc once active workflows stabilize |

## Dead or outdated documentation found

The audit found prior docs that described absent paths such as root `scanner.py`, root `gui.py`, `src/core/scanner/unified_scanner.py`, `project_scanner.py`, root `.pre-commit-config.yaml`, and `scripts/scanners/*`. Those claims are now superseded by the canonical docs listed above. Historical files are retained only as historical context and should not be used to infer current behavior.

## Naming inconsistencies found and resolved in docs

| Inconsistency | Current standard |
| --- | --- |
| `ProjectScanner`, `projectscanner`, `project-scanner`, `Project Scanner` | Use `ProjectScanner` for product/tool name and `projectscanner` for package/repository id. |
| `PRODUCT_REQUIREMENTS_DOCUMENT.md` vs `PRD.md` | Use `PRD.md`. |
| Multiple active roadmaps/task lists | Use root `ROADMAP.md`, `MASTER_TASK_LIST.md`, and `NEXT_UP.md` as canonical. |
| `src/core/scanner/` or root `scanner.py` | Use `src/core/projectscanner/`. |
| `scripts/loc_checker.py` / `scripts/complexity_checker.py` | Use `src/quality/loc_checker.py` and `src/quality/complexity_checker.py`. |
| GUI described as working | Current docs mark GUI implementation as incomplete unless missing modules are restored. |

## Features that were undocumented or underdocumented

- Bare Git repository metadata export.
- Context chunk export modes: `directory`, `language`, and `none`.
- `ScanTarget` manifests and GitHub clone/fetch planning.
- Artifact standard checks for `scan_target.json`, `analysis.json`, `context.json`, `next_up.json`, and `health.json`.
- SQLite snapshot ingestion and its current schema assumptions.
- Standalone portfolio intelligence export under `scripts/export_project_intelligence.py`.
- Contract rules under `src/core/rules/`.

## Documentation that no longer matched implementation

- Older codebase overview described `project_scanner.py`, `project-scanner/`, root `gui.py`, and tree-sitter parser behavior. The current overview has been rewritten.
- Historical GUI and dark mode docs claimed working enhanced GUI behavior that cannot be validated from current files.
- Previous task list proposed a new unified scanner path that is explicitly disallowed by current SSOT tests.
- Previous structure tree listed files and directories that no longer exist. It has been replaced with a high-level current tree.
- Previous validation report claimed three passing tests and an old CLI command; current verification uses `pytest -q`.

## Feature-to-domain coverage

Every major feature now maps to a domain area in `docs/DOMAIN_MODEL.md`:

- Core scanning and reports -> core scanning/report generation.
- Context export -> report generation/LLM context export.
- GitHub repo scanning and target manifests -> GitHub inventory.
- Portfolio intelligence bundles -> portfolio export.
- Snapshot workflow and SQLite ingestion -> CI snapshots/history.
- Contract rules and quality checkers -> quality/contracts.
- GUI -> GUI subdomain, status incomplete/Unknown.

## Completed synchronization work

- Created a complete implementation-backed domain model.
- Created this repository audit.
- Replaced placeholder lifecycle docs with current content.
- Marked Unknowns instead of guessing implementation intent.
- Standardized active documentation around `ProjectScanner`, `projectscanner`, and `src/core/projectscanner/`.
- Converted duplicate/stale docs into pointers or historical notes where appropriate.

## Remaining work

- Implement and test snapshot schema validation.
- Resolve scanner output versus ingestor schema mismatch.
- Decide and document the GUI support status after code changes.
- Add targeted tests for currently untested stable tooling.
- Keep generated or historical docs clearly labeled if they are retained.

## Next recommended work

Follow `NEXT_UP.md`: stabilize the snapshot artifact contract between CI scanner output and SQLite ingestion with tests first.
