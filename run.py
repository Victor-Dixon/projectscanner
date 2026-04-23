#!/usr/bin/env python3
"""
ProjectScanner - Unified Entry Point

Description:
    Scans local repositories and GitHub repositories, then generates
    a unified markdown report of all projects.

Features:
    - Interactive CLI menu (no flags required)
    - Direct CLI support (for automation)
    - Local project discovery + analysis
    - GitHub public + private repo fetching
    - Pagination support (fetch ALL repos)
    - Clean markdown report output

Usage:
    Interactive:
        python run.py

    CLI:
        python run.py . --github YOUR_USERNAME

Environment:
    export GITHUB_TOKEN=your_token_here
"""

import argparse
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

# Ensure local src/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from core.projectscanner import ProjectScanner


# ---------------------------------------------------------------------------
# INTERACTIVE MODE
# ---------------------------------------------------------------------------

def interactive_menu():
    print("\n=== ProjectScanner ===\n")
    print("1) Scan local projects")
    print("2) Scan GitHub repos")
    print("3) Scan both")
    print("4) Exit\n")

    choice = input("Select option: ").strip()

    if choice == "1":
        path = input("Local path (default: .): ").strip() or "."
        return {"local": path, "github": None}

    elif choice == "2":
        username = input("GitHub username: ").strip()
        return {"local": None, "github": username}

    elif choice == "3":
        path = input("Local path (default: .): ").strip() or "."
        username = input("GitHub username: ").strip()
        return {"local": path, "github": username}

    else:
        print("Exiting.")
        sys.exit(0)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _git_last_commit_date(path: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "log", "-1", "--format=%ci"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out[:10] if out else ""
    except:
        return ""


def _fs_last_modified(path: Path) -> str:
    try:
        latest = max(
            (p.stat().st_mtime for p in path.rglob("*") if p.is_file()),
            default=None,
        )
        if latest:
            return datetime.fromtimestamp(latest, tz=timezone.utc).strftime("%Y-%m-%d")
    except:
        pass
    return ""


def _dominant_language(analysis: Dict) -> str:
    counts = {}
    for f in analysis.values():
        lang = f.get("language")
        if lang:
            counts[lang] = counts.get(lang, 0) + 1
    return max(counts, key=counts.get) if counts else "Unknown"


def _read_description(path: Path) -> str:
    for name in ["README.md", "README.txt", "README"]:
        f = path / name
        if f.exists():
            try:
                for line in f.read_text(errors="ignore").splitlines():
                    line = line.strip("# ").strip()
                    if line:
                        return line[:200]
            except:
                pass
    return ""


def _is_project_dir(path: Path) -> bool:
    markers = ["package.json", "pyproject.toml", ".git"]
    for m in markers:
        if (path / m).exists():
            return True

    for f in path.iterdir():
        if f.suffix in [".py", ".js", ".ts"]:
            return True

    return False


# ---------------------------------------------------------------------------
# LOCAL SCANNING
# ---------------------------------------------------------------------------

def scan_local(root_path: str) -> List[Dict]:
    root = Path(root_path).resolve()
    projects = []

    if not root.exists():
        print(f"[error] Path does not exist: {root}")
        return []

    for child in root.iterdir():
        if child.is_dir() and _is_project_dir(child):
            print(f"  Scanning: {child}")
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    scanner = ProjectScanner(str(child), tmp)
                    analysis = scanner.scan_project()

                projects.append({
                    "name": child.name,
                    "language": _dominant_language(analysis),
                    "last_updated": _git_last_commit_date(child) or _fs_last_modified(child),
                    "description": _read_description(child),
                    "path": str(child),
                })

            except Exception as e:
                print(f"  [warn] Failed: {e}")

    return projects


# ---------------------------------------------------------------------------
# GITHUB SCANNING (FIXED)
# ---------------------------------------------------------------------------

def scan_github(username: str, token: Optional[str]) -> List[Dict]:
    import urllib.request
    import json

    repos = []
    page = 1

    print("  Fetching ALL GitHub repos (public + private)...")

    while True:
        if token:
            # ✅ FIXED: visibility=all + affiliation=owner
            url = f"https://api.github.com/user/repos?visibility=all&affiliation=owner&per_page=100&page={page}"
        else:
            url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"

        req = urllib.request.Request(url)

        if token:
            req.add_header("Authorization", f"Bearer {token}")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"[warn] GitHub API error: {e}")
            break

        if not data:
            break

        repos.extend(data)
        page += 1

    projects = []

    for repo in repos:
        projects.append({
            "name": repo.get("name"),
            "language": repo.get("language") or "Unknown",
            "last_updated": (repo.get("updated_at") or "")[:10],
            "description": repo.get("description") or "",
            "path": repo.get("html_url"),
        })

    return projects


# ---------------------------------------------------------------------------
# REPORT GENERATION
# ---------------------------------------------------------------------------

def generate_report(projects: List[Dict], output="projects_report.md"):
    lines = ["# Project Index", ""]

    if not projects:
        lines.append("_No projects found._")

    for p in projects:
        lines.append(f"## {p['name']}")
        lines.append(f"- Language: {p['language']}")
        lines.append(f"- Last Updated: {p['last_updated'] or 'N/A'}")
        lines.append(f"- Description: {p['description'] or 'N/A'}")
        lines.append(f"- Path: {p['path']}")
        lines.append("")

    Path(output).write_text("\n".join(lines), encoding="utf-8")

    print(f"\n✅ Report written: {output}")
    print(f"   {len(projects)} project(s) indexed.")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ProjectScanner CLI")
    parser.add_argument("local_path", nargs="?", default=None)
    parser.add_argument("--github", default=None)
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--output", default="projects_report.md")

    args = parser.parse_args()

    # Interactive fallback
    if not args.local_path and not args.github:
        user = interactive_menu()
        args.local_path = user["local"]
        args.github = user["github"]

    all_projects = []

    # Local
    if args.local_path:
        print(f"\n🔍 Scanning local: {Path(args.local_path).resolve()}")
        local = scan_local(args.local_path)
        print(f"   Found {len(local)} local project(s)")
        all_projects.extend(local)

    # GitHub
    if args.github:
        print(f"\n🔍 Fetching GitHub repos for: {args.github}")
        gh = scan_github(args.github, args.token)
        print(f"   Found {len(gh)} GitHub repo(s)")
        all_projects.extend(gh)

    generate_report(all_projects, args.output)


if __name__ == "__main__":
    main()
