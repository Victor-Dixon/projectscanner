"""Normalize and validate the Dream.OS fleet planning contract."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "dreamos.fleet-planning.v1"
MANIFEST_NAME = "PLANNING_CONTRACT.json"

_DEFAULT_AUTHORITY = {
    "master_task_list": "MASTER_TASK_LIST.md",
    "master_task_log": "MASTER_TASK_LOG.md",
    "next_up": "NEXT_UP.md",
}
DOMAIN_MODEL_CANDIDATES = (
    "DOMAIN_MODEL.md",
    "domain_model.md",
    "docs/DOMAIN_MODEL.md",
    "docs/domain_model.md",
)
ACTION_HEADING_ALIASES = (
    "Immediate actions",
    "Immediate queue",
    "Immediate Next Work",
    "Next actions",
    "Next work",
    "Work next",
    "Queue",
    "Do these next, in order",
    "Priority actions",
    "Actions",
)
_SYNC_RE = re.compile(
    r"^\s*(?:[-*]\s*)?\*{0,2}"
    r"(?:Last synchronized|Last updated|Updated|Last audited|Last reconciled|Snapshot date \(UTC\))"
    r"\*{0,2}:\s*\*{0,2}(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE | re.MULTILINE,
)
_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_NUMBERED_START_RE = re.compile(r"^\s*(\d+)[.)]\s+(.+?)\s*$")
_NUMBERED_HEADING_RE = re.compile(r"^#{2,6}\s+(\d+)[.)]\s+(.+?)\s*$")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_NEXT_LANE_RE = re.compile(r"^`?NEXT_LANE=([^`\n]+)`?\s*$", re.MULTILINE)
_NOW_HEADING_RE = re.compile(r"^##\s+NOW\s+[—-]\s+(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_POINTER_MARKERS = (
    "non-canonical compatibility pointer",
    "non-canonical pointer",
    "compatibility pointer",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def _safe_relative_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value.strip())
    if path.is_absolute() or ".." in path.parts:
        return None
    return path.as_posix()


def _load_manifest(repo: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    path = repo / MANIFEST_NAME
    if not path.is_file():
        return {}, []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}, [
            {"severity": "error", "code": "invalid_contract_manifest", "path": MANIFEST_NAME}
        ]

    if not isinstance(payload, dict):
        return {}, [
            {"severity": "error", "code": "invalid_contract_manifest", "path": MANIFEST_NAME}
        ]

    declared = payload.get("schema_version")
    findings: list[dict[str, str]] = []
    if declared not in (None, SCHEMA_VERSION):
        findings.append(
            {"severity": "error", "code": "unsupported_contract_schema", "path": MANIFEST_NAME}
        )
    return payload, findings


def _resolve_authority(
    repo: Path, manifest: dict[str, Any], findings: list[dict[str, str]]
) -> dict[str, str | None]:
    authority = dict(_DEFAULT_AUTHORITY)
    declared = manifest.get("authority")
    if declared is not None and not isinstance(declared, dict):
        findings.append(
            {"severity": "error", "code": "invalid_authority_manifest", "path": MANIFEST_NAME}
        )
        declared = {}

    for key in _DEFAULT_AUTHORITY:
        if isinstance(declared, dict) and key in declared:
            path = _safe_relative_path(declared[key])
            if path is None:
                findings.append(
                    {"severity": "error", "code": "invalid_authority_path", "path": key}
                )
            else:
                authority[key] = path

    domain_model: str | None = None
    if isinstance(declared, dict) and "domain_model" in declared:
        domain_model = _safe_relative_path(declared["domain_model"])
        if domain_model is None:
            findings.append(
                {"severity": "error", "code": "invalid_authority_path", "path": "domain_model"}
            )
    else:
        domain_model = next(
            (candidate for candidate in DOMAIN_MODEL_CANDIDATES if (repo / candidate).is_file()),
            None,
        )

    authority["domain_model"] = domain_model
    return authority


def _sync_date(text: str) -> str | None:
    match = _SYNC_RE.search(text)
    return match.group(1) if match else None


def _find_section(text: str, headings: list[str] | tuple[str, ...]) -> tuple[str, str | None]:
    wanted = {_normalize_heading(item) for item in headings}
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = _HEADING_RE.match(line)
        if not match or _normalize_heading(match.group(2)) not in wanted:
            continue
        level = len(match.group(1))
        body: list[str] = []
        for following in lines[index + 1 :]:
            next_heading = _HEADING_RE.match(following)
            if next_heading and len(next_heading.group(1)) <= level:
                break
            body.append(following)
        return "\n".join(body), match.group(2).strip()
    return "", None


def _numbered_list_actions(section: str) -> list[str]:
    actions: list[str] = []
    current: list[str] = []
    for raw_line in section.splitlines():
        if _HEADING_RE.match(raw_line):
            continue
        line = raw_line.strip()
        if not line:
            continue
        match = _NUMBERED_START_RE.match(raw_line)
        if match:
            if current:
                actions.append(" ".join(current))
            current = [match.group(2).strip()]
            continue
        if current:
            if line.startswith(("-", "*", "```")):
                continue
            current.append(line)
    if current:
        actions.append(" ".join(current))
    return actions


def _numbered_heading_actions(text: str) -> list[str]:
    actions: list[str] = []
    for raw_line in text.splitlines():
        match = _NUMBERED_HEADING_RE.match(raw_line)
        if match:
            actions.append(match.group(2).strip())
    return actions


def _next_actions(text: str, manifest: dict[str, Any]) -> tuple[list[str], str | None]:
    next_up = manifest.get("next_up") if isinstance(manifest.get("next_up"), dict) else {}
    configured = next_up.get("action_headings") if isinstance(next_up, dict) else None
    headings = (
        [item for item in configured if isinstance(item, str) and item.strip()]
        if isinstance(configured, list)
        else list(ACTION_HEADING_ALIASES)
    )
    section, matched_heading = _find_section(text, headings)
    actions = _numbered_list_actions(section)
    if not actions and section:
        actions = _numbered_heading_actions(section)
    if not actions:
        actions = _numbered_heading_actions(text)
    return actions, matched_heading


def _declared_active_lane(text: str, manifest: dict[str, Any]) -> str | None:
    next_lane = _NEXT_LANE_RE.search(text)
    if next_lane:
        return next_lane.group(1).strip()

    next_up = manifest.get("next_up") if isinstance(manifest.get("next_up"), dict) else {}
    configured_heading = next_up.get("lane_heading") if isinstance(next_up, dict) else None
    headings = [configured_heading] if isinstance(configured_heading, str) else ["Active lane"]
    section, _ = _find_section(text, headings)
    section = section.strip()
    if section:
        first_line = section.splitlines()[0].strip()
        return first_line.split(" — ", 1)[0].strip("` ") or None

    now_heading = _NOW_HEADING_RE.search(text)
    if now_heading:
        return now_heading.group(1).strip()

    for heading in ("Current Priority", "Current priority", "Current focus"):
        section, _ = _find_section(text, [heading])
        if section.strip():
            first_line = section.strip().splitlines()[0].strip()
            return first_line.rstrip(".") or None
    return None


def _active_lane(text: str, actions: list[str], manifest: dict[str, Any]) -> str | None:
    declared = _declared_active_lane(text, manifest)
    if declared:
        return declared
    if not actions:
        return None
    match = _BOLD_RE.search(actions[0])
    return match.group(1).rstrip(".") if match else actions[0].rstrip(".")


def _is_pointer(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _POINTER_MARKERS)


def _git_origin(repo: Path) -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _repo_key_from_origin(origin: str) -> str | None:
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$", origin.strip())
    if not match:
        return None
    owner, name = match.groups()
    return f"github:{owner.casefold()}/{name.casefold()}"


def _repo_key(repo: Path, manifest: dict[str, Any]) -> str:
    declared = manifest.get("repo_key")
    if isinstance(declared, str) and declared.strip():
        return declared.strip().casefold()
    remote_key = _repo_key_from_origin(_git_origin(repo))
    return remote_key or f"local:{repo.name.casefold()}"


def _sync_paths(authority: dict[str, str | None], manifest: dict[str, Any]) -> list[str]:
    declared = manifest.get("sync_date_paths")
    if isinstance(declared, list):
        paths = [_safe_relative_path(item) for item in declared]
        return [item for item in paths if item]
    return [path for path in authority.values() if path]


def inspect_planning_contract(repo: Path, *, generated_at: datetime | None = None) -> dict:
    """Return a deterministic planning-contract record for one repository."""
    repo = repo.resolve()
    generated_at = generated_at or datetime.now(UTC)

    manifest, findings = _load_manifest(repo)
    authority = _resolve_authority(repo, manifest, findings)

    contents: dict[str, str] = {}
    required_files: dict[str, bool] = {}
    for logical_name in ("master_task_list", "master_task_log", "next_up"):
        path = authority.get(logical_name)
        if path is None:
            required_files[logical_name] = False
            findings.append(
                {"severity": "error", "code": "missing_required_file", "path": logical_name}
            )
            continue
        present = (repo / path).is_file()
        required_files[path] = present
        contents[path] = _read(repo / path)
        if not present:
            findings.append(
                {"severity": "error", "code": "missing_required_file", "path": path}
            )
        elif _is_pointer(contents[path]):
            findings.append(
                {"severity": "warning", "code": "required_file_is_pointer", "path": path}
            )

    domain_model = authority.get("domain_model")
    if not domain_model or not (repo / domain_model).is_file():
        findings.append(
            {
                "severity": "error",
                "code": "missing_domain_model",
                "path": domain_model or "DOMAIN_MODEL.md",
            }
        )

    next_up_path = authority.get("next_up")
    next_up_text = contents.get(next_up_path or "", "")
    actions, action_heading = _next_actions(next_up_text, manifest)
    active_lane = _active_lane(next_up_text, actions, manifest)

    if next_up_path and (repo / next_up_path).is_file():
        if not actions:
            findings.append(
                {"severity": "warning", "code": "missing_immediate_actions", "path": next_up_path}
            )
        elif len(actions) > 5:
            findings.append(
                {"severity": "warning", "code": "too_many_immediate_actions", "path": next_up_path}
            )

    sync_dates: dict[str, str | None] = {}
    for path in _sync_paths(authority, manifest):
        sync_dates[path] = _sync_date(_read(repo / path))
    dated = {value for value in sync_dates.values() if value}
    if len(dated) > 1:
        findings.append(
            {"severity": "warning", "code": "planning_sync_date_drift", "path": "planning-set"}
        )

    if any(item["severity"] == "error" for item in findings):
        status = "FAIL"
    elif findings:
        status = "WARN"
    else:
        status = "PASS"

    fleet_state = "active" if next_up_path and (repo / next_up_path).is_file() else "unclassified"

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at.astimezone(UTC).isoformat(),
        "repo": repo.name,
        "repo_key": _repo_key(repo, manifest),
        "repo_path": str(repo),
        "fleet_state": fleet_state,
        "contract_status": status,
        "manifest": MANIFEST_NAME if (repo / MANIFEST_NAME).is_file() else None,
        "authority": authority,
        "required_files": required_files,
        "domain_model": domain_model,
        "sync_dates": sync_dates,
        "action_heading": action_heading,
        "active_lane": active_lane,
        "next_actions": actions,
        "findings": findings,
    }
