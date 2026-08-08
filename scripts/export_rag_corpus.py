from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

SCHEMA_VERSION = "dreamos.rag.document.v1"
SUPPORTED_SUFFIXES = {".md", ".txt", ".py", ".json", ".jsonl", ".yaml", ".yml", ".toml"}
EXCLUDED_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}

DOMAIN_HINTS = {
    "dreamos_core": {"dreamos", "dream.os", "dreamos-brain", "planner", "agent", "lease", "runtime"},
    "tooling": {"agenttools", "projectscanner", "scanner", "tooling"},
    "websites": {"website", "websites", "deploy", "domain", "frontend", "hostinger"},
    "trading": {"trading", "trade", "tsla", "bot-lab", "bot_lab", "broker"},
    "homeschool": {"homeschool", "school", "learning", "curriculum"},
}

ALIASES = {
    "Dream.OS": "DreamOS",
    "Dream OS": "DreamOS",
    "dream.os": "DreamOS",
    "ProjectScanner": "projectscanner",
    "project scanner": "projectscanner",
}


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def discover_files(repo: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(repo).as_posix().lower())


def classify_domain(repo_name: str, relative_path: str) -> str:
    haystack = f"{repo_name} {relative_path}".lower()
    best_domain = "general"
    best_score = 0
    for domain, hints in DOMAIN_HINTS.items():
        score = sum(1 for hint in hints if hint in haystack)
        if score > best_score:
            best_domain = domain
            best_score = score
    return best_domain


def terminology_hits(text: str) -> dict[str, str]:
    hits: dict[str, str] = {}
    lower = text.lower()
    for alias, canonical in ALIASES.items():
        if alias.lower() in lower:
            hits[alias] = canonical
    return hits


def read_text(path: Path, max_bytes: int) -> tuple[str, bool]:
    raw = path.read_bytes()
    truncated = len(raw) > max_bytes
    if truncated:
        raw = raw[:max_bytes]
    return raw.decode("utf-8", errors="replace"), truncated


def repo_provenance(repo: Path) -> dict[str, str]:
    return {
        "branch": run(["git", "branch", "--show-current"], repo) or "NO_BRANCH",
        "head": run(["git", "rev-parse", "HEAD"], repo) or "NO_HEAD",
        "remote": run(["git", "config", "--get", "remote.origin.url"], repo) or "NO_REMOTE",
    }


def build_record(repo: Path, path: Path, authority: str, max_bytes: int) -> dict:
    relative = path.relative_to(repo).as_posix()
    raw = path.read_bytes()
    text, truncated = read_text(path, max_bytes=max_bytes)
    source_digest = sha256_bytes(raw)
    content_digest = sha256_bytes(text.encode("utf-8"))
    provenance = repo_provenance(repo)

    return {
        "schema_version": SCHEMA_VERSION,
        "document_id": f"sha256:{source_digest}",
        "repo": repo.name,
        "path": relative,
        "type": path.suffix.lower().lstrip("."),
        "domain": classify_domain(repo.name, relative),
        "authority": authority,
        "source_sha256": source_digest,
        "content_sha256": content_digest,
        "content": text,
        "truncated": truncated,
        "terminology": terminology_hits(text),
        "provenance": provenance,
    }


def export_repo(repo: Path, output: Path, authority: str, max_bytes: int) -> int:
    files = discover_files(repo)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for path in files:
            record = build_record(repo, path, authority=authority, max_bytes=max_bytes)
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    return len(files)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a normalized Dream.OS RAG corpus JSONL.")
    parser.add_argument("repo", help="Repository path to export")
    parser.add_argument("--output", required=True, help="Destination JSONL path")
    parser.add_argument(
        "--authority",
        default="canonical_source",
        choices=[
            "approved",
            "canonical_runtime",
            "canonical_source",
            "canonical_docs",
            "verified_report",
            "task_artifact",
            "variant_source",
            "historical",
        ],
    )
    parser.add_argument("--max-bytes", type=int, default=262144)
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"repo not found: {repo}")

    count = export_repo(repo, Path(args.output), authority=args.authority, max_bytes=args.max_bytes)
    print("PROJECTSCANNER_RAG_EXPORT=PASS")
    print(f"DOCUMENTS={count}")
    print(f"OUTPUT={Path(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
