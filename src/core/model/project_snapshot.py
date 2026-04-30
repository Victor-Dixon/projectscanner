"""
MODULE: project_snapshot
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Canonical data model for project snapshots.
Single source of truth across scanners, analyzers, and portfolio engine.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


@dataclass
class ProjectSnapshot:
    """Unified representation of a scanned project."""

    # Identity
    path: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    git_commit: Optional[str] = None
    scanner_version: str = "1.0.0"

    # Core structure
    files: List[str] = field(default_factory=list)
    structure: Dict[str, Any] = field(default_factory=dict)

    # Metrics layer
    metrics: Dict[str, Any] = field(default_factory=dict)
    complexity: Dict[str, Any] = field(default_factory=dict)
    languages: Dict[str, Any] = field(default_factory=dict)

    # Intelligence layers
    analysis: Dict[str, Any] = field(default_factory=dict)
    quality: Dict[str, Any] = field(default_factory=dict)

    # Outputs
    reports: Dict[str, Any] = field(default_factory=dict)

    # AI / future layer
    embeddings: Optional[Any] = None
    summary: Optional[str] = None
    insights: Dict[str, Any] = field(default_factory=dict)

