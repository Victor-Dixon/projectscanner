from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scan_targets import (
    TARGETS_DIR,
    github_clone_or_fetch_plan,
    make_github_target,
    make_local_target,
    read_target_manifest,
    write_target_manifest,
)


def target_summary(target) -> dict:
    return {
        "target_id": target.target_id,
        "source_type": target.source_type,
        "name": target.name,
        "status": target.status,
        "local_path": target.local_path,
        "github_url": target.github_url,
        "ready_for_offline_scan": Path(target.local_path).exists(),
    }


def run_plan(plan: list[str], timeout: int = 120) -> list[dict]:
    results = []
    for command in plan:
        if command.startswith("# BLOCKED"):
            results.append({"command": command, "returncode": 1, "stdout": "", "stderr": "blocked"})
            break

        completed = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        results.append(
            {
                "command": command,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-2000:],
                "stderr": completed.stderr[-2000:],
            }
        )
        if completed.returncode != 0:
            break
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ProjectScanner target manager")
    sub = parser.add_subparsers(dest="command", required=True)

    local = sub.add_parser("local", help="Create local directory scan targets")
    local.add_argument("paths", nargs="+")
    local.add_argument("--out", default=str(TARGETS_DIR / "scan_targets_latest.json"))

    github = sub.add_parser("github", help="Create GitHub scan targets")
    github.add_argument("repos", nargs="+")
    github.add_argument("--branch", default="")
    github.add_argument("--out", default=str(TARGETS_DIR / "scan_targets_latest.json"))

    plan = sub.add_parser("plan-github", help="Print clone/fetch plan for GitHub targets")
    plan.add_argument("--manifest", default=str(TARGETS_DIR / "scan_targets_latest.json"))

    fetch = sub.add_parser("fetch-github", help="Execute clone/fetch for GitHub targets")
    fetch.add_argument("--manifest", default=str(TARGETS_DIR / "scan_targets_latest.json"))

    summary = sub.add_parser("summary", help="Summarize scan targets")
    summary.add_argument("--manifest", default=str(TARGETS_DIR / "scan_targets_latest.json"))

    args = parser.parse_args(argv)

    if args.command == "local":
        targets = [make_local_target(path) for path in args.paths]
        out = write_target_manifest(targets, Path(args.out))
        print(f"WROTE_SCAN_TARGETS={out}")
        print(f"TARGET_COUNT={len(targets)}")
        return 0

    if args.command == "github":
        targets = [make_github_target(repo, branch=args.branch) for repo in args.repos]
        out = write_target_manifest(targets, Path(args.out))
        print(f"WROTE_SCAN_TARGETS={out}")
        print(f"TARGET_COUNT={len(targets)}")
        return 0

    if args.command == "plan-github":
        targets = read_target_manifest(Path(args.manifest))
        for target in targets:
            if target.source_type != "github":
                continue
            print(f"\n# {target.name}")
            for command in github_clone_or_fetch_plan(target):
                print(command)
        return 0

    if args.command == "fetch-github":
        targets = read_target_manifest(Path(args.manifest))
        output = []
        for target in targets:
            if target.source_type != "github":
                continue
            output.append(
                {
                    "target": target_summary(target),
                    "results": run_plan(github_clone_or_fetch_plan(target)),
                }
            )
        print(json.dumps(output, indent=2))
        return 0

    if args.command == "summary":
        targets = read_target_manifest(Path(args.manifest))
        print(json.dumps([target_summary(t) for t in targets], indent=2, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
