"""Portfolio authority report — classify repos without mutating them.

Read-only inspection. Promotion recommendations are advisory only.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = "projectscanner.portfolio_authority_report.v1"

TOOLBELT_EVIDENCE_MARKERS = (
    "toolbelt",
    "operator/control-plane",
    "operator control-plane",
    "scanning mechanics",
    "mcp",
    "not dream.os variants",
)
CANONICAL_EVIDENCE_MARKERS = (
    "canonical core",
    "runtime/swarm execution",
    "orchestration primitives",
    "dream.os-core",
    "owns runtime",
)
VARIANT_EVIDENCE_MARKERS = (
    "variant",
    "promotion candidate",
    "salvage",
    "fork",
    "mirror",
    "legacy",
)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm_name(name: str) -> str:
    return name.strip().lower()


def _run_git(repo: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if proc.returncode != 0:
            return ""
        return (proc.stdout or "").strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def git_identity(repo: Path) -> dict[str, Any]:
    is_repo = _run_git(repo, "rev-parse", "--is-inside-work-tree") == "true"
    if not is_repo:
        return {
            "is_repo": False,
            "branch": "",
            "head": "",
            "remote": "",
            "dirty": False,
            "dirty_count": 0,
            "status_short": [],
        }
    status = [ln for ln in _run_git(repo, "status", "--short").splitlines() if ln.strip()]
    remote = _run_git(repo, "remote", "get-url", "origin")
    return {
        "is_repo": True,
        "branch": _run_git(repo, "branch", "--show-current"),
        "head": _run_git(repo, "rev-parse", "HEAD"),
        "remote": remote,
        "dirty": bool(status),
        "dirty_count": len(status),
        "status_short": status[:40],
    }


def _read_text_snippets(repo: Path, limit_files: int = 8) -> str:
    blobs: list[str] = []
    for name in (
        "AGENTS.md",
        "README.md",
        "PRD.md",
        "CONSOLIDATION_MANIFEST.md",
        "PRODUCTION_READINESS.md",
        "NEXT_UP.md",
    ):
        path = repo / name
        if not path.is_file():
            continue
        try:
            blobs.append(path.read_text(encoding="utf-8", errors="replace")[:4000])
        except OSError:
            continue
        if len(blobs) >= limit_files:
            break
    return "\n".join(blobs).lower()


def detect_capabilities(repo: Path, docs: str) -> list[str]:
    caps: set[str] = set()
    markers = {
        "python": ["pyproject.toml", "requirements.txt", "setup.py"],
        "node": ["package.json"],
        "rust": ["Cargo.toml"],
        "pytest": ["pytest.ini", "tests"],
        "ci": [".github/workflows"],
        "discord_bot": [],
        "mcp": [],
        "scanner": [],
        "governance": [],
        "website": [],
        "swarm_runtime": [],
    }
    for cap, files in markers.items():
        for rel in files:
            if (repo / rel).exists():
                caps.add(cap)
    if "mcp" in docs or (repo / "tools").is_dir() and "toolbelt" in docs:
        caps.add("mcp")
        caps.add("operator_toolbelt")
    if "scanner" in docs or (repo / "src" / "core" / "projectscanner").is_dir():
        caps.add("scanner")
        caps.add("repo_intelligence")
    if "governance" in docs or (repo / "runtime" / "tasks").is_dir():
        caps.add("governance")
    if "swarm" in docs or "orchestration" in docs:
        caps.add("swarm_runtime")
    if (repo / "sites").is_dir() or "website" in docs:
        caps.add("website")
    if "discord" in docs:
        caps.add("discord_bot")
    return sorted(caps)


def classify_repo(
    *,
    repo: Path,
    peer_names: set[str],
) -> dict[str, Any]:
    name = repo.name
    norm = _norm_name(name)
    docs = _read_text_snippets(repo)
    evidence: list[str] = []
    confidence = 0.35
    classification = "unknown"

    path_s = str(repo).replace("\\", "/").lower()
    if any(tok in path_s for tok in ("/archive/", "backup", "salvage", "quarantine")):
        classification = "archive_candidate"
        confidence = 0.7
        evidence.append(f"path_signal:{path_s}")

    # Prefer exact/near-exact names before stripping punctuation (Dream.os vs DreamOS).
    exact_toolbelt = {
        "projectscanner",
        "agent-tools",
        "agenttools",
        "agent_tools",
    }
    exact_canonical = {
        "dreamos",
        "dream.os-core",
        "dreamos-core",
        "dream.os_core",
    }
    exact_variant = {
        "dream.os",
        "victor.os",
        "autodream.os",
        "dreamos_headless",
        "dreamos-headless",
        "dream-os-hardened-v33",
        "dreamos_recoveryforge",
        "dreamos_sync",
        "dreamos_worker",
        "dreamos_agent",
        "dreamos_brain",
        "dreamos-brain",
    }

    peer_norm = {_norm_name(p) for p in peer_names}
    has_canonical_peer = bool(peer_norm & exact_canonical)

    if norm in exact_toolbelt:
        classification = "toolbelt"
        confidence = 0.75
        evidence.append(f"name_match:{name}")
    if any(m in docs for m in TOOLBELT_EVIDENCE_MARKERS):
        if classification == "toolbelt":
            confidence = min(0.95, confidence + 0.15)
        elif classification == "unknown":
            classification = "toolbelt"
            confidence = 0.65
        evidence.append("docs_marker:toolbelt")

    if norm in exact_canonical:
        classification = "canonical"
        confidence = 0.8
        evidence.append(f"name_match_canonical_core:{name}")
    if any(m in docs for m in CANONICAL_EVIDENCE_MARKERS) and norm in exact_canonical:
        classification = "canonical"
        confidence = max(confidence, 0.85)
        evidence.append("docs_marker:canonical_core")

    if norm in exact_variant:
        classification = "variant"
        confidence = 0.75 if has_canonical_peer else 0.6
        evidence.append("variant_name_table")
        if has_canonical_peer:
            evidence.append("peer_canonical_present")
    if classification == "variant" and any(m in docs for m in VARIANT_EVIDENCE_MARKERS):
        evidence.append("docs_marker:variant_or_salvage")
        confidence = min(0.9, confidence + 0.1)

    # Product heuristic: app markers without core/toolbelt classification
    if classification == "unknown":
        if (repo / "package.json").is_file() or (repo / "pyproject.toml").is_file():
            classification = "product"
            confidence = 0.45
            evidence.append("packaging_marker_without_core_or_toolbelt_match")

    if not evidence:
        evidence.append("insufficient_signals_preserved_as_unknown")
        classification = "unknown"
        confidence = 0.2

    caps = detect_capabilities(repo, docs)
    promotion = _promotion_recommendation(classification, confidence, caps)

    return {
        "classification": classification,
        "confidence": round(confidence, 2),
        "evidence": evidence,
        "capabilities": caps,
        "promotion_recommendation": promotion,
    }


def _promotion_recommendation(classification: str, confidence: float, caps: list[str]) -> dict[str, Any]:
    """Advisory only — never performs promotion."""
    if classification == "canonical":
        action = "KEEP_CANONICAL_IN_SCAN_SET"
        note = (
            "Canonical within this controlled scan set only — not portfolio-wide "
            "authority promotion. Do not merge variants into it automatically."
        )
    elif classification == "toolbelt":
        action = "KEEP_TOOLBELT"
        note = "Not a Dream.OS variant. Keep separate; consume via CLI/MCP."
    elif classification == "variant":
        action = "REVIEW_FOR_PROMOTION_OR_ARCHIVE"
        note = "Requires salvage/promotion manifest before any cleanup. Do not auto-promote."
    elif classification == "archive_candidate":
        action = "ARCHIVE_REVIEW_ONLY"
        note = "Path suggests archive/backup; verify before delete."
    elif classification == "product":
        action = "KEEP_PRODUCT_SURFACE"
        note = "Application/product repo; not core runtime."
    else:
        action = "MANUAL_REVIEW"
        note = "Unknown — preserve until evidence improves."
    return {
        "action": action,
        "confidence": confidence,
        "note": note,
        "auto_promote": False,
        "capabilities_seen": caps,
    }


def inspect_repo(path: Path, *, peer_names: set[str]) -> dict[str, Any]:
    repo = path.resolve()
    git = git_identity(repo)
    classification = classify_repo(repo=repo, peer_names=peer_names)
    return {
        "name": repo.name,
        "path": str(repo),
        "remote": git.get("remote") or "",
        "branch": git.get("branch") or "",
        "head": git.get("head") or "",
        "dirty_worktree": bool(git.get("dirty")),
        "dirty_count": git.get("dirty_count", 0),
        "git": git,
        **classification,
    }


def _overlap_capabilities(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    overlaps: list[dict[str, Any]] = []
    for i, left in enumerate(repos):
        caps_l = set(left.get("capabilities") or [])
        for right in repos[i + 1 :]:
            caps_r = set(right.get("capabilities") or [])
            shared = sorted(caps_l & caps_r)
            if shared:
                overlaps.append(
                    {
                        "repos": [left["name"], right["name"]],
                        "shared_capabilities": shared,
                        "note": "overlap does not imply merge; use for duplicate-work avoidance",
                    }
                )
    return overlaps


def build_authority_report(paths: list[Path | str]) -> dict[str, Any]:
    resolved = [Path(p).expanduser().resolve() for p in paths]
    peer_names = {p.name for p in resolved}
    repos = [inspect_repo(p, peer_names=peer_names) for p in resolved if p.exists()]
    missing = [str(p) for p in resolved if not p.exists()]
    return {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "generator": "projectscanner",
        "read_only": True,
        "auto_promote": False,
        "authority_scope": "controlled_scan_set",
        "authority_scope_note": (
            "Classifications apply only to the supplied repository paths. "
            "A canonical label (e.g. Dream.os-Core) is a host-local stand-in for "
            "this slice — not portfolio-wide DreamOS authority promotion."
        ),
        "repo_count": len(repos),
        "missing_paths": missing,
        "repositories": repos,
        "duplicate_or_overlapping_capabilities": _overlap_capabilities(repos),
        "summary": {
            "canonical": [r["name"] for r in repos if r["classification"] == "canonical"],
            "variant": [r["name"] for r in repos if r["classification"] == "variant"],
            "toolbelt": [r["name"] for r in repos if r["classification"] == "toolbelt"],
            "product": [r["name"] for r in repos if r["classification"] == "product"],
            "archive_candidate": [r["name"] for r in repos if r["classification"] == "archive_candidate"],
            "unknown": [r["name"] for r in repos if r["classification"] == "unknown"],
        },
    }


def render_authority_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Portfolio Authority Report",
        "",
        f"- Generated: `{report.get('generated_at')}`",
        f"- Schema: `{report.get('schema')}`",
        f"- Repos: **{report.get('repo_count', 0)}**",
        f"- Authority scope: `{report.get('authority_scope')}`",
        f"- Auto-promote: **{report.get('auto_promote')}** (always false)",
        "",
        f"> {report.get('authority_scope_note')}",
        "",
        "## Summary",
        "",
    ]
    summary = report.get("summary") or {}
    for key in ("canonical", "toolbelt", "variant", "product", "archive_candidate", "unknown"):
        vals = summary.get(key) or []
        lines.append(f"- **{key}**: {', '.join(vals) if vals else '_none_'}")
    lines.extend(["", "## Repositories", ""])
    for repo in report.get("repositories") or []:
        lines.append(f"### {repo.get('name')}")
        lines.append(f"- path: `{repo.get('path')}`")
        lines.append(f"- remote: `{repo.get('remote') or 'none'}`")
        lines.append(f"- branch/HEAD: `{repo.get('branch') or 'none'}` / `{(repo.get('head') or '')[:12] or 'none'}`")
        lines.append(f"- dirty: `{repo.get('dirty_worktree')}` (count={repo.get('dirty_count')})")
        lines.append(
            f"- classification: **{repo.get('classification')}** "
            f"(confidence={repo.get('confidence')})"
        )
        lines.append(f"- capabilities: {', '.join(repo.get('capabilities') or []) or '_none_'}")
        lines.append(f"- evidence: {'; '.join(repo.get('evidence') or [])}")
        promo = repo.get("promotion_recommendation") or {}
        lines.append(
            f"- promotion recommendation: `{promo.get('action')}` — {promo.get('note')} "
            f"(auto_promote={promo.get('auto_promote')})"
        )
        lines.append("")
    overlaps = report.get("duplicate_or_overlapping_capabilities") or []
    lines.extend(["## Overlapping capabilities", ""])
    if not overlaps:
        lines.append("_none detected_")
    else:
        for row in overlaps:
            lines.append(
                f"- {' + '.join(row.get('repos') or [])}: "
                f"{', '.join(row.get('shared_capabilities') or [])}"
            )
    lines.append("")
    lines.append("AUTHORITY_REPORT=PASS")
    lines.append("")
    return "\n".join(lines)


def write_authority_report(
    paths: list[Path | str],
    *,
    out_dir: Path | str,
) -> tuple[Path, Path, dict[str, Any]]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = build_authority_report(paths)
    json_path = out / "portfolio_authority_report.json"
    md_path = out / "portfolio_authority_report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_authority_markdown(report), encoding="utf-8")
    return json_path, md_path, report
