"""
MODULE: orchestrator
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pipeline orchestrator – single entry point for scanning + analysis.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional

from src.core.model.project_snapshot import ProjectSnapshot
from src.core.projectscanner.scanner import ProjectScanner


class PipelineOrchestrator:

    # Concept: TODO - Explain the core idea behind _get_git_commit
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _get_git_commit(self, repo_path: Path) -> Optional[str]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()[:8] if result.returncode == 0 else None
        except Exception:
            return None

    # Concept: TODO - Explain the core idea behind scan
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 39 lines > 30 limit)
    def scan(self, path: str) -> ProjectSnapshot:
    # Concept: TODO - Purpose of scan
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        start = time.time()

        abs_path = Path(path).resolve()
        scanner = ProjectScanner(project_root=abs_path)

        raw = scanner.scan_project()

        snapshot = ProjectSnapshot(
            path=str(abs_path),
            git_commit=self._get_git_commit(abs_path),
        )

        # safer fallback handling
        snapshot.analysis = raw if isinstance(raw, dict) else {}

        # file handling (defensive)
        if isinstance(raw, dict):
            snapshot.files = list(raw.get("files", [])) or list(raw.keys())

        # metrics
        snapshot.metrics["file_count"] = len(snapshot.files)

        snapshot.metrics["scan_duration_sec"] = round(time.time() - start, 3)

        # language detection (improved)
        lang_map = {}
        for f in snapshot.files:
            ext = Path(f).suffix.lower()
            if not ext:
                continue
            lang_map[ext] = lang_map.get(ext, 0) + 1

        snapshot.languages = lang_map

        return snapshot

    # Concept: TODO - Explain the core idea behind analyze
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def analyze(self, snapshot: ProjectSnapshot) -> ProjectSnapshot:
    # Concept: TODO - Purpose of analyze
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        try:
            from src.core.analysis.quick_consolidation_analysis import run_analysis

            result = run_analysis(snapshot.analysis)

            snapshot.analysis = {
                "base": snapshot.analysis,
                "insights": result
            }

        except Exception as e:
            snapshot.analysis["analysis_error"] = str(e)

        return snapshot

    # Concept: TODO - Explain the core idea behind quality
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def quality(self, snapshot: ProjectSnapshot) -> ProjectSnapshot:
    # Concept: TODO - Purpose of quality
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        try:
            from src.quality.complexity_checker import analyze_complexity
            snapshot.quality["complexity"] = analyze_complexity(snapshot)
        except Exception:
            pass

        try:
            from src.quality.loc_checker import count_loc
            snapshot.metrics["loc"] = count_loc(snapshot.path)
        except Exception:
            pass

        return snapshot
