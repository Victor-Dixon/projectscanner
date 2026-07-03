# ProjectScanner Production Readiness

Last synchronized: 2026-07-03

## Project

ProjectScanner is repository scanning and inventory intelligence tooling for local and GitHub projects. It belongs to the software repository analysis domain.

## Current readiness summary

ProjectScanner has a working core local scanner/report/context path, but the repository should not be described as production-ready as a fully integrated scanner platform. Several integration seams remain incomplete and are documented as Unknown or partial.

## Ready surfaces

- Local project scanning through `ProjectScanner`.
- Lightweight language analysis for Python, JS/TS, and Rust.
- JSON report generation.
- ChatGPT context export and chunking.
- Bare Git repository metadata export.
- Portfolio docs-marker export.
- GitHub inventory/scan target helper modules.
- Contract and quality checker tooling as standalone utilities.

## Not ready / incomplete surfaces

- Enhanced GUI launch path; missing referenced modules.
- Stable scanner-to-ingestor snapshot schema.
- SQLite ingestion validation.
- Dependency graph output as a complete feature.
- Agent categorization on current analyzer output.
- Pipeline analyze/quality enrichment.

## Current verification gate

```bash
pytest -q
```

## Production-readiness requirements before stronger claims

- [ ] Snapshot schema is documented and validated.
- [ ] CI scanner output and SQLite ingestion are aligned.
- [ ] Ingestion has tests for malformed inputs and idempotency.
- [ ] GUI status is resolved and documented.
- [ ] Dependency graph and agent categorization are either implemented with tests or removed from supported-feature docs.
- [ ] Stable utility surfaces have tests.

## What remains

See `MASTER_TASK_LIST.md` for the canonical backlog and `NEXT_UP.md` for the immediate next work.
