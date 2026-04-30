"""
MODULE: file_processor
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

import hashlib
import logging
import threading
from pathlib import Path
from typing import Dict, Optional

from .language_analyzer import LanguageAnalyzer

logger = logging.getLogger(__name__)


class FileProcessor:
    """SSOT file processing with cheap cache validation (mtime + size first)."""

    # Concept: TODO - Explain the core idea behind __init__
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def __init__(
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        self,
        project_root: Path,
        cache: Dict,
        cache_lock: threading.Lock,
        additional_ignore_dirs: set,
        max_file_size_bytes: int = 10 * 1024 * 1024,
        hash_on_change: bool = False,
    ):
        self.project_root = project_root
        self.cache = cache
        self.cache_lock = cache_lock
        self.additional_ignore_dirs = additional_ignore_dirs
        self.max_file_size_bytes = max_file_size_bytes
        self.hash_on_change = hash_on_change

    # Concept: TODO - Explain the core idea behind hash_file
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def hash_file(self, file_path: Path) -> str:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        try:
            hasher = hashlib.md5()
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:  # pragma: no cover
            return ""

    # Concept: TODO - Explain the core idea behind should_exclude
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 47 lines > 30 limit)
    def should_exclude(self, file_path: Path) -> bool:
    # Concept: TODO - Purpose of should_exclude
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        venv_patterns = {
            "venv", "env", ".env", ".venv", "virtualenv",
            "ENV", "VENV", ".ENV", ".VENV",
            "python-env", "python-venv", "py-env", "py-venv",
            "envs", "conda-env", ".conda-env",
            ".poetry/venv", ".poetry-venv",
        }
        default_exclude_dirs = {
            "__pycache__", "node_modules", "migrations", "build",
            "target", ".git", "coverage", "chrome_profile",
            "runtime", "logs",
        } | venv_patterns

        file_abs = file_path.resolve()

        for ignore in self.additional_ignore_dirs:
            ignore_path = Path(ignore)
            if not ignore_path.is_absolute():
                ignore_path = (self.project_root / ignore_path).resolve()
            try:
                file_abs.relative_to(ignore_path)
                return True
            except ValueError:
                continue

        if any(excluded in file_path.parts for excluded in default_exclude_dirs):
            return True

        scanner_artifact_patterns = (
            ".projectscanner_cache.json",
            "project_analysis_",
            "chatgpt_project_context_",
        )

        if file_abs.name == scanner_artifact_patterns[0] or any(
            file_abs.name.startswith(pattern) and file_abs.suffix == ".json"
            for pattern in scanner_artifact_patterns[1:]
        ):
            return True
        path_str = str(file_abs).lower().replace("\\", "/")
        if any(f"/{pattern}/" in path_str for pattern in venv_patterns):
            return True
        return False

    # Concept: TODO - Explain the core idea behind process_file
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 41 lines > 30 limit)
    def process_file(self, file_path: Path, language_analyzer: LanguageAnalyzer) -> Optional[tuple]:
    # Concept: TODO - Purpose of process_file
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        if self.should_exclude(file_path):
            return None

        try:
            stat_result = file_path.stat()
        except OSError:
            return None

        if stat_result.st_size > self.max_file_size_bytes:
            return None

        relative_path = str(file_path.relative_to(self.project_root))
        mtime = stat_result.st_mtime
        size = stat_result.st_size

        with self.cache_lock:
            cached = self.cache.get(relative_path, {})
            if cached.get("mtime") == mtime and cached.get("size") == size:
                return None

        try:
            with file_path.open("r", encoding="utf-8") as f:
                source_code = f.read()
            analysis_result = language_analyzer.analyze_file(file_path, source_code)
            cache_entry = {"mtime": mtime, "size": size}
            if self.hash_on_change:
                cache_entry["hash"] = self.hash_file(file_path)
            return (relative_path, analysis_result, cache_entry)
        except SyntaxError as exc:
            logger.debug("⚠️ Syntax error in %s: %s", file_path.name, exc.msg)
            return None
        except UnicodeDecodeError as exc:
            logger.debug("⚠️ Encoding issue in %s: %s", file_path.name, exc.reason)
            return None
        except Exception as exc:  # pragma: no cover
            logger.error("❌ Unexpected error analyzing %s: %s", file_path, exc)
            return None
