"""Public compatibility surface for the ProjectScanner core package."""

from .file_processor import FileProcessor
from .language_analyzer import LanguageAnalyzer
from .scanner import ProjectScanner
from .snapshot_contract import (
    SNAPSHOT_CONTRACT_VERSION,
    SnapshotContractError,
    normalize_analysis_payload,
    validate_analysis_payload,
    validate_metadata,
)

__all__ = [
    "FileProcessor",
    "LanguageAnalyzer",
    "ProjectScanner",
    "SNAPSHOT_CONTRACT_VERSION",
    "SnapshotContractError",
    "normalize_analysis_payload",
    "validate_analysis_payload",
    "validate_metadata",
]
