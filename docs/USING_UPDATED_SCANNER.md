# Using ProjectScanner

Last synchronized: 2026-07-03

## What this project is

ProjectScanner is repository scanning and inventory intelligence tooling in the software repository analysis domain.

## Source of truth

The canonical scanner path is:

```text
src/core/projectscanner/
```

New scanner behavior should be added there rather than in parallel scanner engines.

## Supported scanner behavior

`ProjectScanner` currently supports:

- local source tree scans,
- cheap cache validation with `mtime` and `size`,
- optional hash-on-change cache enrichment,
- parallel file processing,
- bare Git repository metadata mode,
- JSON analysis report output,
- ChatGPT context export,
- context chunk exports by `directory`, `language`, or `none`,
- optional `__init__.py` generation for Python package directories.

## Direct Python usage

```python
from core.projectscanner import ProjectScanner

scanner = ProjectScanner(
    project_root="/path/to/project",
    output_dir="/path/to/reports",
    max_file_size_mb=10,
    hash_on_change=False,
    workers=16,
)

scanner.additional_ignore_dirs = {"vendor", "archive"}
scanner.scan_project(
    split_output_by="directory",
    max_files_per_chunk=200,
    export_context=True,
)
```

## CLI usage via `main.py`

```bash
python main.py --scan /path/to/project --export-context --generate-init
python main.py --quick-scan /path/to/project
```

## CI-oriented runner

```bash
python src/utils/run_scanner.py --target ./src --output ./snapshots/manual --mode manual
```

Target resolution order:

1. `--target` override,
2. `repo_root/src`,
3. `repo_root` fallback.

Relative targets are resolved against the git repository root. Non-existent targets raise `FileNotFoundError`.

## Portfolio intelligence export

```bash
python scripts/export_project_intelligence.py \
  --projects-root "$HOME/projects" \
  --out-root "$HOME/projects/DreamVault/data/intelligence/repos_from_projectscanner"
```

Expected files per repository:

```text
repo_analysis.json
chatgpt_context.json
cleanup_recommendations.json
docs_gap_report.md
```

## Known incomplete surfaces

- `python main.py --gui` currently imports missing enhanced GUI modules.
- `ingest_snapshot.py` expects a normalized `analysis.json` schema that the scanner runner does not yet emit directly.
- Dependency graph and agent categorization are not complete scanner-output guarantees with the current analyzer output.

## Verification

```bash
pytest -q
```

## What remains

The next work is snapshot contract stabilization. See root `NEXT_UP.md`.
