# ProjectScanner Next Up

Last synchronized: 2026-09-09
SSOT: `MASTER_TASK_LIST.md`

## Immediate queue

1. `PSC-INTEL-001 | P0 | READY` — Consolidate ProjectScanner outputs into the canonical artifact hierarchy and one-way ownership/derivation contract.
2. `PSC-BRANCH-001 | P0 | BLOCKED` — Extend `repo_analysis.json` with branch evidence and FAST_PATH/FORENSIC_PATH/UNRESOLVED classification inputs after PSC-INTEL-001.
3. `PSC-PLAN-001 | P0 | BLOCKED` — Normalize stable repo-owned task/status/dependency/NEXT_UP authority into `planning_contract.json` after PSC-INTEL-001.
4. `PSC-PACKET-001 | P0 | BLOCKED` — Build/verify `projectscanner_intelligence_packet.v1` after branch + planning normalization.
5. `PSC-CONSUMER-001 | P0 | BLOCKED` — Verify ChatGPT/RAG/portfolio outputs derive from the canonical packet.

## Guardrails

- ProjectScanner generates normalized evidence; DreamVault owns governance/ranking; DreamOS/CPC owns authorized mutation.
- Do not restore removed scanner/GUI implementations as parallel engines.
- Do not treat `cleanup_recommendations.json`, legacy ChatGPT exports, generated queues, or historical prose as canonical planning authority.
- `UNRESOLVED` branch evidence is fail-closed and cannot support deletion.
- Deferred snapshot/RAG/legacy/CI work remains HOLD until the canonical intelligence hierarchy is established.
