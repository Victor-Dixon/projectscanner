#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DOC_KEYS = ["readme", "prd", "roadmap", "master_task_list", "next_up"]

def run(cmd: list[str], cwd: Path) -> str:
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    return r.stdout.strip() if r.returncode == 0 else ""

def markers(repo: Path) -> dict:
    children = list(repo.iterdir()) if repo.exists() else []
    names = [p.name for p in children]
    upper = [n.upper() for n in names]
    return {
        "readme": any(n in names for n in ["README.md", "readme.md", "README.txt"]),
        "prd": any("PRD" in n for n in upper),
        "roadmap": any("ROADMAP" in n for n in upper),
        "master_task_list": "MASTER_TASK_LIST.md" in names,
        "next_up": "NEXT_UP.md" in names,
        "package_json": "package.json" in names,
        "pyproject": "pyproject.toml" in names,
        "requirements": "requirements.txt" in names,
        "pytest_ini": "pytest.ini" in names,
        "github_workflows": (repo / ".github" / "workflows").exists(),
    }

def docs_score(m: dict) -> int:
    return round((sum(1 for k in DOC_KEYS if m.get(k)) / len(DOC_KEYS)) * 100)

def scan_repo(repo: Path) -> dict:
    m = markers(repo)
    files = [p for p in repo.rglob("*") if ".git" not in p.parts and p.is_file()]
    dirs = [p for p in repo.rglob("*") if ".git" not in p.parts and p.is_dir()]
    status = run(["git", "status", "--short"], repo).splitlines()

    return {
        "name": repo.name,
        "path": str(repo),
        "generated": datetime.now(timezone.utc).isoformat(),
        "is_git": (repo / ".git").exists(),
        "branch": run(["git", "branch", "--show-current"], repo) or "NO_BRANCH",
        "head": run(["git", "rev-parse", "--short=8", "HEAD"], repo) or "NO_HEAD",
        "dirty": bool(status),
        "git_status_short": status,
        "file_count": len(files),
        "dir_count": len(dirs),
        "top_level": sorted([p.name for p in repo.iterdir() if p.name != ".git"]),
        "docs_markers": m,
        "docs_score": docs_score(m),
        "missing_docs": [k for k in DOC_KEYS if not m.get(k)],
    }

def write_bundle(repo: Path, out_root: Path) -> None:
    analysis = scan_repo(repo)
    out = out_root / repo.name
    out.mkdir(parents=True, exist_ok=True)

    context = {
        "repo": analysis["name"],
        "current_state": {
            "branch": analysis["branch"],
            "head": analysis["head"],
            "dirty": analysis["dirty"],
            "file_count": analysis["file_count"],
            "docs_score": analysis["docs_score"],
            "missing_docs": analysis["missing_docs"],
        },
        "operator_guidance": {
            "safe_next_action": "docs_refresh" if analysis["missing_docs"] else "maintain",
            "guardrails": [
                "No destructive cleanup without a promotion manifest.",
                "Commit only scoped artifacts per lane.",
                "Verify with tests or file checks before commit.",
            ],
        },
    }

    recommendations = {
        "repo": analysis["name"],
        "recommended_next_classes": (
            ["docs_refresh"] if analysis["missing_docs"] else ["no_docs_gap_detected"]
        ),
        "missing_docs": analysis["missing_docs"],
        "risk": "medium" if analysis["dirty"] else "low",
    }

    (out / "repo_analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    (out / "chatgpt_context.json").write_text(json.dumps(context, indent=2, sort_keys=True) + "\n")
    (out / "cleanup_recommendations.json").write_text(json.dumps(recommendations, indent=2, sort_keys=True) + "\n")
    (out / "docs_gap_report.md").write_text(
        f"# {analysis['name']} Docs Gap Report\n\n"
        f"- Docs score: {analysis['docs_score']}\n"
        f"- Missing docs: {', '.join(analysis['missing_docs']) or 'none'}\n\n"
        "DOCS_GAP_REPORT=PASS\n"
    )

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects-root", default=str(Path.home() / "projects"))
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--repos", nargs="*", default=None)
    args = ap.parse_args()

    root = Path(args.projects_root)
    out_root = Path(args.out_root)

    repos = args.repos or [
        p.name for p in root.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name != "_ARCHIVE"
    ]

    for name in sorted(repos, key=str.lower):
        repo = root / name
        if repo.is_dir():
            write_bundle(repo, out_root)

    print("PROJECTSCANNER_INTELLIGENCE_EXPORT=PASS")
    print(f"REPOS={len(repos)}")
    print(f"OUT_ROOT={out_root}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
