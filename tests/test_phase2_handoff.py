import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.projectscanner import ProjectScanner


def test_context_chunk_exports_directory_and_none(tmp_path):
    root = tmp_path / "proj"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    (root / "b.js").write_text("function b() { return 2; }\n", encoding="utf-8")

    scanner = ProjectScanner(project_root=root)
    scanner.scan_project(export_context=True, split_output_by="directory", max_files_per_chunk=1)

    reports_dir = root / "runtime" / "reports"
    index_path = reports_dir / "project_context_index.json"
    assert index_path.exists()
    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert index["total_files"] >= 2
    assert len(index["chunks"]) >= 1

    scanner.scan_project(export_context=True, split_output_by="none", max_files_per_chunk=1)
    index2 = json.loads(index_path.read_text(encoding="utf-8"))
    assert len(index2["chunks"]) >= 2


def test_bare_repo_metadata_export(tmp_path):
    bare = tmp_path / "mirror.git"
    subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True)

    scanner = ProjectScanner(project_root=bare)
    scanner.scan_project()

    out = bare.parent / "_scanner_reports" / "mirror" / "bare_repo_metadata.json"
    assert out.exists()
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["type"] == "bare_repo_metadata"


def test_main_uses_ssot_imports():
    main_text = Path("main.py").read_text(encoding="utf-8")
    assert "from core.projectscanner import ProjectScanner" in main_text
    assert "src.core.scanner.unified_scanner" not in main_text
    assert "scripts.scanners.quick_scanner" not in main_text


def test_no_direct_scanner_module_imports():
    python_files = list(Path("src").rglob("*.py")) + list(Path("tests").rglob("*.py"))
    banned_imports = (
        "from core.projectscanner.scanner import ProjectScanner",
        "from core.projectscanner.language_analyzer import LanguageAnalyzer",
    )
    allowed_files = {"tests/test_phase2_handoff.py"}

    for file_path in python_files:
        relative = file_path.as_posix()
        if relative in allowed_files:
            continue
        content = file_path.read_text(encoding="utf-8")
        for banned_import in banned_imports:
            assert banned_import not in content, f"{relative} uses non-SSOT import: {banned_import}"
