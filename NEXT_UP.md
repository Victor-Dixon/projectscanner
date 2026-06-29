# NEXT_UP — Post-productization (Phase 5)

**Active lane:** v0.1 release prep  
**Regression gate:** `pytest -q`

## Completed (Phases 1–4)

- [x] Unified `projectscanner` CLI (`scan`, `export`, `ingest`, `history`, `gui`)
- [x] `pip install -e .` + console script
- [x] `main.py` deprecated shim (no default GUI)
- [x] Root cleanup: removed one-off fix scripts; moved `scan_targets`/`github_sources` to `scripts/`
- [x] `schema_version` in `analysis.json`
- [x] Ingest validation with clear errors
- [x] `projectscanner history` query helper
- [x] CLI + contract tests

## Remaining for v0.1 tag (Phase 5)

- [ ] Stakeholder sign-off on GUI deferral
- [ ] Execute archive removal policy (`archive/untracked_overlay_20260505/` → git tag only)
- [ ] Tag `v0.1.0` with changelog
- [ ] DreamVault portfolio README sync

## Optional v0.2 candidates

- Scanner preset unification (`quick`, `standard`, `full`)
- Working GUI module (restore or rewrite `enhanced_gui`)
- Dedicated ingest/history query report utilities

## Verification gate (current)

```bash
pip install -e ".[dev]"
projectscanner scan ./src --output /tmp/ps-out
test -f /tmp/ps-out/analysis.json
pytest -q
```
