#!/usr/bin/env python3
"""
ProjectScanner - Unified Entry Point

Description:
    Scans local repositories and GitHub repositories, then generates
    a unified markdown report of all projects.

Features:
    - Interactive CLI menu (no flags required)
    - Direct CLI support (for automation)
    - Local project discovery + analysis with detailed info (type, scale, entry points)
    - JSON output for agent integration (--list --json)
    - GitHub public + private repo fetching
    - Pagination support (fetch ALL repos)
    - Clean markdown report output

Usage:
    Interactive:
        python run.py

    CLI (project listing):
        python run.py --list
        python run.py --list --json
        python run.py --list --base-dir ~/projects

    CLI (full scan and report):
        python run.py . --github YOUR_USERNAME

Environment:
    export GITHUB_TOKEN=your_token_here
"""

import argparse
import json
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


def _detect_project_type_and_scale(project_path: Path) -> tuple:
    """Return (type, scale, entry_points). Mimics workspace.sh logic."""
    type_map = {
        '.py': 'Python project',
        '.js': 'JavaScript project',
        '.ts': 'TypeScript project',
        '.html': 'Web application',
        '.rs': 'Rust project',
        '.go': 'Go project',
        '.java': 'Java project',
        '.kt': 'Kotlin project',
        '.cpp': 'C++ project',
        '.c': 'C project',
    }
    # Count files by extension
    ext_counts = {}
    total_files = 0
    for ext in type_map:
        ext_counts[ext] = len(list(project_path.rglob(f'*{ext}')))
        total_files += ext_counts[ext]
    
    # Dominant extension
    dominant_ext = max(ext_counts, key=ext_counts.get) if ext_counts else None
    proj_type = type_map.get(dominant_ext, 'Unknown project')
    
    # Scale: lightweight (<50 files), medium-scale (50-200), large-scale (>200)
    if total_files < 50:
        scale = 'lightweight'
    elif total_files < 200:
        scale = 'medium-scale'
    else:
        scale = 'large-scale'
    
    # Entry points: common entry files
    entry_candidates = ['main.py', 'run.py', 'app.py', 'index.js', 'index.ts', 'package.json', 'Dockerfile', 'docker-compose.yml']
    entry_points = [f for f in entry_candidates if (project_path / f).exists()]
    
    # Special: if no entry found and it's Python, check for any .py file
    if not entry_points and dominant_ext == '.py':
        py_files = list(project_path.glob('*.py'))
        if py_files:
            entry_points = [py_files[0].name]
    
    return proj_type, scale, entry_points


# ---------------------------------------------------------------------------
# LOCAL SCANNING (Detailed for --list)
# ---------------------------------------------------------------------------

def scan_local_detailed(root_path: str) -> List[Dict]:
    """Scan local directory and return detailed project info (type, scale, entry points)."""
    root = Path(root_path).expanduser().resolve()
    projects = []
    
    if not root.exists():
        print(f"[error] Path does not exist: {root}", file=sys.stderr)
        return []
    
    for child in root.iterdir():
        if child.is_dir() and not child.name.startswith('.') and _is_project_dir(child):
            proj_type, scale, entry_points = _detect_project_type_and_scale(child)
            projects.append({
                "name": child.name,
                "type": proj_type,
                "scale": scale,
                "entry_points": entry_points,
                "path": str(child),
                "last_updated": _git_last_commit_date(child) or _fs_last_modified(child),
                "description": _read_description(child),
            })
    return projects


# ---------------------------------------------------------------------------
# LOCAL SCANNING (Original for report)
# ---------------------------------------------------------------------------

def scan_local(root_path: str) -> List[Dict]:
    """Original scan_local for markdown report (simpler)."""
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
# GITHUB SCANNING
# ---------------------------------------------------------------------------

def scan_github(username: str, token: Optional[str]) -> List[Dict]:
    import urllib.request

    repos = []
    page = 1

    print("  Fetching ALL GitHub repos (public + private)...")

    while True:
        if token:
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
    parser.add_argument("local_path", nargs="?", default=None,
                        help="Local path to scan (for report mode)")
    parser.add_argument("--github", default=None,
                        help="GitHub username to fetch repos from")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"),
                        help="GitHub personal access token (or set GITHUB_TOKEN env)")
    parser.add_argument("--output", default="projects_report.md",
                        help="Output markdown file name")
    
    # NEW arguments for project listing (detailed)
    parser.add_argument("--list", action="store_true",
                        help="List projects in a directory (detailed: type, scale, entry points)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON (use with --list)")
    parser.add_argument("--base-dir", default=str(Path.home()),
                        help="Root directory to scan for projects (default: home)")

    args = parser.parse_args()

    # --- NEW: --list mode (detailed listing) ---
    if args.list:
        projects = scan_local_detailed(args.base_dir)
        if args.json:
            output = {
                "projects": projects,
                "total_count": len(projects),
                "scan_timestamp": datetime.now(timezone.utc).isoformat()
            }
            print(json.dumps(output, indent=2))
        else:
            # Human-readable table (like workspace list)
            for p in projects:
                entry_str = ", ".join(p["entry_points"]) if p["entry_points"] else "No clear entry point detected"
                print(f"{p['name']} :: {p['type']} ({p['scale']}). Entry: {entry_str}")
        return

    # --- Original interactive / report mode ---
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
