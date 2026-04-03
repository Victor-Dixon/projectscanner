# Using the Updated SSOT Scanner

## What changed
- The SSOT scanner path is `src/core/projectscanner/`.
- `ProjectScanner` now supports:
  - cheap cache validation (`mtime` + `size`)
  - optional hash-on-change cache enrichment
  - parallel file processing
  - bare-repo metadata mode
  - context chunk exports (`directory`, `language`, `none`)

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
