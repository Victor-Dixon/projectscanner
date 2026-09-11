from pathlib import Path
import threading

from core.projectscanner.file_processor import FileProcessor


def test_explicit_runtime_scripts_scan_is_allowed(tmp_path: Path) -> None:
    scripts = tmp_path / "runtime" / "scripts"
    scripts.mkdir(parents=True)
    script = scripts / "worker.py"
    script.write_text("x = 1\n", encoding="utf-8")

    processor = FileProcessor(scripts, {}, threading.Lock(), set())

    assert processor.should_exclude(script) is False


def test_full_repo_scan_excludes_generated_runtime_state(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    state_file = repo / "runtime" / "state" / "packet.json"
    state_file.parent.mkdir(parents=True)
    state_file.write_text("{}", encoding="utf-8")
    script = repo / "runtime" / "scripts" / "worker.py"
    script.parent.mkdir(parents=True)
    script.write_text("x = 1\n", encoding="utf-8")

    processor = FileProcessor(repo, {}, threading.Lock(), set())

    assert processor.should_exclude(state_file) is True
    assert processor.should_exclude(script) is False
