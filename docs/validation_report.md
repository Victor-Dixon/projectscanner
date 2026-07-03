# Validation Report

Last synchronized: 2026-07-03

## Project

ProjectScanner is repository scanning and inventory intelligence tooling in the software repository analysis domain.

## Current validation result

Command run during this documentation synchronization:

```bash
python3 -m pytest -q
```

Result:

```text
14 passed, 1 skipped, 1 warning
```

## Why this file is historical

Previous contents referenced `project_scanner.py`, an old output filename, and an old test count. Those details are superseded by this report and by the current docs:

- `README.md`
- `docs/DOMAIN_MODEL.md`
- `docs/REPOSITORY_AUDIT.md`
- `MASTER_TASK_LOG.md`

## Standard validation gate

The repository-level regression gate remains:

```bash
pytest -q
```

## Current next work

Stabilize the snapshot artifact contract between CI scanner output and `ingest_snapshot.py`.
