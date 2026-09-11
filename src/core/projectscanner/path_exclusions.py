"""Path exclusion rules relative to the active ProjectScanner scan root."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

GLOBAL_EXCLUDE_DIR_NAMES = frozenset(
    {
        "__pycache__",
        "node_modules",
        "migrations",
        "build",
        "target",
        ".git",
        "coverage",
        "chrome_profile",
        "logs",
        "venv",
        "env",
        ".env",
        ".venv",
        "virtualenv",
        "ENV",
        "VENV",
        ".ENV",
        ".VENV",
        "python-env",
        "python-venv",
        "py-env",
        "py-venv",
        "envs",
        "conda-env",
        ".conda-env",
        ".poetry",
    }
)
RUNTIME_GENERATED_SUBDIR_NAMES = frozenset({"state", "cache", "tmp", "logs", "reports"})
VENV_PATH_MARKERS = frozenset(
    {
        "venv",
        "env",
        ".env",
        ".venv",
        "virtualenv",
        "ENV",
        "VENV",
        ".ENV",
        ".VENV",
        "python-env",
        "python-venv",
        "py-env",
        "py-venv",
        "envs",
        "conda-env",
        ".conda-env",
        ".poetry/venv",
        ".poetry-venv",
    }
)
SCANNER_ARTIFACT_NAMES = (
    ".projectscanner_cache.json",
    "project_analysis_",
    "chatgpt_project_context_",
)


def relative_parts(file_path: Path, project_root: Path) -> tuple[str, ...]:
    """Return path segments relative to the active scan root."""
    try:
        return file_path.resolve().relative_to(project_root.resolve()).parts
    except ValueError:
        return ()


def is_runtime_generated_path(rel_parts: Iterable[str]) -> bool:
    """Return whether a repo-relative runtime path is generated state/noise."""
    parts = tuple(rel_parts)
    return len(parts) >= 2 and parts[0] == "runtime" and parts[1] in RUNTIME_GENERATED_SUBDIR_NAMES


def should_exclude_path(
    file_path: Path,
    project_root: Path,
    additional_ignore_dirs: Iterable[str],
) -> bool:
    """Return True when file_path should be skipped for this scan root."""
    file_abs = file_path.resolve()
    root = project_root.resolve()

    for ignore in additional_ignore_dirs:
        ignore_path = Path(ignore)
        if not ignore_path.is_absolute():
            ignore_path = (root / ignore_path).resolve()
        try:
            file_abs.relative_to(ignore_path)
            return True
        except ValueError:
            continue

    rel_parts = relative_parts(file_path, project_root)
    if rel_parts and any(part in GLOBAL_EXCLUDE_DIR_NAMES for part in rel_parts):
        return True
    if is_runtime_generated_path(rel_parts):
        return True

    if file_abs.name == SCANNER_ARTIFACT_NAMES[0] or any(
        file_abs.name.startswith(pattern) and file_abs.suffix == ".json"
        for pattern in SCANNER_ARTIFACT_NAMES[1:]
    ):
        return True

    path_str = str(file_abs).lower().replace("\\", "/")
    return any(f"/{pattern}/" in path_str for pattern in VENV_PATH_MARKERS)
