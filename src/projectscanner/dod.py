"""Evaluate repository evidence against an explicit Definition-of-Done contract.

The evaluator is evidence-only. It does not rank work, approve mutations,
delete branches, or become a second planner.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATUS_DONE = "DONE"
STATUS_DONE_WITH_KEEP = "DONE_WITH_INTENTIONAL_KEEP"
STATUS_BLOCKED = "BLOCKED"
STATUS_NOT_READY = "NOT_READY"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def evaluate_definition_of_done(profile: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic evidence-only DoD evaluation."""
    requirements = list(profile.get("done_when", []))
    specialized = list(profile.get("specialized_done", []))
    keys = list(dict.fromkeys(requirements + specialized))
    checks: dict[str, dict[str, Any]] = {}

    for key in keys:
        value = evidence.get(key)
        checks[key] = {
            "status": "PASS" if value is True else "FAIL" if value is False else "UNKNOWN",
            "evidence": value,
        }

    failed = sorted(k for k, item in checks.items() if item["status"] == "FAIL")
    unknown = sorted(k for k, item in checks.items() if item["status"] == "UNKNOWN")
    if failed:
        status = STATUS_BLOCKED
    elif unknown:
        status = STATUS_NOT_READY
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
    contract_path: Path,
    profiles_path: Path,
    repository: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate one named repository using the portfolio contract and profile."""
    contract = load_json(contract_path)
    profiles = load_json(profiles_path).get("profiles", {})
    raw = profiles.get(repository)
    if not isinstance(raw, dict):
        raise KeyError(f"no DoD profile for repository: {repository}")

    profile = dict(raw)
    profile["repository"] = repository
    profile["done_when"] = contract.get("common_requirements", [])
    return evaluate_definition_of_done(profile, evidence)
