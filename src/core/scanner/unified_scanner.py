#!/usr/bin/env python3
"""
Unified Project Scanner

A single, configurable scanning engine that supports three presets:
- quick: single JSON output only
- standard: merged JSON + single ChatGPT context (optionally split tests) + optional __init__ generation
- full: merged JSON + split ChatGPT context by directory/language/chunks with index/metadata + optional __init__ generation

This unifies prior scanners while allowing fine-grained configuration via parameters.
"""

from __future__ import annotations

import os
import ast
import json
import hashlib
import threading
import queue
import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple


# Optional tree-sitter support
try:
    from tree_sitter import Language, Parser  # type: ignore
except Exception:  # pragma: no cover
    Language = None
    Parser = None


CACHE_FILE = "dependency_cache.json"


class LanguageAnalyzer:
    """Language-specific analysis helpers."""

    def __init__(self) -> None:
        self.rust_parser = self._init_tree_sitter_language("rust")
        self.js_parser = self._init_tree_sitter_language("javascript")

    def _init_tree_sitter_language(self, lang_name: str) -> Optional[Parser]:
        if not Language or not Parser:
            return None

        grammar_paths = {
            "rust": "path/to/tree-sitter-rust.so",
            "javascript": "path/to/tree-sitter-javascript.so",
        }
        grammar_path = grammar_paths.get(lang_name)
        if not grammar_path or not Path(grammar_path).exists():
            return None
        try:
            lang_lib = Language(grammar_path, lang_name)
            parser = Parser()
            parser.set_language(lang_lib)
            return parser
        except Exception:
            return None

    def analyze(self, file_path: Path, source_code: str) -> Dict[str, Any]:
        suffix = file_path.suffix.lower()
        if suffix == ".py":
            return self._analyze_python(source_code)
        if suffix == ".rs" and self.rust_parser:
            return self._analyze_rust(source_code)
        if suffix in [".js", ".ts"] and self.js_parser:
            return self._analyze_javascript(source_code)
        return {"language": suffix, "functions": [], "classes": {}, "routes": [], "complexity": 0}

    def _analyze_python(self, source_code: str) -> Dict[str, Any]:
        tree = ast.parse(source_code)
        functions: List[str] = []
        classes: Dict[str, List[str]] = {}
        routes: List[Dict[str, str]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and hasattr(decorator.func, "attr"):
                        func_attr = decorator.func.attr.lower()
                        if func_attr in {"route", "get", "post", "put", "delete", "patch"}:
                            path_arg = "/unknown"
                            methods = [func_attr.upper()]
                            if decorator.args:
                                arg0 = decorator.args[0]
                                if isinstance(arg0, ast.Str):
                                    path_arg = arg0.s
                            for kw in decorator.keywords:
                                if kw.arg == "methods" and isinstance(kw.value, ast.List):
                                    extracted = []
                                    for elt in kw.value.elts:
                                        if isinstance(elt, ast.Str):
                                            extracted.append(elt.s.upper())
                                    if extracted:
                                        methods = extracted
                            for m in methods:
                                routes.append({"function": node.name, "method": m, "path": path_arg})
            elif isinstance(node, ast.ClassDef):
                method_names = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                classes[node.name] = method_names

        complexity = len(functions) + sum(len(m) for m in classes.values())
        return {
            "language": ".py",
            "functions": functions,
            "classes": classes,
            "routes": routes,
            "complexity": complexity,
        }

    def _analyze_rust(self, source_code: str) -> Dict[str, Any]:
        if not self.rust_parser:
            return {"language": ".rs", "functions": [], "classes": {}, "routes": [], "complexity": 0}
        tree = self.rust_parser.parse(bytes(source_code, "utf-8"))
        functions: List[str] = []
        classes: Dict[str, List[str]] = {}

        def _traverse(node):
            if node.type == "function_item":
                fn = node.child_by_field_name("name")
                if fn:
                    functions.append(fn.text.decode("utf-8"))
            elif node.type == "struct_item":
                nm = node.child_by_field_name("name")
                if nm:
                    classes[nm.text.decode("utf-8")] = []
            elif node.type == "impl_item":
                impl_type = node.child_by_field_name("type")
                if impl_type:
                    impl_name = impl_type.text.decode("utf-8")
                    classes.setdefault(impl_name, [])
                    for child in node.children:
                        if child.type == "function_item":
                            mn = child.child_by_field_name("name")
                            if mn:
                                classes[impl_name].append(mn.text.decode("utf-8"))
            for ch in node.children:
                _traverse(ch)

        _traverse(tree.root_node)
        return {"language": ".rs", "functions": functions, "classes": classes, "routes": [], "complexity": len(functions) + sum(len(v) for v in classes.values())}

    def _analyze_javascript(self, source_code: str) -> Dict[str, Any]:
        if not self.js_parser:
            return {"language": ".js", "functions": [], "classes": {}, "routes": [], "complexity": 0}
        tree = self.js_parser.parse(bytes(source_code, "utf-8"))
        root = tree.root_node
        functions: List[str] = []
        classes: Dict[str, List[str]] = {}
        routes: List[Dict[str, str]] = []

        def get_text(node):
            return node.text.decode("utf-8")

        def _traverse(node):
            if node.type == "function_declaration":
                nm = node.child_by_field_name("name")
                if nm:
                    functions.append(get_text(nm))
            elif node.type == "class_declaration":
                nm = node.child_by_field_name("name")
                if nm:
                    classes[get_text(nm)] = []
            elif node.type == "lexical_declaration":
                for ch in node.children:
                    if ch.type == "variable_declarator":
                        name_node = ch.child_by_field_name("name")
                        value_node = ch.child_by_field_name("value")
                        if name_node and value_node and value_node.type == "arrow_function":
                            functions.append(get_text(name_node))
            elif node.type == "call_expression":
                if node.child_count >= 2:
                    callee = node.child_by_field_name("function")
                    args = node.child_by_field_name("arguments")
                    if callee:
                        parts = get_text(callee).split(".")
                        if len(parts) == 2:
                            obj, method = parts
                            if method.lower() in {"get", "post", "put", "delete", "patch"}:
                                path_str = "/unknown"
                                if args and args.child_count > 0:
                                    first = args.child(0)
                                    if first.type == "string":
                                        path_str = get_text(first).strip("\"' ")
                                routes.append({"object": obj, "method": method.upper(), "path": path_str})
            for ch in node.children:
                _traverse(ch)

        _traverse(root)
        return {"language": ".js", "functions": functions, "classes": classes, "routes": routes, "complexity": len(functions) + sum(len(v) for v in classes.values())}


class FileProcessor:
    """File hashing, ignore filtering, cache checks, binary detection."""

    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

    SUPPORTED_EXTENSIONS = {
        ".py", ".rs", ".js", ".ts", ".tsx", ".jsx", ".md", ".json",
        ".yaml", ".yml", ".toml", ".sh", ".rst",
    }

    DEFAULT_IGNORE_DIRS = {
        ".git", ".svn", ".hg", ".bzr",
        "__pycache__", "*.egg-info", "venv", ".venv", "env", "virtualenv", ".virtualenv",
        ".pytest_cache", ".mypy_cache", ".coverage", "htmlcov",
        "build", "dist", ".tox", "node_modules", "target",
        "runtime/reports",
    }

    DEFAULT_IGNORE_FILES = {
        ".gitignore", "LICENSE", "README.md", "package-lock.json", "yarn.lock",
        "requirements.txt", "setup.py", "Dockerfile", ".dockerignore",
    }

    def __init__(self, project_root: Path, cache: Dict[str, Any], cache_lock: threading.Lock, additional_ignore_dirs: set) -> None:
        self.project_root = project_root
        self.cache = cache
        self.cache_lock = cache_lock
        self.ignore_dirs = set(self.DEFAULT_IGNORE_DIRS)
        if additional_ignore_dirs:
            self.ignore_dirs.update(additional_ignore_dirs)

    def hash_file(self, file_path: Path) -> str:
        try:
            with file_path.open("rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def should_exclude(self, file_path: Path) -> bool:
        try:
            rel = file_path.relative_to(self.project_root)
        except Exception:
            return True
        parts = rel.parts

        # ignore directories
        for i in range(len(parts)):
            if parts[i] in self.ignore_dirs:
                return True

        # size
        if file_path.is_file() and file_path.stat().st_size > self.MAX_FILE_SIZE_BYTES:
            return True

        # extension and file filters
        if file_path.is_file():
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                return True
            if file_path.name in self.DEFAULT_IGNORE_FILES:
                return True

            # binary sniff
            try:
                with file_path.open("rb") as f:
                    if b"\x00" in f.read(4096):
                        return True
            except Exception:
                return True
        return False


class ReportGenerator:
    """Save merged analysis and export ChatGPT context in different modes."""

    def __init__(self, project_root: Path, analysis: Dict[str, Dict[str, Any]]):
        self.project_root = project_root
        self.analysis = analysis

    def load_json(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_merged_report(self) -> Path:
        report_path = self.project_root / "project_analysis.json"
        existing = self.load_json(report_path)
        merged = {**existing, **self.analysis}
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(merged, f, indent=4)
        return report_path

    def save_single_report(self) -> Path:
        report_path = self.project_root / "project_analysis.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(self.analysis, f, indent=4)
        return report_path

    def export_context(self, split_by: str = "directory", max_files_per_chunk: int = 100, single_file: bool = False) -> None:
        reports_dir = self.project_root / "runtime" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        base = reports_dir / "project_context"

        # Build all_files structure from analysis
        all_files: Dict[str, Dict[str, Any]] = {}
        for file_path, analysis in self.analysis.items():
            if "error" in analysis:
                continue
            suffix = Path(file_path).suffix.lower()
            file_entry: Dict[str, Any] = {
                "type": "file",
                "language": self._lang_from_ext(suffix),
                "functions": analysis.get("functions", []),
                "classes": list(analysis.get("classes", {}).keys()) if isinstance(analysis.get("classes"), dict) else analysis.get("classes", []),
                "complexity": analysis.get("complexity", 0),
            }
            all_files[file_path.replace("/", "\\")] = file_entry

        if single_file:
            out = base.with_suffix(".json")
            with out.open("w", encoding="utf-8") as f:
                json.dump(all_files, f, indent=4)
            return

        # index and split strategies
        index = {
            "type": "index",
            "total_files": len(all_files),
            "project_root": str(self.project_root),
            "generated_at": str(datetime.datetime.now()),
            "chunks": [],
        }

        if split_by == "directory":
            groups: Dict[str, Dict[str, Any]] = {}
            for fp, data in all_files.items():
                parts = Path(fp).parts
                top = parts[0] if len(parts) > 1 else "_root_"
                groups.setdefault(top, {})[fp] = data
            for name, files in groups.items():
                safe = name.replace("\\", "_").replace("/", "_").replace(":", "_")
                out = reports_dir / f"project_context_{safe}.json"
                with out.open("w", encoding="utf-8") as f:
                    json.dump(files, f, indent=4)
                index["chunks"].append({"name": name, "file_count": len(files), "path": out.name})
        elif split_by == "language":
            groups: Dict[str, Dict[str, Any]] = {}
            for fp, data in all_files.items():
                lang = data.get("language", "unknown")
                groups.setdefault(lang, {})[fp] = data
            for lang, files in groups.items():
                out = reports_dir / f"project_context_{lang}.json"
                with out.open("w", encoding="utf-8") as f:
                    json.dump(files, f, indent=4)
                index["chunks"].append({"language": lang, "file_count": len(files), "path": out.name})
        else:
            items = list(all_files.items())
            chunks = [items[i:i + max_files_per_chunk] for i in range(0, len(items), max_files_per_chunk)]
            for i, chunk in enumerate(chunks, 1):
                out = reports_dir / f"project_context_chunk{i}.json"
                with out.open("w", encoding="utf-8") as f:
                    json.dump(dict(chunk), f, indent=4)
                index["chunks"].append({"chunk": i, "file_count": len(chunk), "path": out.name})

        with (reports_dir / "project_context_index.json").open("w", encoding="utf-8") as f:
            json.dump(index, f, indent=4)
        metadata = {
            "type": "metadata",
            "total_files": len(all_files),
            "project_root": str(self.project_root),
            "generated_at": str(datetime.datetime.now()),
            "languages": sorted({v.get("language", "unknown") for v in all_files.values()}),
            "file_extensions": sorted({Path(k).suffix for k in all_files.keys()}),
        }
        with (reports_dir / "project_metadata.json").open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

    def _lang_from_ext(self, ext: str) -> str:
        mapping = {
            ".py": "python", ".js": "javascript", ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript",
            ".rs": "rust", ".go": "go", ".java": "java", ".c": "c", ".cpp": "cpp", ".h": "c", ".hpp": "cpp",
            ".cs": "csharp", ".rb": "ruby", ".php": "php", ".html": "html", ".css": "css", ".md": "markdown",
            ".json": "json", ".xml": "xml", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".sh": "bash",
        }
        return mapping.get(ext.lower(), "text")


class UnifiedProjectScanner:
    """Unified scanning engine with configurable outputs."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.analysis: Dict[str, Dict[str, Any]] = {}
        self.cache = self._load_cache()
        self.cache_lock = threading.Lock()
        self.additional_ignore_dirs: set = set()
        self.language_analyzer = LanguageAnalyzer()
        self.file_processor = FileProcessor(self.project_root, self.cache, self.cache_lock, self.additional_ignore_dirs)

    def _load_cache(self) -> Dict[str, Any]:
        path = Path(CACHE_FILE)
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self) -> None:
        with Path(CACHE_FILE).open("w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=4)

    def scan_project(
        self,
        export_context: bool = False,
        split_by: str = "directory",
        max_files_per_chunk: int = 100,
        single_report_only: bool = False,
        generate_init: bool = False,
    ) -> Path:
        """Run the scan and write outputs according to flags.

        Returns: path to project_analysis.json
        """
        valid_files: List[Path] = []
        for root, _dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            if self.file_processor.should_exclude(root_path):
                continue
            for fn in files:
                fp = root_path / fn
                if fp.suffix.lower() in self.file_processor.SUPPORTED_EXTENSIONS and not self.file_processor.should_exclude(fp):
                    valid_files.append(fp)

        # cache moved files detection
        previous_files = set(self.cache.keys())
        current_files = {str(f.relative_to(self.project_root)) for f in valid_files}
        moved = {}
        missing = previous_files - current_files
        for old in previous_files:
            old_hash = self.cache.get(old, {}).get("hash")
            if not old_hash:
                continue
            for new_rel in current_files:
                new_file = self.project_root / new_rel
                if self.file_processor.hash_file(new_file) == old_hash:
                    moved[old] = new_rel
                    break
        for miss in missing:
            if miss not in moved:
                with self.cache_lock:
                    self.cache.pop(miss, None)
        for old, new_rel in moved.items():
            with self.cache_lock:
                self.cache[new_rel] = self.cache.pop(old)

        # async workers
        manager = _MultibotManager(self, num_workers=os.cpu_count() or 4)
        for fp in valid_files:
            manager.add_task(fp)
        manager.wait_for_completion()
        manager.stop_workers()
        for result in manager.results_list:
            if result is not None:
                rel, data = result
                self.analysis[rel] = data

        reporter = ReportGenerator(self.project_root, self.analysis)
        report_path = reporter.save_single_report() if single_report_only else reporter.save_merged_report()

        if export_context:
            reporter.export_context(split_by=split_by, max_files_per_chunk=max_files_per_chunk, single_file=(split_by == "none"))

        if generate_init:
            self._generate_init_files()

        self._save_cache()
        return report_path

    def process_file(self, file_path: Path) -> Optional[Tuple[str, Dict[str, Any]]]:
        try:
            rel = str(file_path.relative_to(self.project_root))
        except Exception:
            return None

        file_hash = self.file_processor.hash_file(file_path)
        with self.cache_lock:
            if rel in self.cache and self.cache[rel].get("hash") == file_hash:
                return None

        try:
            with file_path.open("r", encoding="utf-8", errors="replace") as f:
                source = f.read()
            data = self.language_analyzer.analyze(file_path, source)
            with self.cache_lock:
                self.cache[rel] = {"hash": file_hash}
            return rel, data
        except Exception as e:  # pragma: no cover (best-effort)
            return rel, {"error": str(e)}

    def _generate_init_files(self, overwrite: bool = True) -> None:
        from collections import defaultdict

        package_modules: Dict[str, List[str]] = defaultdict(list)
        for rel_path in self.analysis.keys():
            if rel_path.endswith(".py"):
                p = Path(rel_path)
                if p.name == "__init__.py":
                    continue
                package_modules[str(p.parent)].append(p.stem)

        for package, modules in package_modules.items():
            pkg_dir = self.project_root / package
            init_fp = pkg_dir / "__init__.py"
            pkg_dir.mkdir(parents=True, exist_ok=True)
            lines = [
                "# AUTO-GENERATED __init__.py",
                "# DO NOT EDIT MANUALLY - changes may be overwritten\n",
            ]
            for m in sorted(modules):
                lines.append(f"from . import {m}")
            lines.append("\n__all__ = [")
            for m in sorted(modules):
                lines.append(f"    '{m}',")
            lines.append("]\n")
            content = "\n".join(lines)
            if overwrite or not init_fp.exists():
                with init_fp.open("w", encoding="utf-8") as f:
                    f.write(content)


class _BotWorker(threading.Thread):
    def __init__(self, task_queue: queue.Queue, results_list: list, scanner: UnifiedProjectScanner):
        super().__init__(daemon=True)
        self.task_queue = task_queue
        self.results_list = results_list
        self.scanner = scanner
        self.start()

    def run(self) -> None:  # pragma: no cover (threaded)
        while True:
            file_path = self.task_queue.get()
            if file_path is None:
                break
            res = self.scanner.process_file(file_path)
            if res is not None:
                self.results_list.append(res)
            self.task_queue.task_done()


class _MultibotManager:
    def __init__(self, scanner: UnifiedProjectScanner, num_workers: int = 4):
        self.task_queue: queue.Queue = queue.Queue()
        self.results_list: list = []
        self.workers = [_BotWorker(self.task_queue, self.results_list, scanner) for _ in range(num_workers)]

    def add_task(self, file_path: Path) -> None:
        self.task_queue.put(file_path)

    def wait_for_completion(self) -> None:
        self.task_queue.join()

    def stop_workers(self) -> None:
        for _ in self.workers:
            self.task_queue.put(None)


