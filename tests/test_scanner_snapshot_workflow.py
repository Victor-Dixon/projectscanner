from pathlib import Path


def test_snapshot_timestamp_is_artifact_safe():
    workflow = Path(".github/workflows/scanner-snapshot.yml").read_text()

    assert "%H:%M:%S" not in workflow
    assert "%Y-%m-%dT%H-%M-%SZ" in workflow


def test_snapshot_dir_uses_safe_timestamp_variable():
    workflow = Path(".github/workflows/scanner-snapshot.yml").read_text()

    assert "SNAPSHOT_DIR=\"snapshots/${GITHUB_REF_NAME}-${TIMESTAMP}-${GITHUB_SHA::8}\"" in workflow
