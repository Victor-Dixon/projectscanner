import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.projectscanner.workflow_mode import (
    derive_workflow_mode,
    normalize_workflow_mode,
)


def test_normalize_workflow_mode_expected_values():
    assert normalize_workflow_mode("nightly") == "nightly"
    assert normalize_workflow_mode("pull_request") == "pr"
    assert normalize_workflow_mode("tag") == "release"
    assert normalize_workflow_mode("main") == "main"


def test_normalize_workflow_mode_alias_and_fallback_behavior():
    assert normalize_workflow_mode("workflow_dispatch") == "manual"
    assert normalize_workflow_mode("unknown") == "manual"
    assert normalize_workflow_mode(None) == "manual"
    assert normalize_workflow_mode("") == "manual"


def test_derive_workflow_mode_from_github_context():
    assert derive_workflow_mode("schedule", None, None) == "nightly"
    assert derive_workflow_mode("pull_request", None, None) == "pr"
    assert derive_workflow_mode("push", "tag", "v1.0.0") == "release"
    assert derive_workflow_mode("push", "branch", "main") == "main"
    assert derive_workflow_mode("workflow_dispatch", "branch", "feature") == "manual"
