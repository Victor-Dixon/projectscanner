from __future__ import annotations

try:
    from engine.file_processor import FileProcessor
except Exception:
    class FileProcessor:
        pass

try:
    from engine.language_analyzer import LanguageAnalyzer
except Exception:
    class LanguageAnalyzer:
        pass

try:
    from engine.scanner import ProjectScanner
except Exception:
    class ProjectScanner:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
