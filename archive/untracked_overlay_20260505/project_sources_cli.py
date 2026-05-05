from __future__ import annotations

import argparse
import json

from github_sources import check_gh_auth, refresh_github_sources


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ProjectScanner source inventory manager")
    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("gh-auth", help="Check GitHub CLI auth")
    auth.set_defaults(command="gh-auth")

    refresh = sub.add_parser("refresh", help="Refresh GitHub source inventory and scan targets")
    refresh.add_argument("--owner", required=True)
    refresh.add_argument("--limit", type=int, default=200)

    args = parser.parse_args(argv)

    if args.command == "gh-auth":
        status = check_gh_auth()
        print(json.dumps(status.__dict__, indent=2, sort_keys=True))
        return 0 if status.gh_installed and status.authenticated else 1

    if args.command == "refresh":
        result = refresh_github_sources(args.owner, limit=args.limit)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
