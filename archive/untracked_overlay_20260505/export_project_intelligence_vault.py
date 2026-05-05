from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


PROJECTSCANNER_ROOT = Path.home() / "projects" / "projectscanner"
VAULT_ROOT = Path.home() / "projects" / "DreamVault" / "data" / "project_intelligence"

EXPORT_FILES = [
    ("runtime/targets/github_inventory.json", "github_inventory.json"),
    ("runtime/targets/github_scan_targets_latest.json", "github_scan_targets_latest.json"),
    ("runtime/targets/local_projects_census.json", "local_projects_census.json"),
    ("runtime/targets/local_scan_targets_latest.json", "local_scan_targets_latest.json"),
    ("runtime/tasks/master_project_task_list.json", "master_project_task_list.json"),
    ("runtime/tasks/next_up.json", "next_up.json"),
    ("runtime/tasks/project_artifact_standard_report.json", "project_artifact_standard_report.json"),
]


def copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def copytree_replace(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    return True


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    latest_dir = VAULT_ROOT / "latest"
    snapshot_dir = VAULT_ROOT / "snapshots" / stamp

    VAULT_ROOT.mkdir(parents=True, exist_ok=True)
    latest_dir.mkdir(parents=True, exist_ok=True)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    missing = []

    for rel_src, name in EXPORT_FILES:
        src = PROJECTSCANNER_ROOT / rel_src
        for base in [latest_dir, snapshot_dir]:
            ok = copy_if_exists(src, base / name)
        if src.exists():
            copied.append(rel_src)
        else:
            missing.append(rel_src)

    artifacts_src = PROJECTSCANNER_ROOT / "runtime" / "project_artifacts"
    artifacts_latest = VAULT_ROOT / "project_artifacts"
    artifacts_snapshot = snapshot_dir / "project_artifacts"

    artifacts_copied = copytree_replace(artifacts_src, artifacts_latest)
    if artifacts_copied:
        copytree_replace(artifacts_src, artifacts_snapshot)

    manifest = {
        "generated_at": generated_at,
        "snapshot": stamp,
        "vault_root": str(VAULT_ROOT),
        "source_root": str(PROJECTSCANNER_ROOT),
        "latest_dir": str(latest_dir),
        "snapshot_dir": str(snapshot_dir),
        "copied": copied,
        "missing": missing,
        "project_artifacts_copied": artifacts_copied,
    }

    (VAULT_ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (snapshot_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    readme = """# Project Intelligence Vault

This folder stores exported ProjectScanner intelligence snapshots inside DreamVault.

ProjectScanner generates data. This vault preserves history.

## Folders

- `latest/` — current exported inventory/task state
- `snapshots/` — timestamped historical exports
- `project_artifacts/` — latest standardized per-project artifact library

## Source

Generated from `~/projects/projectscanner`.
"""
    (VAULT_ROOT / "README.md").write_text(readme, encoding="utf-8")

    print(f"VAULT_ROOT={VAULT_ROOT}")
    print(f"SNAPSHOT={stamp}")
    print(f"LATEST_DIR={latest_dir}")
    print(f"SNAPSHOT_DIR={snapshot_dir}")
    print(f"COPIED={len(copied)}")
    print(f"MISSING={len(missing)}")
    print(f"PROJECT_ARTIFACTS_COPIED={artifacts_copied}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
