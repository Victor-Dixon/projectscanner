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

from .language_analyzer import LanguageAnalyzer
from .path_exclusions import should_exclude_path

logger = logging.getLogger(__name__)


class FileProcessor:
    """SSOT file processing with cheap cache validation (mtime + size first)."""

    def __init__(
        self,
        project_root: Path,
        cache: dict,
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

    def hash_file(self, file_path: Path) -> str:
        try:
            hasher = hashlib.md5()
            with file_path.open("rb") as file_handle:
                for chunk in iter(lambda: file_handle.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:  # noqa: BLE001  # preserve legacy fail-soft hashing
            return ""

    def should_exclude(self, file_path: Path) -> bool:
        return should_exclude_path(file_path, self.project_root, self.additional_ignore_dirs)

    def process_file(self, file_path: Path, language_analyzer: LanguageAnalyzer) -> tuple | None:
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
            with file_path.open("r", encoding="utf-8") as file_handle:
                source_code = file_handle.read()
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
        except Exception as exc:  # noqa: BLE001  # preserve legacy per-file isolation
            logger.error("❌ Unexpected error analyzing %s: %s", file_path, exc)
            return None
