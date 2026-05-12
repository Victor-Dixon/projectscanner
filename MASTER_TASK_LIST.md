# projectscanner 

Baseline Dream.OS project artifact.

## Status

Seeded after dirty zero-score cleanup and full regression pass.

## Notes

- Canonical scanner source remains under src/core/projectscanner/.
- Overlay scanner experiment is archived under archive/untracked_overlay_20260505/.
- Current regression gate: pytest -q.

---

## DreamPlan Alignment

### Runtime Governance
- [ ] Register active lanes in DreamVault dreamboard before starting major work.
- [ ] Use `dreamrun` for operator-visible terminal execution when available.
- [ ] Keep repo work scoped to declared lane ownership.
- [ ] Record blockers, salvage candidates, and promotion ideas with `dreamboard add`.

### Cleanup / Stability
- [ ] Remove generated caches before committing.
- [ ] Keep repo status clean after each lane.
- [ ] Preserve unique implementation ideas before retirement or merge.
- [ ] Avoid modifying unrelated paths in the same commit.

### Next Operating Step
- [ ] Review this repo’s active purpose: keep, productize, salvage, or retire.
