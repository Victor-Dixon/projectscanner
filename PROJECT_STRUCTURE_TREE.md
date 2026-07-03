# ProjectScanner Structure Tree

Last synchronized: 2026-07-03

This is a high-level map of the current repository. It intentionally avoids generated/runtime-only files.

```text
.
├── .github/
│   ├── profile/
│   └── workflows/
│       ├── agent-enforcer.yml
│       └── scanner-snapshot.yml
├── archive/
│   └── untracked_overlay_20260505/       # archived scanner overlay experiment
├── config/
├── docs/
│   ├── CODEBASE_OVERVIEW.md
│   ├── CURRENT_STATE_ASSESSMENT.md
│   ├── DOMAIN_MODEL.md
│   ├── REPOSITORY_AUDIT.md
│   ├── USING_UPDATED_SCANNER.md
│   ├── guides/
│   ├── strategic/
│   └── template-agent-repo/
├── scripts/
│   ├── __init__.py
│   └── export_project_intelligence.py
├── src/
│   ├── core/
│   │   ├── analysis/
│   │   ├── model/
│   │   ├── pipeline/
│   │   ├── projectscanner/              # canonical scanner source
│   │   └── rules/
│   ├── deployment/
│   ├── gui/                             # GUI surface; currently incomplete
│   ├── quality/
│   ├── scanners/
│   └── utils/
├── tests/
│   └── unit/
├── AGENTS.md
├── CONSOLIDATION_MANIFEST.md
├── MASTER_TASK_LIST.md
├── MASTER_TASK_LOG.md
├── NEXT_UP.md
├── PRD.md
├── PRODUCTION_READINESS.md
├── README.md
├── ROADMAP.md
├── TASK_LIST.md                         # historical pointer
├── github_sources.py
├── ingest_snapshot.py
├── main.py
├── project_artifact_standards.py
├── pyproject.toml
├── pytest.ini
├── run.py
└── scan_targets.py
```

## Current documentation authority

- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Requirements: `PRD.md`
- Roadmap: `ROADMAP.md`
- Active next work: `NEXT_UP.md`

## Current next work

Stabilize the snapshot artifact contract between CI scanner output and `ingest_snapshot.py`.
