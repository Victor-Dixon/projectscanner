# ProjectScanner Next Up

Last synchronized: 2026-09-09

## Purpose

Immediate executable/dependency queue only. `MASTER_TASK_LIST.md` owns stable task identity and strategic inventory.

## Immediate actions

1. `PSC-INTEL-001 | P0 | READY` — Consolidate the artifact pipeline around the canonical hierarchy.
   - Keep deep scan and current repo scan as distinct evidence inputs.
   - Make `planning_contract.json` the normalized repository-planning evidence surface.
   - Make `projectscanner_intelligence_packet.v1` the canonical compact operational evidence packet.
   - Keep `chatgpt_context.json` as a bounded projection, not authority.
   - Downgrade legacy context/cleanup artifacts to compatibility/advisory roles rather than peer authority.

2. `PSC-BRANCH-001 | P0 | BLOCKED` — Add branch intelligence using `FAST_PATH`, `FORENSIC_PATH`, and `UNRESOLVED`.
   - Dependency: PSC-INTEL-001.
   - Emit evidence only; DreamVault owns deletion/promotion governance.

3. `PSC-PLAN-001 | P0 | BLOCKED` — Normalize stable task IDs, status, dependencies and NEXT_UP membership from repository-owned planning.
   - Dependency: PSC-INTEL-001.
   - Fail closed on malformed/unknown planning; never invent task identity.

4. `PSC-PACKET-001 | P0 | BLOCKED` — Join deep scan + repo facts + planning evidence into the canonical intelligence packet with provenance/version checks.
   - Dependencies: PSC-INTEL-001, PSC-BRANCH-001, PSC-PLAN-001.

5. `PSC-CONSUMER-001 | P1 | BLOCKED` — Verify DreamVault/Dream.OS consumption and authority boundaries.
   - Dependency: PSC-PACKET-001.

## Exit criteria

- One documented artifact hierarchy; no ambiguous peer authority.
- Branch evidence supports FAST_PATH vs FORENSIC_PATH without authorizing mutation.
- Planning evidence preserves stable source task IDs/status/dependencies/NEXT_UP.
- DreamVault remains governance/ranking authority.
- `pytest -q` remains the implementation regression gate; planning changes alone do not claim implementation completion.
