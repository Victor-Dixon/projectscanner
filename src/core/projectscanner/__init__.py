"""Public compatibility surface for the ProjectScanner core package."""

from .file_processor import FileProcessor
from .language_analyzer import LanguageAnalyzer
from .scanner import ProjectScanner

__all__ = [
    "FileProcessor",
    "LanguageAnalyzer",
    "ProjectScanner",
]
