"""
MODULE: __init__
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES
AGENTIC INSTRUCTIONS
"""

try:
    from .gui import AnalysisViewer
except Exception:  # pragma: no cover - optional dependency
    AnalysisViewer = None

__all__ = [
    "ProjectScanner",
    "LanguageAnalyzer",
    "FileProcessor",
    "ReportGenerator",
    "BotWorker",
    "MultibotManager",
    "AnalysisViewer",
]
