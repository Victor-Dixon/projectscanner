# ProjectScanner Repository Audit Pilot

## Purpose

Package the existing ProjectScanner scanning and intelligence-export capability into a bounded, evidence-first repository audit pilot without changing scanner authority, inventing market validation, or claiming customers, revenue, pricing, partners, or adoption that are not evidenced.

## Existing verified capability boundary

ProjectScanner already provides:

- a canonical scanner under `src/core/projectscanner/`;
- `python src/utils/run_scanner.py --target <repo_root>` for a direct scan;
- `python scripts/intelligence/emit_intelligence.py <repo_root> --packet-only` for an intelligence packet;
- portfolio intelligence export producing `repo_analysis.json`, `chatgpt_context.json`, `cleanup_recommendations.json`, and `docs_gap_report.md`;
- snapshot artifacts with a versioned `projectscanner.snapshot.v1` contract;
- SQLite history ingestion for scanner snapshots;
- a repository regression gate of `pytest -q`.

This pilot packages those existing capabilities; it does not create a second scanner, governance authority, or documentation-repair engine.

## Candidate buyer problem

Hypothesis only: software teams and solo maintainers with messy, inherited, duplicated, or poorly documented repositories may need a fast evidence packet before deciding what to repair, consolidate, archive, or hand to an agent.

This is a buyer hypothesis, not validated demand.

## Bounded pilot scope

For one authorized repository or a small explicitly approved repository set:

1. Run ProjectScanner using the canonical scanner path.
2. Emit the existing intelligence packet and/or full scan artifacts.
3. Produce a concise audit handoff using scanner outputs only:
   - repository structure and source-of-truth observations;
   - cleanup candidates;
   - documentation gaps;
   - high-risk ambiguity requiring human verification;
   - recommended next verification lane.
4. Preserve provenance to the scanner artifacts and repository commit/ref used for the assessment.
5. Do not mutate the customer's repository unless a separate implementation scope is explicitly authorized.

## Acceptance evidence

A pilot is technically prepared only when it can show:

- exact repository/ref scanned;
- scanner command used;
- successful scanner/regression execution where applicable;
- generated intelligence artifacts;
- a deterministic, reviewable audit handoff tied to those artifacts;
- explicit separation between observed facts, scanner-derived findings, and recommendations;
- no credentials or private source content copied into public artifacts.

## Commercialization gates

### Gate A — repeatable delivery

Prove the same bounded workflow on at least two disposable or internally authorized repositories without manual reconstruction of the output contract.

### Gate B — buyer evidence

Do not claim market validation until real external evidence exists, such as an authorized discovery conversation, a requested audit, a completed pilot, or documented buyer feedback.

### Gate C — pricing evidence

Pricing is **TBD**. Do not publish or infer a price from competitor rates, internal effort, or hypothetical willingness to pay. Record validated pricing feedback separately when it exists.

### Gate D — privacy and authorization

Only scan repositories the operator is authorized to inspect. Private repository outputs remain private unless explicit publication authority exists.

## Candidate revenue models — unvalidated

These are options to test, not current offerings or revenue claims:

- fixed-scope repository audit;
- portfolio repository health assessment;
- audit + implementation follow-on for verified cleanup lanes;
- internal developer/agent enablement package using ProjectScanner as the diagnostic layer.

## Explicit non-claims

As of this artifact, ProjectScanner does **not** claim:

- paying customers;
- completed external pilots;
- validated pricing;
- recurring revenue;
- sponsors or commercial partners;
- quantified market demand;
- guaranteed security, compliance, or defect detection.

## Current status

`PILOT-PACKAGED / DELIVERY-PROOF-NEEDED / NOT MARKET-VALIDATED`

## Next safe closure

Create an internal, disposable two-repository delivery proof using the canonical scan and intelligence commands, record the exact outputs and effort, and only then decide whether an external outreach/pilot request is warranted.