"""Path exclusion rules for ProjectScanner (relative to scan root)."""

from __future__ import annotations

from pathlib import Path
from typing import FrozenSet, Iterable, Tuple

# Directory names excluded anywhere under the scan root (relative segments).
GLOBAL_EXCLUDE_DIR_NAMES: FrozenSet[str] = frozenset(
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
        # Virtualenv / env folder names
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

# Under `<scan_root>/runtime/<name>/...` these subtrees are skipped on full-repo walks.
RUNTIME_GENERATED_SUBDIR_NAMES: FrozenSet[str] = frozenset(
    {"state", "cache", "tmp", "logs", "reports"}
)

VENV_PATH_MARKERS: FrozenSet[str] = frozenset(
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

SCANNER_ARTIFACT_NAMES: Tuple[str, ...] = (
    ".projectscanner_cache.json",
    "project_analysis_",
    "chatgpt_project_context_",
)


def relative_parts(file_path: Path, project_root: Path) -> Tuple[str, ...]:
    """Path segments relative to project_root; empty if outside root."""
    try:
        return file_path.resolve().relative_to(project_root.resolve()).parts
    except ValueError:
        return ()


def is_runtime_generated_path(rel_parts: Iterable[str]) -> bool:
    """True when relative path is runtime/<generated>/... (full-repo perspective)."""
    parts = tuple(rel_parts)
    return (
        len(parts) >= 2
        and parts[0] == "runtime"
        and parts[1] in RUNTIME_GENERATED_SUBDIR_NAMES
    )


def should_exclude_path(
    file_path: Path,
    project_root: Path,
    additional_ignore_dirs: Iterable[str],
) -> bool:
    """Return True if file_path should be skipped for this scan root."""
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
    if any(f"/{pattern}/" in path_str for pattern in VENV_PATH_MARKERS):
        return True

    return False
