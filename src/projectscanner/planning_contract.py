"""Normalize and validate the Dream.OS fleet planning contract."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

SCHEMA_VERSION = "dreamos.fleet-planning.v1"
REQUIRED_PLANNING_FILES = (
    "MASTER_TASK_LIST.md",
    "MASTER_TASK_LOG.md",
    "NEXT_UP.md",
)
DOMAIN_MODEL_CANDIDATES = ("DOMAIN_MODEL.md", "docs/DOMAIN_MODEL.md")
_SYNC_RE = re.compile(r"^Last synchronized:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
_NUMBERED_START_RE = re.compile(r"^\s*\d+\.\s+(.+?)\s*$")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_POINTER_MARKERS = (
    "non-canonical compatibility pointer",
    "non-canonical pointer",
    "compatibility pointer",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _sync_date(text: str) -> str | None:
    match = _SYNC_RE.search(text)
    return match.group(1) if match else None


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        return ""
    tail = text.split(marker, 1)[1]
    return tail.split("\n## ", 1)[0]


def _next_actions(text: str) -> list[str]:
    section = _section(text, "Immediate actions")
    actions: list[str] = []
    current: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = _NUMBERED_START_RE.match(raw_line)
        if match:
            if current:
                actions.append(" ".join(current))
            current = [match.group(1).strip()]
        elif current:
            current.append(line)
    if current:
        actions.append(" ".join(current))
    return actions


def _active_lane(actions: list[str]) -> str | None:
    if not actions:
        return None
    match = _BOLD_RE.search(actions[0])
    return match.group(1).rstrip(".") if match else actions[0].rstrip(".")


def _is_pointer(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _POINTER_MARKERS)


def inspect_planning_contract(repo: Path, *, generated_at: datetime | None = None) -> dict:
    """Return a deterministic planning-contract record for one repository."""
    repo = repo.resolve()
    generated_at = generated_at or datetime.now(UTC)

    files = {name: repo / name for name in REQUIRED_PLANNING_FILES}
    presence = {name: path.is_file() for name, path in files.items()}
    domain_model = next((name for name in DOMAIN_MODEL_CANDIDATES if (repo / name).is_file()), None)

    contents = {name: _read(path) for name, path in files.items()}
    sync_dates = {name: _sync_date(text) for name, text in contents.items() if text}
    if domain_model:
        sync_dates[domain_model] = _sync_date(_read(repo / domain_model))

    actions = _next_actions(contents.get("NEXT_UP.md", ""))
    findings: list[dict[str, str]] = []

    for name, present in presence.items():
        if not present:
            findings.append({"severity": "error", "code": "missing_required_file", "path": name})
            continue
        if _is_pointer(contents[name]):
            findings.append({"severity": "warning", "code": "required_file_is_pointer", "path": name})

    if domain_model is None:
        findings.append({"severity": "error", "code": "missing_domain_model", "path": "DOMAIN_MODEL.md"})

    if presence["NEXT_UP.md"]:
        if not actions:
            findings.append({"severity": "warning", "code": "missing_immediate_actions", "path": "NEXT_UP.md"})
        elif len(actions) > 5:
            findings.append({"severity": "warning", "code": "too_many_immediate_actions", "path": "NEXT_UP.md"})

    dated = {value for value in sync_dates.values() if value}
    if len(dated) > 1:
        findings.append({"severity": "warning", "code": "planning_sync_date_drift", "path": "planning-set"})

    if any(item["severity"] == "error" for item in findings):
        status = "FAIL"
    elif findings:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at.astimezone(UTC).isoformat(),
        "repo": repo.name,
        "repo_path": str(repo),
        "contract_status": status,
        "required_files": presence,
        "domain_model": domain_model,
        "sync_dates": sync_dates,
        "active_lane": _active_lane(actions),
        "next_actions": actions,
        "findings": findings,
    }
