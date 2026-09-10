from __future__ import annotations

import json
from pathlib import Path

from projectscanner.cli import main


def _run_scan(target: Path, output: Path) -> None:
    code = main(
        [
            "scan",
            str(target),
            "--output",
            str(output),
            "--export-context",
            "--split-by",
            "none",
            "--max-files-per-chunk",
            "1",
        ]
    )
    assert code == 0


def _chunk_bytes(output: Path) -> dict[str, bytes]:
    reports = output / "runtime" / "reports"
    return {
        path.name: path.read_bytes()
        for path in sorted(reports.glob("project_context_chunk_*.json"))
    }


def test_repeated_scan_preserves_cached_files_and_artifact_order(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    output = tmp_path / "out"
    target.mkdir()
    (target / "b.py").write_text("def beta():\n    return 2\n", encoding="utf-8")
    (target / "a.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")

    _run_scan(target, output)
    first_contract = (output / "analysis.json").read_bytes()
    first_report = (output / "project_analysis_repo.json").read_bytes()
    first_context = (output / "chatgpt_project_context_repo.json").read_bytes()
    first_chunks = _chunk_bytes(output)

    contract = json.loads(first_contract)
    assert contract["total_files"] == 2
    assert [item["path"] for item in contract["files"]] == ["a.py", "b.py"]

    _run_scan(target, output)

    assert (output / "analysis.json").read_bytes() == first_contract
    assert (output / "project_analysis_repo.json").read_bytes() == first_report
    assert (output / "chatgpt_project_context_repo.json").read_bytes() == first_context
    assert _chunk_bytes(output) == first_chunks


def test_repeated_scan_drops_deleted_file_from_current_artifacts(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    output = tmp_path / "out"
    target.mkdir()
    (target / "a.py").write_text("value = 1\n", encoding="utf-8")
    removed = target / "b.py"
    removed.write_text("value = 2\n", encoding="utf-8")

    _run_scan(target, output)
    removed.unlink()
    _run_scan(target, output)

    contract = json.loads((output / "analysis.json").read_text(encoding="utf-8"))
    report = json.loads((output / "project_analysis_repo.json").read_text(encoding="utf-8"))
    context = json.loads((output / "chatgpt_project_context_repo.json").read_text(encoding="utf-8"))

    assert contract["total_files"] == 1
    assert [item["path"] for item in contract["files"]] == ["a.py"]
    assert "b.py" not in report
    assert "b.py" not in context["analysis_details"]
