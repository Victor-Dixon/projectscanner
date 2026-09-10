# ProjectScanner Master Task List

Last synchronized: 2026-09-09

## Purpose

ProjectScanner is the repository-intelligence producer for Dream.OS. It scans source/runtime/git facts and emits normalized evidence. It does not rank portfolio work, own DreamVault governance, or perform branch deletion.

Only stable `PSC-*` rows below are executable planning inventory. Historical prose/backlog remains available through git history and reports but cannot be autonomously assigned.

Statuses: `READY`, `ACTIVE`, `BLOCKED`, `HOLD`, `COMPLETE`.

## Canonical artifact hierarchy

```text
raw repository
   |-- deep source scan ------> project_analysis_<repo>.json
   |-- runtime/git scan -----> repo_analysis.json
                                  |
                                  v
                         planning_contract.json
                                  |
                                  v
              projectscanner_intelligence_packet.v1
                       /                    \
                      v                      v
            chatgpt_context.json       portfolio_index.json
                      |
                      v
                    RAG
```

- `project_analysis_<repo>.json`: deep codebase evidence.
- `repo_analysis.json`: current repository/runtime/git/branch facts.
- `planning_contract.json`: normalized repo-owned planning authority, including stable IDs/status/dependencies/NEXT_UP membership; ProjectScanner does not invent tasks.
- `projectscanner_intelligence_packet.v1`: canonical operational evidence packet.
- `chatgpt_context.json`: compact AI handoff derived from the packet.
- RAG JSONL: searchable/indexable representation.
- `portfolio_index.json`: fleet-level summary.
- legacy `chatgpt_project_context_<repo>.json`: compatibility/deep-analysis context, not canonical operational authority.
- `cleanup_recommendations.json`: legacy/advisory output to absorb into normalized evidence rather than maintain as a competing authority.

## Canonical execution lanes

- [ ] PSC-INTEL-001 | P0 | READY | Consolidate current overlapping ProjectScanner outputs into the canonical hierarchy above and define one-way derivation/ownership rules.
- [ ] PSC-BRANCH-001 | P0 | BLOCKED | Extend `repo_analysis.json` with normalized branch intelligence and `FAST_PATH` / `FORENSIC_PATH` / `UNRESOLVED` evidence; depends on PSC-INTEL-001.
- [ ] PSC-PLAN-001 | P0 | BLOCKED | Normalize repository planning into `planning_contract.json` without task invention; depends on PSC-INTEL-001.
- [ ] PSC-PACKET-001 | P0 | BLOCKED | Build/verify `projectscanner_intelligence_packet.v1` from deep scan + repo analysis + planning contract; depends on PSC-BRANCH-001 and PSC-PLAN-001.
- [ ] PSC-CONSUMER-001 | P0 | BLOCKED | Verify compact ChatGPT/RAG/portfolio consumers derive from the packet without creating competing truth; depends on PSC-PACKET-001.

## Deferred verification lanes

These are deliberately HOLD, not competing NEXT_UP work. Promote only after the P0 hierarchy is established and evidence shows the capability remains necessary.

- [ ] PSC-SNAPSHOT-001 | P1 | HOLD | Snapshot/ingestion contract verification.
- [ ] PSC-RAG-001 | P1 | HOLD | RAG corpus provenance/determinism verification.
- [ ] PSC-LEGACY-001 | P2 | HOLD | Removed GUI/legacy documentation reconciliation.
- [ ] PSC-CI-001 | P1 | HOLD | Broader CLI/report/CI regression verification.

## Branch evidence contract

`repo_analysis.json` must represent enough evidence for downstream DreamVault policy without deciding disposition itself:

- branch name and exact head SHA;
- canonical head and merge base;
- ahead/behind or equivalent ancestry evidence;
- containment state;
- open PR identity/state;
- unique commits/files or normalized capability summary;
- production/runtime evidence when known;
- `classification_path`: `FAST_PATH`, `FORENSIC_PATH`, or `UNRESOLVED`;
- proposed/evidence disposition and references;
- deletion eligibility evidence (never inferred from age alone).

`UNRESOLVED` is fail-closed. DreamVault owns governance/disposition; DreamOS/CPC performs authorized mutation.

## Planning representation contract

For repositories with canonical planning, ProjectScanner should preserve and normalize:

- stable task ID;
- priority;
- status;
- dependencies;
- NEXT_UP membership/order;
- source path/ref/SHA;
- freshness/validation state.

It must not convert historical prose, completed logs, generated queues, or stale architecture notes into executable work.

## Completion gate

ProjectScanner is planning-standardized when the canonical hierarchy is implemented/verified, branch evidence can drive DreamVault FAST/FORENSIC classification without rescanning by hand, planning normalization preserves repo authority without invention, downstream compact outputs derive from the intelligence packet, and NEXT_UP contains five or fewer stable tasks.
