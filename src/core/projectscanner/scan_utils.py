"""
MODULE: scan_utils
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parallel file scanner and agent categorization module.

This module provides utility functions to:
- Recursively scan a project directory for files with specific extensions,
  skipping ignored directories and user‑defined exclusions.
- Process the discovered files in parallel using a thread pool.
- Enrich analysis results with agent maturity and type annotations.

Core authors: Dream
Assisted by: DeepSeek, ChatGPT
Date: 2026-04-26
License: MIT (or your preferred license)
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Set, Union

# Configure module‑level logger for error reporting
logger = logging.getLogger(__name__)


# Concept: TODO - Explain the core idea behind iter_scan_files
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 47 lines > 30 limit)
def iter_scan_files(
# Concept: TODO - Purpose of iter_scan_files
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    project_root: Union[str, Path],
    supported_extensions: Set[str],
    file_processor: object,
    ignore_dirs: Set[str],
) -> Iterator[Path]:
    """
    Recursively walk a directory and yield file paths that match supported extensions
    and are not excluded by `file_processor` or `ignore_dirs`.

    The function modifies the `dirs` list in‑place during `os.walk` to prune
    unwanted subtrees, improving scanning efficiency.

    Args:
        project_root: Root directory to scan (string or Path).
        supported_extensions: Set of file suffixes (e.g., {'.py', '.md'}) to include.
        file_processor: Object with a `should_exclude(path: Path) -> bool` method.
        ignore_dirs: Set of directory names to skip entirely (exact name match).

    Yields:
        Path objects for each matching file.

    Example:
        >>> skip_dirs = {'.git', '__pycache__'}
        >>> exts = {'.py', '.yaml'}
        >>> for fp in iter_scan_files('/myproject', exts, my_processor, skip_dirs):
        ...     print(fp)
    """
    project_root = Path(project_root)

    for root, dirs, files in os.walk(project_root):
        root_path = Path(root)

        # Prune directories in‑place: remove those that are in ignore_dirs
        # or are excluded by the file_processor (e.g., virtual environments).
        dirs[:] = [
            d for d in dirs
            if d not in ignore_dirs and not file_processor.should_exclude(root_path / d)
        ]

        for filename in files:
            file_path = root_path / filename
            if (
                file_path.suffix.lower() in supported_extensions
                and not file_processor.should_exclude(file_path)
            ):
                yield file_path


# Concept: TODO - Explain the core idea behind process_files_parallel
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 55 lines > 30 limit)
def process_files_parallel(
# Concept: TODO - Purpose of process_files_parallel
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    files: List[Path],
    process_file: Callable[[Path], Optional[Dict]],
    workers: int,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> List[Dict]:
    """
    Process a list of files in parallel using a thread pool.

    Each file is processed by the `process_file` callable. Results that are `None`
    are silently ignored. Any exception raised during processing of a single file
    is logged and does not stop processing of other files.

    Args:
        files: List of file paths to process.
        process_file: Function that takes a Path and returns a result dictionary
                      (or None if the file should be skipped).
        workers: Maximum number of worker threads.
        progress_callback: Optional callback receiving an integer percentage (0‑100)
                           after each completed file.

    Returns:
        List of non‑None results (dictionaries) from `process_file`, in the order
        of completion (not the original order).
    """
    results: List[Dict] = []
    total_files = len(files)
    processed = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks and keep a mapping from future to its file path
        future_to_file = {
            executor.submit(process_file, file_path): file_path
            for file_path in files
        }

        for future in as_completed(future_to_file):
            processed += 1
            if progress_callback:
                progress_callback(int(processed / total_files * 100))

            try:
                result = future.result()
            except Exception as e:
                file_path = future_to_file[future]
                logger.error(f"Error processing {file_path}: {e}")
                continue  # Skip this file, continue with the next one

            if result is not None:
                results.append(result)

    return results


# Concept: TODO - Explain the core idea behind categorize_agents
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 49 lines > 30 limit)
def categorize_agents(
# Concept: TODO - Purpose of categorize_agents
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    analysis: Dict,
    maturity_fn: Callable[[str, Dict], str],
    agent_type_fn: Callable[[str, Dict], str],
) -> Dict:
    """
    Enrich each agent class in the analysis dict with maturity and type annotations.

    The `analysis` dictionary is assumed to have the structure:
        {
            file_path: {
                "class_details": {      # may also be called "classes"
                    class_name: { ... }   # arbitrary details about the class
                }
            }
        }

    The function modifies the input dictionary in‑place and also returns it.

    Args:
        analysis: Dictionary mapping file paths to their analysis results.
        maturity_fn: Function that takes (class_name, details) and returns a maturity
                     string (e.g., "stable", "experimental").
        agent_type_fn: Function that takes (class_name, details) and returns an agent
                       type string (e.g., "llm", "rule_based").

    Returns:
        The same analysis dictionary with "maturity" and "agent_type" keys added
        to each class's details dictionary.
    """
    for file_result in analysis.values():
        # Support two possible keys for backward compatibility
        classes = file_result.get("class_details") or file_result.get("classes")
        if not isinstance(classes, dict):
            continue  # No classes to process in this file

        for class_name, details in classes.items():
            if not isinstance(details, dict):
                # Skip malformed entries
                continue

            # Add the two derived annotations
            details["maturity"] = maturity_fn(class_name, details)
            details["agent_type"] = agent_type_fn(class_name, details)

    return analysis
