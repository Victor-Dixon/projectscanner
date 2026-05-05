from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scan_targets import make_github_target, write_target_manifest


TARGETS_DIR = Path("runtime") / "targets"
RAW_PATH = TARGETS_DIR / "github_repos_raw.json"
INVENTORY_JSON = TARGETS_DIR / "github_inventory.json"
INVENTORY_MD = TARGETS_DIR / "github_inventory.md"
SCAN_TARGETS_JSON = TARGETS_DIR / "github_scan_targets_latest.json"


@dataclass(frozen=True)
class GitHubAuthStatus:
    gh_installed: bool
    authenticated: bool
    account: str
    detail: str


def run_command(args: list[str], *, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def check_gh_auth() -> GitHubAuthStatus:
    if shutil.which("gh") is None:
        return GitHubAuthStatus(
            gh_installed=False,
            authenticated=False,
            account="",
            detail="gh executable not found",
        )

    completed = run_command(["gh", "auth", "status"], timeout=20)
    output = (completed.stdout + "\n" + completed.stderr).strip()

    if completed.returncode != 0:
        return GitHubAuthStatus(
            gh_installed=True,
            authenticated=False,
            account="",
            detail=output,
        )

    account = ""
    for line in output.splitlines():
        if "Logged in to github.com account" in line:
            account = line.split("account", 1)[-1].strip()
            account = account.split("(", 1)[0].strip()
            break
        if "Logged in to github.com as" in line:
            account = line.split("as", 1)[-1].strip()
            break

    return GitHubAuthStatus(
        gh_installed=True,
        authenticated=True,
        account=account,
        detail=output,
    )


def fetch_github_repos(owner: str, *, limit: int = 200) -> list[dict[str, Any]]:
    TARGETS_DIR.mkdir(parents=True, exist_ok=True)

    completed = run_command(
        [
            "gh",
            "repo",
            "list",
            owner,
            "--limit",
            str(limit),
            "--json",
            "name,nameWithOwner,url,isPrivate,updatedAt,defaultBranchRef",
        ],
        timeout=90,
    )

    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())

    RAW_PATH.write_text(completed.stdout, encoding="utf-8")
    return json.loads(completed.stdout)


def normalize_repos(owner: str, repos: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = []

    for repo in repos:
        branch = repo.get("defaultBranchRef") or {}
        normalized.append(
            {
                "name": repo.get("name", ""),
                "name_with_owner": repo.get("nameWithOwner", ""),
                "url": repo.get("url", ""),
                "is_private": bool(repo.get("isPrivate", False)),
                "updated_at": repo.get("updatedAt", ""),
                "default_branch": branch.get("name", "") if isinstance(branch, dict) else "",
            }
        )

    return {
        "owner": owner,
        "repo_count": len(normalized),
        "private_count": sum(1 for r in normalized if r["is_private"]),
        "public_count": sum(1 for r in normalized if not r["is_private"]),
        "repos": normalized,
    }


def write_github_inventory(payload: dict[str, Any]) -> tuple[Path, Path]:
    TARGETS_DIR.mkdir(parents=True, exist_ok=True)
    INVENTORY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# GitHub Inventory",
        "",
        f"- Owner: `{payload['owner']}`",
        f"- Repos: `{payload['repo_count']}`",
        f"- Private: `{payload['private_count']}`",
        f"- Public: `{payload['public_count']}`",
        "",
        "## Repos",
    ]

    for repo in payload["repos"]:
        visibility = "private" if repo["is_private"] else "public"
        lines.append(
            f"- `{repo['name_with_owner']}` [{visibility}] "
            f"branch=`{repo['default_branch']}` updated=`{repo['updated_at']}`"
        )

    INVENTORY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return INVENTORY_JSON, INVENTORY_MD


def write_github_scan_targets(payload: dict[str, Any]) -> Path:
    targets = []

    for repo in payload["repos"]:
        branch = repo.get("default_branch") or ""
        targets.append(make_github_target(repo["name_with_owner"], branch=branch))

    return write_target_manifest(targets, SCAN_TARGETS_JSON)


def refresh_github_sources(owner: str, *, limit: int = 200) -> dict[str, Any]:
    auth = check_gh_auth()
    if not auth.gh_installed:
        raise RuntimeError("gh is not installed")
    if not auth.authenticated:
        raise RuntimeError("gh is installed but not authenticated. Run: gh auth login")

    repos = fetch_github_repos(owner, limit=limit)
    payload = normalize_repos(owner, repos)
    inventory_json, inventory_md = write_github_inventory(payload)
    scan_targets = write_github_scan_targets(payload)

    return {
        "owner": owner,
        "account": auth.account,
        "repo_count": payload["repo_count"],
        "private_count": payload["private_count"],
        "public_count": payload["public_count"],
        "inventory_json": str(inventory_json),
        "inventory_md": str(inventory_md),
        "scan_targets": str(scan_targets),
    }
