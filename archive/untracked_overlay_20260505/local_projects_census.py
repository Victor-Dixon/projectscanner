from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


PROJECTS_ROOT = Path.home() / "projects"
OUT_DIR = Path("runtime/targets")
OUT_JSON = OUT_DIR / "local_projects_census.json"
OUT_MD = OUT_DIR / "local_projects_census.md"


@dataclass(frozen=True)
class LocalProject:
    name: str
    path: str
    is_git_repo: bool
    dirty: bool
    git_branch: str
    remote_origin: str
    category: str


def run_git(path: Path, args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), *args],
            text=True,
            capture_output=True,
            timeout=10,
        )
        if completed.returncode != 0:
            return ""
        return completed.stdout.strip()
    except Exception:
        return ""


def classify(name: str) -> str:
    lower = name.lower()

    if lower in {"agenttools", "projectscanner"}:
        return "toolbelt"

    if any(x in lower for x in ["dreamos", "dream.os", "victor.os", "autodream"]):
        return "dreamos_family"

    if any(x in lower for x in ["discord", "bot"]):
        return "discord_ops"

    if any(x in lower for x in ["homeschool", "lesson", "teks", "staar"]):
        return "homeschool"

    if any(x in lower for x in ["trade", "trading", "market", "stocks"]):
        return "trading"

    return "other"


def inspect_project(path: Path) -> LocalProject:
    is_git = (path / ".git").exists()
    branch = ""
    remote = ""
    dirty = False

    if is_git:
        branch = run_git(path, ["branch", "--show-current"])
        remote = run_git(path, ["remote", "get-url", "origin"])
        dirty = bool(run_git(path, ["status", "--short"]))

    return LocalProject(
        name=path.name,
        path=str(path),
        is_git_repo=is_git,
        dirty=dirty,
        git_branch=branch,
        remote_origin=remote,
        category=classify(path.name),
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    projects = []
    for child in sorted(PROJECTS_ROOT.iterdir()):
        if child.is_dir():
            projects.append(inspect_project(child))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(PROJECTS_ROOT),
        "project_count": len(projects),
        "git_repo_count": sum(1 for p in projects if p.is_git_repo),
        "dirty_count": sum(1 for p in projects if p.dirty),
        "categories": {},
        "projects": [asdict(p) for p in projects],
    }

    for project in projects:
        payload["categories"].setdefault(project.category, 0)
        payload["categories"][project.category] += 1

    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Local Projects Census",
        "",
        f"- Root: `{PROJECTS_ROOT}`",
        f"- Projects: `{payload['project_count']}`",
        f"- Git repos: `{payload['git_repo_count']}`",
        f"- Dirty repos: `{payload['dirty_count']}`",
        "",
        "## Categories",
    ]

    for category, count in sorted(payload["categories"].items()):
        lines.append(f"- `{category}`: {count}")

    lines += ["", "## Projects"]
    for p in projects:
        dirty = "DIRTY" if p.dirty else "clean"
        git = "git" if p.is_git_repo else "no-git"
        remote = f" — {p.remote_origin}" if p.remote_origin else ""
        lines.append(f"- `{p.name}` [{p.category}] [{git}/{dirty}] `{p.path}`{remote}")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"WROTE_JSON={OUT_JSON}")
    print(f"WROTE_MD={OUT_MD}")
    print(f"PROJECT_COUNT={payload['project_count']}")
    print(f"GIT_REPO_COUNT={payload['git_repo_count']}")
    print(f"DIRTY_COUNT={payload['dirty_count']}")
    print("CATEGORIES=" + json.dumps(payload["categories"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
