# ProjectScanner Master Task List

Last synchronized: 2026-09-09

## Purpose

ProjectScanner is the canonical repository evidence generator for Dream.OS portfolio intelligence. It answers what is in a repository and what its observable repository/planning state is. It does not rank portfolio work, grant execution authority, or make destructive governance decisions.

Completed history belongs in `MASTER_TASK_LOG.md`; no more than five immediate actions belong in `NEXT_UP.md`.

Every executable lane MUST have a stable `PSC-*` task ID. Prose domains below are non-executable context until normalized.

## Canonical artifact hierarchy

```text
repository source
   |-- deep source scan -> project_analysis_<repo>.json
   |-- runtime/git scan -> repo_analysis.json
   +---------------------------+
                               v
                    planning_contract.json
                               v
             projectscanner_intelligence_packet.v1
                               v
                     chatgpt_context.json
                        /              \
                       v                v
                  RAG index       portfolio_index.json
```

Artifact responsibilities:

- `project_analysis_<repo>.json`: deep code/content evidence.
- `repo_analysis.json`: current repository/runtime/git/branch facts.
- `planning_contract.json`: normalized repository-owned task/NEXT_UP evidence; never portfolio ranking authority.
- `projectscanner_intelligence_packet.v1`: compact normalized operational evidence joining deep + current facts.
- `chatgpt_context.json`: bounded AI handoff projection, not authority.
- RAG: retrieval/index layer.
- `portfolio_index.json`: fleet summary, not task-selection authority.
- legacy `chatgpt_project_context_<repo>.json`: compatibility/deep-analysis export; not canonical operational handoff.
- `cleanup_recommendations.json`: advisory only; absorb into normalized evidence over time rather than treat as peer authority.

## Canonical task ledger

- [ ] PSC-INTEL-001 | P0 | READY | Consolidate artifact production around the canonical hierarchy above and eliminate peer-authority ambiguity.
- [ ] PSC-BRANCH-001 | P0 | BLOCKED | Add normalized branch intelligence with FAST_PATH/FORENSIC_PATH evidence fields to `repo_analysis.json` and the intelligence packet | depends on PSC-INTEL-001.
- [ ] PSC-PLAN-001 | P0 | BLOCKED | Normalize stable task IDs/status/dependencies/NEXT_UP evidence into `planning_contract.json` without inventing tasks | depends on PSC-INTEL-001.
- [ ] PSC-PACKET-001 | P0 | BLOCKED | Make the intelligence packet join deep scan + repo facts + planning contract with provenance/version checks | depends on PSC-INTEL-001, PSC-BRANCH-001, PSC-PLAN-001.
- [ ] PSC-CONSUMER-001 | P1 | BLOCKED | Verify DreamVault/Dream.OS consumers against the canonical packet and fail closed on schema/authority drift | depends on PSC-PACKET-001.
- [ ] PSC-SNAPSHOT-001 | P1 | HOLD | Stabilize snapshot directory/ingestion contract and validate metadata/analysis before writes.
- [ ] PSC-RAG-001 | P1 | HOLD | Verify normalized RAG export provenance/determinism against current Dream.OS retrieval needs.
- [ ] PSC-LEGACY-001 | P2 | HOLD | Reconcile removed GUI/legacy scanner references without restoring parallel engines.
- [ ] PSC-CI-001 | P1 | HOLD | Map canonical scanner behavior to focused regression/CLI/export coverage.

## Branch intelligence contract

ProjectScanner emits evidence; it does not authorize deletion.

For each non-canonical branch, normalized evidence should include at minimum:

- branch/ref and exact head SHA;
- canonical branch/head;
- merge base/ancestry where meaningful;
- ahead/behind or equivalent containment evidence;
- unique commit/file counts and bounded inventory references;
- open PR/protection/retention facts when available;
- `classification_path`: `FAST_PATH`, `FORENSIC_PATH`, or `UNRESOLVED`;
- `classification_reason` and evidence references;
- unique-surface dispositions when forensic: `PROMOTE`, `RETAIN`, `REJECT_WITH_EVIDENCE`, `UNKNOWN`;
- `delete_eligible` as an evidence-derived candidate flag only, never mutation authority.

FAST_PATH is appropriate only for proven containment/equivalence/supersession. Unique or ambiguous content routes to FORENSIC_PATH. `UNKNOWN` blocks a clean-delete recommendation.

## Planning representation contract

ProjectScanner must represent repository-owned planning cleanly:

- stable task ID;
- priority;
- status (`READY`, `ACTIVE`, `BLOCKED`, `COMPLETE`, `HOLD` where supported by the source repo);
- dependencies;
- whether the task appears in canonical NEXT_UP;
- source file/ref/digest/provenance;
- parser errors/drift as explicit invalid/unknown evidence.

ProjectScanner MUST NOT manufacture missing task IDs, rerank portfolio work, reinterpret HOLD/BLOCKED as executable, or turn advisory cleanup recommendations into tasks.

## Non-executable strategic inventory

These remain valid capability domains but cannot be assigned until promoted to a stable `PSC-*` row:

- canonical scanner regression coverage and optional dependency/agent analysis;
- CLI/report/context schema verification;
- generated analysis retention/ignore policy;
- RAG/knowledge ownership and handoff;
- snapshot/ingestion hardening;
- legacy GUI/history documentation cleanup;
- documentation synchronization and Dream.OS consumer compatibility.

## Completion gate

ProjectScanner is planning/intelligence-standardized when:

- canonical artifact hierarchy is implemented and documented;
- branch facts use the FAST_PATH/FORENSIC_PATH vocabulary;
- repository planning emits stable task identities without invention;
- intelligence packet provenance joins deep/current/planning evidence;
- DreamVault can consume the packet while retaining governance/ranking authority;
- legacy peer artifacts are compatibility/advisory surfaces rather than competing authority;
- current executable queue is five items or fewer.
