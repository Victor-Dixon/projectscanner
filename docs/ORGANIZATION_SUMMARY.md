# Historical Note: Project Organization Summary

Last synchronized: 2026-07-03

This document is historical and not authoritative for the current ProjectScanner layout.

## Current project

ProjectScanner is repository scanning and inventory intelligence tooling. The canonical scanner source is `src/core/projectscanner/`.

## Why this file is historical

The previous organization summary described paths that are absent or no longer authoritative, including root `scanner.py`, root `gui.py`, `src/core/scanner/`, and several setup/GUI launcher locations. Those claims are superseded by current repository documentation.

## Current authoritative references

- Structure tree: `PROJECT_STRUCTURE_TREE.md`
- Codebase overview: `docs/CODEBASE_OVERVIEW.md`
- Domain model: `docs/DOMAIN_MODEL.md`
- Repository audit: `docs/REPOSITORY_AUDIT.md`
- Active next work: `NEXT_UP.md`

## Current next work

Stabilize the snapshot artifact contract between CI scanner output and `ingest_snapshot.py`.