from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PROJECTS_ROOT = Path.home() / "projects"
RUNTIME_DIR = Path("runtime")
TARGETS_DIR = RUNTIME_DIR / "targets"
CACHE_DIR = RUNTIME_DIR / "github_cache"
ARTIFACTS_DIR = RUNTIME_DIR / "project_artifacts"


@dataclass(frozen=True)
class ScanTarget:
    target_id: str
    source_type: str
    name: str
    local_path: str
    github_url: str
    owner: str
    repo: str
    branch: str
    status: str
    metadata: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"[^A-Za-z0-9._/-]+", "_", value)
    value = value.replace("/", "__")
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown"


def parse_github_repo(value: str) -> tuple[str, str, str]:
    """
    Returns owner, repo, normalized HTTPS URL.

    Accepts:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    - owner/repo
    """
    raw = value.strip()

    if raw.startswith("git@github.com:"):
        rest = raw.removeprefix("git@github.com:")
        rest = rest.removesuffix(".git")
        owner, repo = rest.split("/", 1)
        return owner, repo, f"https://github.com/{owner}/{repo}.git"

    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(parts) < 2 or "github.com" not in parsed.netloc.lower():
            raise ValueError(f"not a GitHub repo URL: {value}")
        owner, repo = parts[0], parts[1].removesuffix(".git")
        return owner, repo, f"https://github.com/{owner}/{repo}.git"

    if "/" in raw:
        owner, repo = raw.split("/", 1)
        repo = repo.removesuffix(".git")
        return owner, repo, f"https://github.com/{owner}/{repo}.git"

    raise ValueError(f"cannot parse GitHub repo target: {value}")


def make_local_target(path: str | Path) -> ScanTarget:
    root = Path(path).expanduser().resolve()
    if not root.exists():
        status = "missing"
    elif not root.is_dir():
        status = "not_directory"
    else:
        status = "ready"

    name = root.name
    return ScanTarget(
        target_id=f"local::{slug(str(root))}",
        source_type="local",
        name=name,
        local_path=str(root),
        github_url="",
        owner="",
        repo=name,
        branch="",
        status=status,
        metadata={
            "created_at": utc_now(),
            "exists": root.exists(),
            "is_git_repo": (root / ".git").exists(),
        },
    )


def make_github_target(repo_ref: str, *, branch: str = "", clone_root: Path | None = None) -> ScanTarget:
    owner, repo, url = parse_github_repo(repo_ref)
    clone_root = clone_root or (PROJECTS_ROOT / "_github_sources")
    local_path = clone_root / owner / repo

    if local_path.exists() and (local_path / ".git").exists():
        status = "cached_clone"
    elif local_path.exists():
        status = "path_exists_not_git"
    else:
        status = "not_cloned"

    return ScanTarget(
        target_id=f"github::{owner}/{repo}",
        source_type="github",
        name=f"{owner}/{repo}",
        local_path=str(local_path),
        github_url=url,
        owner=owner,
        repo=repo,
        branch=branch,
        status=status,
        metadata={
            "created_at": utc_now(),
            "clone_root": str(clone_root),
            "offline_capable": local_path.exists(),
        },
    )


def write_target_manifest(targets: list[ScanTarget], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": utc_now(),
        "target_count": len(targets),
        "targets": [asdict(t) for t in targets],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def read_target_manifest(path: Path) -> list[ScanTarget]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [ScanTarget(**item) for item in raw.get("targets", [])]


def github_clone_or_fetch_plan(target: ScanTarget) -> list[str]:
    if target.source_type != "github":
        raise ValueError("clone/fetch plan only supports github targets")

    local_path = Path(target.local_path)
    branch_args = f"--branch {target.branch}" if target.branch else ""

    if not local_path.exists():
        return [
            f"mkdir -p {local_path.parent!s}",
            f"git clone {branch_args} {target.github_url} {local_path!s}".replace("  ", " "),
        ]

    if (local_path / ".git").exists():
        return [
            f"cd {local_path!s}",
            "git fetch --all --prune",
            f"git checkout {target.branch}" if target.branch else "git status --short",
            "git pull --ff-only",
        ]

    return [
        f"# BLOCKED: {local_path!s} exists but is not a git repo",
    ]


def materialize_github_target(target: ScanTarget, *, execute: bool = False, timeout: int = 120) -> dict[str, Any]:
    plan = github_clone_or_fetch_plan(target)

    result: dict[str, Any] = {
        "target_id": target.target_id,
        "execute": execute,
        "plan": plan,
        "ok": True,
        "commands": [],
    }

    if not execute:
        return result

    for command in plan:
        if command.startswith("# BLOCKED"):
            result["ok"] = False
            result["commands"].append({"command": command, "returncode": 1, "stdout": "", "stderr": "blocked"})
            break

        completed = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        result["commands"].append(
            {
                "command": command,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-2000:],
                "stderr": completed.stderr[-2000:],
            }
        )
        if completed.returncode != 0:
            result["ok"] = False
            break

    return result


def artifact_dir_for_target(target: ScanTarget) -> Path:
    if target.source_type == "github":
        return ARTIFACTS_DIR / "github" / target.owner / target.repo
    return ARTIFACTS_DIR / "local" / slug(target.name)


def target_summary(target: ScanTarget) -> dict[str, Any]:
    artifact_dir = artifact_dir_for_target(target)
    return {
        "target_id": target.target_id,
        "source_type": target.source_type,
        "name": target.name,
        "status": target.status,
        "local_path": target.local_path,
        "github_url": target.github_url,
        "artifact_dir": str(artifact_dir),
        "ready_for_offline_scan": Path(target.local_path).exists(),
    }
