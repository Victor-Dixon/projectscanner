"""Public compatibility surface for the ProjectScanner core package."""

from .file_processor import FileProcessor
from .language_analyzer import LanguageAnalyzer
from .scanner import ProjectScanner
from .snapshot_contract import (
    ANALYSIS_SCHEMA_VERSION,
    SnapshotValidationError,
    build_snapshot_analysis,
    validate_analysis_payload,
    validate_metadata_payload,
)

__all__ = [
    "ANALYSIS_SCHEMA_VERSION",
    "FileProcessor",
    "LanguageAnalyzer",
    "ProjectScanner",
    "SnapshotValidationError",
    "build_snapshot_analysis",
    "validate_analysis_payload",
    "validate_metadata_payload",
]
