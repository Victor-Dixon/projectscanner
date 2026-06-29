# projectscanner — Master Task List

## Status

Productization Phase 0 complete (definition docs). Engine baseline seeded after dirty zero-score cleanup; regression gate `pytest -q` green.

## Active decision

**Productize** — keep as Dream.OS toolbelt scanner; shrink repo surface area while scanning arbitrarily large portfolios.

Canonical scanner source: `src/core/projectscanner/`  
Archived overlay (pending removal): `archive/untracked_overlay_20260505/`

---

## Productization track

### Phase 0 — Definition ✅
- [x] PRD with scope, file budget, boundaries
- [x] ROADMAP with phased delivery
- [x] PRODUCTION_READINESS honest checklist
- [x] NEXT_UP for Phase 1 implementation slice

### Phase 1 — Surgical amputation ✅
- [x] Unified `projectscanner` CLI (`scan`, `export`, `ingest`, `history`, `gui`)
- [x] `pyproject.toml` console script + `pip install -e .`
- [x] Deprecate fragmented entry points (`main.py` shim only)
- [x] Quarantine broken GUI imports behind `[gui]` extra
- [x] Root script cleanup (removed fix scripts; moved targets to `scripts/`)

### Phase 2 — Packaging ✅
- [x] Optional dependency groups `[gui]`, `[dev]`
- [x] README quick start (install → scan → export → verify)
- [x] Remove `sys.path` hacks from canonical entry (`projectscanner` CLI)

### Phase 3 — Output contracts ✅
- [x] `schema_version` in `analysis.json`
- [x] Ingest validation with clear errors on malformed payloads
- [x] History query ergonomics (`projectscanner history`)

### Phase 4 — CI confidence depth ✅
- [x] CLI contract tests
- [x] Ingest malformed fixture tests
- [x] CI workflow uses `projectscanner scan`

### Phase 5 — v0.1 release
- [ ] Tag `v0.1.0` with changelog
- [ ] Execute archive removal policy
- [ ] DreamVault portfolio README sync

---

## DreamPlan alignment

### Runtime governance
- [ ] Register active lanes in DreamVault dreamboard before major work
- [ ] Use `dreamrun` for operator-visible terminal execution when available
- [ ] Keep repo work scoped to declared lane ownership
- [ ] Record blockers, salvage candidates, and promotion ideas with `dreamboard add`

### Cleanup / stability
- [ ] Remove generated caches before committing
- [ ] Keep repo status clean after each lane
- [ ] Preserve unique implementation ideas before retirement or merge
- [ ] Avoid modifying unrelated paths in the same commit

### Operating step
- [x] Review repo purpose: **productize** (toolbelt scanner for portfolio intelligence)

---

## Regression gate

```bash
pytest -q
```
