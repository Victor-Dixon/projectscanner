import ast
import re
from pathlib import Path
from typing import Any, Dict, List


class LanguageAnalyzer:
    """SSOT language analyzer used by ProjectScanner.

    Keeps parsing logic lightweight and deterministic for Python/JS/Rust files.
    """

    JS_FUNC_RE = re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    JS_ARROW_RE = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\([^)]*\)\s*=>")
    JS_CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)")

    RUST_FN_RE = re.compile(r"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    RUST_STRUCT_RE = re.compile(r"\bstruct\s+([A-Za-z_][A-Za-z0-9_]*)")
    RUST_IMPL_RE = re.compile(r"\bimpl\s+([A-Za-z_][A-Za-z0-9_]*)")

    def analyze_file(self, file_path: Path, source_code: str) -> Dict[str, Any]:
        suffix = file_path.suffix.lower()
        if suffix == ".py":
            return self._analyze_python(source_code)
        if suffix in {".js", ".jsx", ".ts", ".tsx"}:
            return self._analyze_js(source_code, suffix)
        if suffix == ".rs":
            return self._analyze_rust(source_code)
        return {
            "language": suffix or "unknown",
            "functions": [],
            "classes": [],
            "routes": [],
            "complexity": 0,
            "lint": [],
        }

    def _analyze_python(self, source_code: str) -> Dict[str, Any]:
        tree = ast.parse(source_code)
        functions: List[str] = []
        classes: List[str] = []
        routes: List[Dict[str, str]] = []
        complexity = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
                complexity += 1
                node_routes = self._extract_routes(node)
                routes.extend(node_routes)
                if node_routes:
                    complexity += 1
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
                complexity += 1
            elif isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.BoolOp, ast.IfExp)):
                complexity += 1

        return {
            "language": ".py",
            "functions": sorted(set(functions)),
            "classes": sorted(set(classes)),
            "routes": routes,
            "complexity": complexity,
            "lint": [],
        }

    def _extract_routes(self, node: ast.AST) -> List[Dict[str, str]]:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        extracted: List[Dict[str, str]] = []

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            if decorator.func.attr != "route":
                continue

            path = ""
            methods = ["GET"]
            if decorator.args and isinstance(decorator.args[0], ast.Constant) and isinstance(decorator.args[0].value, str):
                path = decorator.args[0].value

            for kw in decorator.keywords:
                if kw.arg != "methods" or not isinstance(kw.value, (ast.List, ast.Tuple)):
                    continue
                candidate: List[str] = []
                for item in kw.value.elts:
                    if isinstance(item, ast.Constant) and isinstance(item.value, str):
                        candidate.append(item.value.upper())
                if candidate:
                    methods = candidate

            for method in methods:
                extracted.append({"function": node.name, "path": path, "method": method})

        return extracted

    def _analyze_js(self, source_code: str, suffix: str) -> Dict[str, Any]:
        functions = set(self.JS_FUNC_RE.findall(source_code))
        functions.update(self.JS_ARROW_RE.findall(source_code))
        classes = set(self.JS_CLASS_RE.findall(source_code))

        complexity_tokens = ["if", "for", "while", "catch", "&&", "||", "?"]
        complexity = sum(source_code.count(tok) for tok in complexity_tokens)

        return {
            "language": suffix,
            "functions": sorted(functions),
            "classes": sorted(classes),
            "routes": [],
            "complexity": complexity,
            "lint": [],
        }

    def _analyze_rust(self, source_code: str) -> Dict[str, Any]:
        functions = set(self.RUST_FN_RE.findall(source_code))
        classes = set(self.RUST_STRUCT_RE.findall(source_code))
        classes.update(self.RUST_IMPL_RE.findall(source_code))
        complexity = sum(source_code.count(tok) for tok in ["if ", "match ", "while ", "for ", "&&", "||"])

        return {
            "language": ".rs",
            "functions": sorted(functions),
            "classes": sorted(classes),
            "routes": [],
            "complexity": complexity,
            "lint": [],
        }
