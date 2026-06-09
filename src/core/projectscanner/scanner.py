"""
MODULE: scanner
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SSOT (Single Source of Truth) scanner engine for software projects.

This module provides a `ProjectScanner` orchestrator that:
- Recursively scans a project for supported file types.
- Extracts classes, methods, docstrings, and imports (AST analysis).
- Processes files in parallel with thread‑safe caching.
- Builds a cross‑file dependency graph (reverse import index).
- Categorizes agent classes by maturity and type.
- Handles bare Git repositories gracefully.

Core authors: Dream
Assisted by: DeepSeek, ChatGPT, Gemini
Date: 2026-04-26
License: MIT
"""

import json
import logging
import os
import subprocess
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

from .file_cache import SCAN_EXCLUDE_DIR_NAMES, load_file_cache, save_file_cache
from .file_processor import FileProcessor
from .language_analyzer import LanguageAnalyzer
from .report_generator import ReportGenerator
from .scan_utils import iter_scan_files, process_files_parallel, categorize_agents

logger = logging.getLogger(__name__)


class ProjectScanner:
    """
    Orchestrator for scanning, analyzing, and reporting on a codebase.
    
    Delegates file walking, parallel processing, and caching to helper modules,
    and adds cross‑file dependency graph building as a Phase 1 feature.
    """
    
    SUPPORTED_EXTENSIONS: Set[str] = {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".rs",
        ".md", ".json", ".yaml", ".yml", ".toml", ".sh", ".rst",
    }

    # Concept: TODO - Explain the core idea behind __init__
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 48 lines > 30 limit)
    def __init__(
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        self,
        project_root: Union[str, Path] = ".",
        output_dir: Optional[Union[str, Path]] = None,
        max_file_size_mb: int = 10,
        hash_on_change: bool = False,
        workers: Optional[int] = None,
        no_cache: bool = False,
        refresh_cache: bool = False,
    ) -> None:
        """
        Initialize the scanner.

        Args:
            project_root: Root directory to scan.
            output_dir: Output directory for reports and cache (auto‑detected if None).
            max_file_size_mb: Maximum file size to process (larger files are skipped).
            hash_on_change: If True, re‑hash files on every run to detect changes.
            workers: Number of parallel worker threads (auto‑tuned if None).
            no_cache: Ignore on-disk cache for this run (do not load or save).
            refresh_cache: Delete canonical cache before scanning.
        """
        self.project_root = Path(project_root).resolve()
        self.is_bare = self._is_bare_repo(self.project_root)

        self.output_dir = self._resolve_output_dir(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.no_cache = no_cache
        self.cache_lock = threading.Lock()
        self.cache_path = self.output_dir / ".projectscanner_cache.json"
        if no_cache:
            self.cache = {}
        else:
            self.cache = load_file_cache(self.output_dir, refresh=refresh_cache)

        self.additional_ignore_dirs: Set[str] = set()
        self.analysis: Dict[str, Dict] = {}
        self.dependency_graph: Dict[str, List[str]] = {}  # target -> list of importers

        self.language_analyzer = LanguageAnalyzer()
        self.file_processor = FileProcessor(
            project_root=self.project_root,
            cache=self.cache,
            cache_lock=self.cache_lock,
            additional_ignore_dirs=self.additional_ignore_dirs,
            max_file_size_bytes=max_file_size_mb * 1024 * 1024,
            hash_on_change=hash_on_change,
        )
        self.report_generator = ReportGenerator(
            project_root=self.project_root,
            analysis=self.analysis,
            output_dir=self.output_dir,
        )

        self.workers = workers or min(32, max(4, (os.cpu_count() or 4) * 2))

    # ------------------------- Setup / Helpers -------------------------
    # Concept: TODO - Explain the core idea behind _resolve_output_dir
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _resolve_output_dir(self, output_dir: Optional[Union[str, Path]]) -> Path:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """Determine output directory based on bare repo status or user input."""
        if output_dir:
            return Path(output_dir).resolve()
        if self.is_bare:
            repo_name = self.project_root.name.replace(".git", "")
            return self.project_root.parent / "_scanner_reports" / repo_name
        return self.project_root

    # Concept: TODO - Explain the core idea behind _run_git
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _run_git(self, repo_path: Path, *args: str) -> Tuple[int, str]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """Execute a Git command and return (return_code, output)."""
        try:
            proc = subprocess.run(
                ["git", *args],
                cwd=repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            output = (proc.stdout or "").strip() or (proc.stderr or "").strip()
            return proc.returncode, output
        except Exception as exc:
            return 1, str(exc)

    # Concept: TODO - Explain the core idea behind _is_bare_repo
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _is_bare_repo(self, repo_path: Path) -> bool:
        """Check if the given path is a bare Git repository."""
    # Concept: TODO - Purpose of _run_git
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        code, output = self._run_git(repo_path, "rev-parse", "--is-bare-repository")
        return code == 0 and output.lower() == "true"

    # ------------------------- Cache -------------------------
    # Concept: TODO - Explain the core idea behind _load_cache
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _save_cache(self) -> None:
        """Write in‑memory cache to disk (canonical path, pruned)."""
        if not self.no_cache:
            save_file_cache(self.output_dir, self.cache)

    # ------------------------- Core Scan Flow (No Stubs) -------------------------
    # Concept: TODO - Explain the core idea behind _collect_files
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _collect_files(self) -> List[Path]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """Walk the project root and collect all supported files, respecting ignores."""
        walk_ignore = set(self.additional_ignore_dirs) | set(SCAN_EXCLUDE_DIR_NAMES)
        return list(
            iter_scan_files(
                self.project_root,
                self.SUPPORTED_EXTENSIONS,
                self.file_processor,
                walk_ignore,
            )
        )

    # Concept: TODO - Explain the core idea behind _process_file
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _process_file(self, file_path: Path) -> Tuple[str, Dict, Dict[str, str]]:
        """Wrap the file processor for use in parallel execution."""
        return self.file_processor.process_file(file_path, self.language_analyzer)

    # Concept: TODO - Explain the core idea behind _run_parallel_scan
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _run_parallel_scan(
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        self,
        files: List[Path],
        progress_callback: Optional[Callable[[int], None]],
    ) -> List[Tuple[str, Dict, Dict[str, str]]]:
        """Process all collected files in parallel using a thread pool."""
        return process_files_parallel(
            files,
            self._process_file,
            self.workers,
            progress_callback,
        )

    # Concept: TODO - Explain the core idea behind _merge_results
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _merge_results(self, results: List[Tuple[str, Dict, Dict[str, str]]]) -> None:
        """Merge parallel processing results into the main analysis dict and cache."""
        for relative_path, analysis_result, cache_entry in results:
            self.analysis[relative_path] = analysis_result
            with self.cache_lock:
                self.cache[relative_path] = cache_entry

    # Concept: TODO - Explain the core idea behind _finalize_report
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _finalize_report(
    # Concept: TODO - Purpose of _finalize_report
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        self,
        export_context: bool,
        split_output_by: str,
        max_files_per_chunk: int,
    ) -> Dict[str, Dict]:
        """Generate final report(s) and save cache."""
        self.report_generator.analysis = self.analysis
        merged_analysis = self.report_generator.save_report()

        if export_context:
            self.report_generator.analysis = merged_analysis
            self.report_generator.export_chatgpt_context(
                split_by=split_output_by,
                max_files_per_chunk=max_files_per_chunk,
            )

        self._save_cache()
        return merged_analysis

    # ------------------------- Cross‑file Dependency Graph (Phase 1) -------------------------
    # Concept: TODO - Explain the core idea behind _build_global_dependency_graph
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 34 lines > 30 limit)
    def _build_global_dependency_graph(self) -> Dict[str, List[str]]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """
        Build a reverse index: for each Python file, which other files import it.
        
        Uses a simplified module‑to‑file mapping (relative path with slashes replaced by dots,
        `.py` removed). For a real resolver, consider augmenting with `__init__.py` and
        namespace package logic.
        """
    # Concept: TODO - Purpose of _build_global_dependency_graph
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        # Map module names to their defining file (only .py files)
        module_to_file = {}
        for rel_path in self.analysis:
            if rel_path.endswith(".py"):
                module_name = rel_path.replace("/", ".").replace(".py", "")
                module_to_file[module_name] = rel_path
        
        # Reverse graph: target_file -> list_of_importer_files
        reverse_graph: Dict[str, List[str]] = {}
        for importer_path, data in self.analysis.items():
            imports = data.get("imports", [])
            for imp in imports:
                if imp.get("type") == "direct":
                    mod = imp.get("module")
                    if mod in module_to_file:
                        target = module_to_file[mod]
                        reverse_graph.setdefault(target, []).append(importer_path)
                elif imp.get("type") == "from":
                    mod = imp.get("module")
                    if mod and mod in module_to_file:
                        target = module_to_file[mod]
                        reverse_graph.setdefault(target, []).append(importer_path)
        return reverse_graph

    # Concept: TODO - Explain the core idea behind search_usage
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def search_usage(self, class_or_module_name: str) -> List[str]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """
        Find all files that import a given module or class name.
        
        Args:
            class_or_module_name: Module name (e.g., "foo.bar") or class name imported
                                  via `from module import ClassName`.
        
        Returns:
            Sorted list of file paths (relative to project root) that reference the name.
        """
    # Concept: TODO - Purpose of search_usage
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        results = set()
        for file_path, data in self.analysis.items():
            imports = data.get("imports", [])
            for imp in imports:
                if imp.get("type") == "direct" and imp.get("module") == class_or_module_name:
                    results.add(file_path)
                elif imp.get("type") == "from":
                    if class_or_module_name in imp.get("names", []):
                        results.add(file_path)
                    if imp.get("module") == class_or_module_name:
                        results.add(file_path)
        return sorted(results)

    # ------------------------- Public API -------------------------
    # Concept: TODO - Explain the core idea behind scan_project
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 43 lines > 30 limit)
    def scan_project(
    # Concept: TODO - Purpose of scan_project
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        self,
        progress_callback: Optional[Callable[[int], None]] = None,
        split_output_by: str = "directory",
        max_files_per_chunk: int = 100,
        export_context: bool = False,
        build_graph: bool = True,
    ) -> Dict[str, Dict]:
        """
        Run the full project scan, analysis, and report generation.
        
        Args:
            progress_callback: Optional function called with completion percentage.
            split_output_by: How to split the ChatGPT export ("directory" or "file").
            max_files_per_chunk: Max files per chunk when splitting.
            export_context: Whether to generate ChatGPT context files.
            build_graph: If True, build the cross‑file dependency graph.
        
        Returns:
            Dictionary mapping relative file paths to their analysis results.
        """
        self.file_processor.additional_ignore_dirs = self.additional_ignore_dirs

        if self.is_bare:
            self.report_generator.export_bare_repo_metadata(self._run_git)
            self._save_cache()
            return self.analysis

        files = self._collect_files()
        if not files:
            return self._finalize_report(export_context, split_output_by, max_files_per_chunk)

        logger.info("Scanning %d files under %s", len(files), self.project_root)
        results = self._run_parallel_scan(files, progress_callback)
        skipped = len(files) - len(results)
        if skipped:
            logger.info("Cache fast-path skipped %d unchanged files", skipped)
        self._merge_results(results)

        if build_graph:
            self.dependency_graph = self._build_global_dependency_graph()
            self.analysis["__dependency_graph__"] = self.dependency_graph

        return self._finalize_report(export_context, split_output_by, max_files_per_chunk)

    # Concept: TODO - Explain the core idea behind categorize_agents
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def categorize_agents(self) -> Dict[str, Dict]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """Enrich the analysis data with agent maturity and type fields."""
        return categorize_agents(
            self.analysis,
            self._maturity_level,
            self._agent_type,
        )

    # ------------------------- Agent Categorization Logic -------------------------
    # Concept: TODO - Explain the core idea behind _maturity_level
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _maturity_level(self, name: str, details: Dict) -> str:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """Determine maturity level based on methods, docstring, and inheritance."""
        methods = details.get("methods", []) or []
        has_doc = bool(details.get("docstring"))
        has_base = bool(details.get("base_classes", []))
        if len(methods) >= 4 and has_doc and has_base:
            return "Core Asset"
        if len(methods) >= 2 or has_doc:
            return "Growing Asset"
        return "Kiddie Script"

    # Concept: TODO - Explain the core idea behind _agent_type
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _agent_type(self, name: str, details: Dict) -> str:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """Classify agent type by method names and docstring content."""
        methods = {m.lower() for m in (details.get("methods", []) or [])}
        doc = (details.get("docstring") or "").lower()
        if {"run", "execute", "act"} & methods:
            return "ActionAgent"
        if any(token in doc for token in ["transform", "parse", "ingest", "data"]):
            return "DataAgent"
        if {"predict", "score", "infer", "classify"} & methods:
            return "SignalAgent"
        return "Utility"

    # ------------------------- Delegated Features -------------------------
    # Concept: TODO - Explain the core idea behind generate_init_files
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def generate_init_files(self, overwrite: bool = True) -> None:
        """Generate `__init__.py` files in directories containing `.py` files."""
        self.report_generator.generate_init_files(overwrite=overwrite)

    # Concept: TODO - Explain the core idea behind export_chatgpt_context
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def export_chatgpt_context(
    # Concept: TODO - Purpose of export_chatgpt_context
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        self,
        template_path: Optional[str] = None,
        output_path: Optional[str] = None,
        split_by: str = "directory",
        max_files_per_chunk: int = 100,
    ) -> None:
        """Export the analysis as ChatGPT‑compatible context files."""
        self.report_generator.export_chatgpt_context(
            template_path=template_path,
            output_path=output_path,
            split_by=split_by,
            max_files_per_chunk=max_files_per_chunk,
        )
