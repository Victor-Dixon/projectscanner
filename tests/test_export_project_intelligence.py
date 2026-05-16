import json
import subprocess
from pathlib import Path

from scripts import export_project_intelligence as epi


def test_docs_markers_detect_core_docs(tmp_path):
    repo = tmp_path / "Example"
    repo.mkdir()
    (repo / "README.md").write_text("# Example\n")
    (repo / "PRD.md").write_text("# PRD\n")
    (repo / "ROADMAP.md").write_text("# Roadmap\n")
    (repo / "MASTER_TASK_LIST.md").write_text("# Tasks\n")
    (repo / "NEXT_UP.md").write_text("# Next\n")

    m = epi.markers(repo)
    assert m["readme"]
    assert m["prd"]
    assert m["roadmap"]
    assert m["master_task_list"]
    assert m["next_up"]
    assert epi.docs_score(m) == 100


def test_write_bundle_creates_chatgpt_context(tmp_path):
    repo = tmp_path / "Example"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    (repo / "README.md").write_text("# Example\n")

    out = tmp_path / "out"
    epi.write_bundle(repo, out)

    assert (out / "Example" / "repo_analysis.json").exists()
    assert (out / "Example" / "chatgpt_context.json").exists()
    assert (out / "Example" / "cleanup_recommendations.json").exists()
    assert (out / "Example" / "docs_gap_report.md").exists()

    data = json.loads((out / "Example" / "chatgpt_context.json").read_text())
    assert data["repo"] == "Example"
    assert "missing_docs" in data["current_state"]
