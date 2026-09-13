"""Evaluate repository evidence against a small, explicit Definition-of-Done contract.

The evaluator is intentionally evidence-only. It does not rank work, approve mutations,
delete branches, or become a second planner.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATUS_DONE = "DONE"
STATUS_DONE_WITH_KEEP = "DONE_WITH_INTENTIONAL_KEEP"
STATUS_BLOCKED = "BLOCKED"
STATUS_HOLD = "HOLD"
STATUS_NOT_READY = "NOT_READY"


def load_registry(path: Path) -> dict[str, Any]:
    """Load and minimally validate a DoD registry."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("schema_version"), str):
        raise ValueError("invalid DoD registry")
    if not isinstance(data.get("common_done_requirements"), list):
        raise ValueError("registry missing common_done_requirements")
    return data


def evaluate_definition_of_done(
    profile: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Return a deterministic evidence-only DoD evaluation.

    Missing evidence is a finding, never an implicit pass. The evaluator accepts
    boolean evidence for common and specialized requirements and leaves policy
    decisions to the caller.
    """
    requirements = list(profile.get("done_when", []))
    specialized = list(profile.get("specialized_done", []))
    checks: dict[str, dict[str, Any]] = {}

    for key in requirements + specialized:
        value = evidence.get(key)
        checks[key] = {
            "status": "PASS" if value is True else "FAIL" if value is False else "UNKNOWN",
            "evidence": value,
        }

    failed = sorted(key for key, item in checks.items() if item["status"] == "FAIL")
    unknown = sorted(key for key, item in checks.items() if item["status"] == "UNKNOWN")

    if failed or unknown:
        status = STATUS_BLOCKED if failed else STATUS_NOT_READY
    else:
        status = STATUS_DONE_WITH_KEEP if evidence.get("intentional_keep") else STATUS_DONE

    return {
        "schema_version": "dreamos.repository-dod-result.v1",
        "repository": profile.get("repository"),
        "mvp": profile.get("mvp"),
        "status": status,
        "checks": checks,
        "failed": failed,
        "unknown": unknown,
        "evidence_only": True,
        "mutation_authority": False,
    }


def evaluate_from_registry(
    registry_path: Path,
    repository: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate one named repository profile from a registry."""
    registry = load_registry(registry_path)
    raw = registry.get("profiles", {}).get(repository)
    if raw is None:
        raise KeyError(f"no DoD profile for repository: {repository}")
    if not isinstance(raw, dict):
        raise ValueError(f"invalid DoD profile for repository: {repository}")
    profile = dict(raw)
    profile["repository"] = repository
    profile["done_when"] = registry["common_done_requirements"]
    return evaluate_definition_of_done(profile, evidence)
