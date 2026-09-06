"""Tests for the unified projectscanner CLI."""

from __future__ import annotations

import json
import subprocess

import pytest

from projectscanner.cli import build_parser, main


def test_cli_help_lists_subcommands():
    parser = build_parser()
    help_text = parser.format_help()
    for command in ("scan", "export", "planning", "hygiene", "ingest", "history", "gui"):
        assert command in help_text


def test_scan_writes_analysis_json(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()
    (project / "sample.py").write_text("def sample():\n    return 1\n", encoding="utf-8")
    out = tmp_path / "out"

    code = main(["scan", str(project), "--output", str(out)])
    assert code == 0
    assert (out / "analysis.json").exists()

    payload = json.loads((out / "analysis.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["total_files"] >= 1
    assert isinstance(payload["files"], list)


def test_scan_missing_path_returns_error(tmp_path):
    code = main(["scan", str(tmp_path / "missing")])
    assert code == 1


def test_hygiene_cli_writes_snapshot(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "cli@example.invalid"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "CLI Test"],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "-C", str(repo), "branch", "-M", "master"], check=True, capture_output=True)
    (repo / "README.md").write_text("demo\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "baseline"], check=True, capture_output=True)

    out = tmp_path / "hygiene.json"
    code = main(
        [
            "hygiene",
            str(repo),
            "--canonical-branch",
            "master",
            "--output",
            str(out),
        ]
    )

    assert code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema"] == "projectscanner_fleet_hygiene_snapshot.v1"
    assert payload["repo"]["canonical_branch"] == "master"
    assert payload["policy"]["scanner_mutations_made"] is False


def test_history_empty_db(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code = main(["history", "--last", "5"])
    assert code == 0


def test_ingest_rejects_malformed_analysis(tmp_path):
    snapshot = tmp_path / "snap"
    snapshot.mkdir()
    (snapshot / "metadata.json").write_text(
        json.dumps({"commit_sha": "abc123def456"}),
        encoding="utf-8",
    )
    (snapshot / "analysis.json").write_text(json.dumps({"bad": True}), encoding="utf-8")

    code = main(["ingest", str(snapshot)])
    assert code == 1


def test_ingest_accepts_valid_snapshot(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    snapshot = tmp_path / "snap"
    snapshot.mkdir()
    (snapshot / "metadata.json").write_text(
        json.dumps({"commit_sha": "abc123def456", "scan_mode": "pr", "timestamp": "2026-01-01"}),
        encoding="utf-8",
    )
    (snapshot / "analysis.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "total_files": 1,
                "files": [{"path": "a.py", "language": ".py", "functions": 1, "classes": 0, "loc": 1}],
                "issues": [],
            }
        ),
        encoding="utf-8",
    )

    code = main(["ingest", str(snapshot), "--repo", "demo"])
    assert code == 0
    assert (tmp_path / "scanner_history.db").exists()


@pytest.mark.skipif(
    subprocess.run(["which", "projectscanner"], capture_output=True, check=False).returncode != 0,
    reason="console script not installed",
)
def test_console_script_installed():
    result = subprocess.run(["projectscanner", "--help"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "scan" in result.stdout
