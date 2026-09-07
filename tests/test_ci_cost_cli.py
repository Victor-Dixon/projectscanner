"""Exercise the existing CLI dispatch without importing unrelated scanner dependencies."""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest


def _cli(monkeypatch):
    # The real CLI is loaded unchanged. Only unrelated legacy imports are stubbed.
    package = types.ModuleType("projectscanner")
    package.__path__ = []
    monkeypatch.setitem(sys.modules, "projectscanner", package)
    core = types.ModuleType("core.projectscanner")
    core.ProjectScanner = object
    core.build_snapshot_analysis = lambda data: data
    monkeypatch.setitem(sys.modules, "core.projectscanner", core)
    for name, exports in {
        "export_intelligence": ["export_portfolio"],
        "history": ["fetch_recent_snapshots", "file_count_delta", "format_history_table"],
        "ingest": ["ingest_snapshot"],
        "planning_contract": ["inspect_planning_contract"],
    }.items():
        module = types.ModuleType("projectscanner." + name)
        for export in exports:
            setattr(module, export, lambda *args, **kwargs: None)
        if name == "ingest":
            module.SnapshotValidationError = type("SnapshotValidationError", (ValueError,), {})
        monkeypatch.setitem(sys.modules, module.__name__, module)
    path = Path(__file__).parents[1] / "src/projectscanner/cli.py"
    spec = importlib.util.spec_from_file_location("projectscanner.cli", path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_ci_cost_cli_single_and_portfolio(tmp_path, monkeypatch, capsys):
    cli = _cli(monkeypatch)
    projects = tmp_path / "projects"
    repo = projects / "repo"
    workflows = repo / ".github/workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("on: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n")
    output = tmp_path / "report.json"
    assert cli.main(["ci-cost", str(repo), "--output", str(output)]) == 0
    assert json.loads(output.read_text())["summary"]["github_hosted_jobs"] == 1
    assert "CI_COST_SCAN=PASS" in capsys.readouterr().out
    assert cli.main(["ci-cost", "--projects-root", str(projects), "--repos", "repo", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["repo_count"] == 1
    assert "ci-cost" in cli.build_parser().format_help()


def test_ci_cost_cli_fails_closed(tmp_path, monkeypatch, capsys):
    cli = _cli(monkeypatch)
    repo = tmp_path / "repo"
    workflow = repo / ".github/workflows/ci.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("on: push\njobs: [\n")
    assert cli.main(["ci-cost", str(repo), "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["evidence_complete"] is False
    assert cli.main(["ci-cost", str(repo), "--projects-root", str(tmp_path)]) == 2
    assert cli.main(["ci-cost", "--repos", "repo"]) == 2
    assert cli.main(["ci-cost", str(tmp_path / "missing")]) == 2
    assert cli.main(["ci-cost", str(repo), "--usage-json", str(tmp_path / "missing.json")]) == 2
