# Using the Updated SSOT Scanner

## What changed
- The SSOT scanner path is `src/core/projectscanner/`.
- `ProjectScanner` now supports:
  - cheap cache validation (`mtime` + `size`)
  - optional hash-on-change cache enrichment
  - parallel file processing
  - bare-repo metadata mode
  - context chunk exports (`directory`, `language`, `none`)
- `src/utils/run_scanner.py` now emits normalized `analysis.json` for snapshot ingestion while preserving the legacy `project_analysis_<target>.json` report.

## Direct usage (Python)
```python
from core.projectscanner import ProjectScanner

scanner = ProjectScanner(
    project_root="/path/to/project",
    output_dir="/path/to/reports",   # optional
    max_file_size_mb=10,
    hash_on_change=False,
    workers=16,
)

scanner.additional_ignore_dirs = {"vendor", "archive"}
scanner.scan_project(
    split_output_by="directory",      # directory | language | none
    max_files_per_chunk=200,
    export_context=True,
)
```

## CLI usage via `main.py`
```bash
python main.py --scan /path/to/project --export-context --generate-init
python main.py --quick-scan /path/to/project
```

## Snapshot Directory Contract

Snapshot directories are the handoff boundary between CI scanner output and SQLite ingestion.

Required files:
- `metadata.json`
- `analysis.json`

Required `metadata.json` fields:
- `commit_sha`
- `timestamp`
- `scan_mode`

Optional metadata fields currently preserved by ingestion:
- `branch`
- `scanner_version`
- `duration_seconds`
- `workflow_run_id`

Required `analysis.json` fields:
- `schema`: must be `projectscanner.snapshot.v1`
- `total_files`: integer count of normalized file rows
- `files`: list of file objects with at least `path`
- `issues`: list of issue objects; each issue must include `rule`

Normalized file objects include:
- `path`
- `language`
- `hash`
- `functions_count`
- `classes_count`
- `loc`
- `raw`

CI writes metadata and the scanner wrapper writes `analysis.json`:

```bash
python src/utils/run_scanner.py --target ./src --output "$SNAPSHOT_DIR" --mode "$MODE"
python ingest_snapshot.py "$SNAPSHOT_DIR" --repo projectscanner
```

Duplicate ingests for the same `repo + commit_sha` are idempotent: the snapshot row is reused, file rows are replaced, and issue rows are refreshed.

## High-value rollout plan
1. Keep all wrappers importing from `core.projectscanner` only.
2. Use `hash_on_change=False` first for speed; enable if collision-proofing is needed.
3. Start with `split_output_by=directory` and `max_files_per_chunk=100`.
4. For large batch scans, tune `workers` based on disk throughput (8–32 typical).
5. For bare mirrors (`*.git`), run metadata scan and skip source expectations.

## SSOT guardrails
- Do not create parallel scanner engines in `scripts/`.
- New scanner behaviors should be added under `src/core/projectscanner/`.
- Entrypoints should call package-level imports:
  - `from core.projectscanner import ProjectScanner, LanguageAnalyzer`
