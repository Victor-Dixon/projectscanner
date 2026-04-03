import json
import logging
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional

from .file_processor import FileProcessor
from .language_analyzer import LanguageAnalyzer
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class ProjectScanner:
    """SSOT scanner engine with optional bare-repo and parallel scan support."""

    SUPPORTED_EXTENSIONS = {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".rs",
        ".md", ".json", ".yaml", ".yml", ".toml", ".sh", ".rst",
    }

    def __init__(
        self,
        project_root: str | Path = ".",
        output_dir: str | Path | None = None,
        max_file_size_mb: int = 10,
        hash_on_change: bool = False,
        workers: int | None = None,
    ):
        self.project_root = Path(project_root).resolve()
        self.is_bare = self._is_bare_repo(self.project_root)

        if output_dir:
            self.output_dir = Path(output_dir).resolve()
        elif self.is_bare:
            self.output_dir = self.project_root.parent / "_scanner_reports" / self.project_root.name.replace(".git", "")
        else:
            self.output_dir = self.project_root

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.cache_lock = threading.Lock()
        self.cache_path = self.output_dir / ".projectscanner_cache.json"
        self.cache: Dict[str, Dict[str, str]] = self._load_cache()

        self.additional_ignore_dirs: set = set()
        self.analysis: Dict[str, Dict] = {}

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

    def _run_git(self, repo_path: Path, *args: str) -> tuple[int, str]:
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
        except Exception as exc:  # pragma: no cover
            return 1, str(exc)

    def _is_bare_repo(self, repo_path: Path) -> bool:
        code, output = self._run_git(repo_path, "rev-parse", "--is-bare-repository")
        return code == 0 and output.lower() == "true"

    def _load_cache(self) -> Dict[str, Dict[str, str]]:
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_cache(self) -> None:
        try:
            with self.cache_path.open("w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as exc:  # pragma: no cover
            logger.error("❌ Failed to save cache: %s", exc)

    def _iter_scan_files(self) -> Iterable[Path]:
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            dirs[:] = [
                d for d in dirs
                if d not in self.additional_ignore_dirs
                and not self.file_processor.should_exclude(root_path / d)
            ]

            for filename in files:
                file_path = root_path / filename
                if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                    continue
                yield file_path

    def _process_file(self, file_path: Path):
        return self.file_processor.process_file(file_path, self.language_analyzer)

    def scan_project(
        self,
        progress_callback: Optional[Callable[[int], None]] = None,
        split_output_by: str = "directory",
        max_files_per_chunk: int = 100,
        export_context: bool = False,
    ) -> Dict[str, Dict]:
        self.file_processor.additional_ignore_dirs = self.additional_ignore_dirs

        if self.is_bare:
            self.report_generator.export_bare_repo_metadata(self._run_git)
            self._save_cache()
            return self.analysis

        files = list(self._iter_scan_files())
        total_files = len(files)

        if total_files == 0:
            merged_analysis = self.report_generator.save_report()
            if export_context:
                self.report_generator.analysis = merged_analysis
                self.report_generator.export_chatgpt_context(split_by=split_output_by, max_files_per_chunk=max_files_per_chunk)
            self._save_cache()
            return merged_analysis

        processed = 0
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self._process_file, fp): fp for fp in files}
            for future in as_completed(futures):
                processed += 1
                result = future.result()
                if progress_callback:
                    progress_callback(int((processed / total_files) * 100))
                if result is None:
                    continue
                relative_path, analysis_result, cache_entry = result
                self.analysis[relative_path] = analysis_result
                with self.cache_lock:
                    self.cache[relative_path] = cache_entry

        self.report_generator.analysis = self.analysis
        merged_analysis = self.report_generator.save_report()
        if export_context:
            self.report_generator.analysis = merged_analysis
            self.report_generator.export_chatgpt_context(split_by=split_output_by, max_files_per_chunk=max_files_per_chunk)
        self._save_cache()
        return merged_analysis

    def categorize_agents(self) -> Dict[str, Dict]:
        for file_result in self.analysis.values():
            classes = file_result.get("class_details") or file_result.get("classes", {})
            if not isinstance(classes, dict):
                continue
            for class_name, details in classes.items():
                if not isinstance(details, dict):
                    continue
                details["maturity"] = self._maturity_level(class_name, details)
                details["agent_type"] = self._agent_type(class_name, details)
        return self.analysis

    def _maturity_level(self, name: str, details: Dict) -> str:
        methods = details.get("methods", []) or []
        has_doc = bool(details.get("docstring"))
        has_base = bool(details.get("base_classes", []))
        if len(methods) >= 4 and has_doc and has_base:
            return "Core Asset"
        if len(methods) >= 2 or has_doc:
            return "Growing Asset"
        return "Kiddie Script"

    def _agent_type(self, name: str, details: Dict) -> str:
        methods = {m.lower() for m in (details.get("methods", []) or [])}
        doc = (details.get("docstring") or "").lower()

        if {"run", "execute", "act"} & methods:
            return "ActionAgent"
        if any(token in doc for token in ["transform", "parse", "ingest", "data"]):
            return "DataAgent"
        if {"predict", "score", "infer", "classify"} & methods:
            return "SignalAgent"
        return "Utility"

    def generate_init_files(self, overwrite: bool = True) -> None:
        self.report_generator.generate_init_files(overwrite=overwrite)

    def export_chatgpt_context(
        self,
        template_path: str | None = None,
        output_path: str | None = None,
        split_by: str = "directory",
        max_files_per_chunk: int = 100,
    ) -> None:
        self.report_generator.export_chatgpt_context(
            template_path=template_path,
            output_path=output_path,
            split_by=split_by,
            max_files_per_chunk=max_files_per_chunk,
        )
