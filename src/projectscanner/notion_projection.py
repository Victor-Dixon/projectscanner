"""Deterministic Notion projection planning for the Dream.OS repo portfolio."""

from __future__ import annotations

from typing import Any

PROJECTION_SCHEMA_VERSION = "dreamos.notion-repo-portfolio.v1"
MATERIAL_FIELDS = (
    "Repo Key",
    "Repo",
    "Contract Status",
    "Active Lane",
    "Findings",
    "Branch",
    "Head SHA",
    "Scanner Schema",
    "Source",
)


def _string(value: Any) -> str:
    return "" if value is None else str(value)


def _finding_summary(findings: list[dict]) -> str:
    if not findings:
        return "none"
    return "; ".join(
        f"{item.get('code', 'unknown')}: {item.get('path', 'unknown')}" for item in findings
    )


def desired_rows(portfolio_index: dict) -> list[dict]:
    """Return stable Notion property maps for active repositories only."""
    rows: list[dict] = []
    for repo in portfolio_index.get("repos", []):
        if repo.get("fleet_state") != "active":
            continue
        rows.append(
            {
                "Repo Key": _string(repo.get("repo_key")).casefold(),
                "Repo": _string(repo.get("repo")),
                "Contract Status": _string(repo.get("contract_status") or "Unknown"),
                "Active Lane": _string(repo.get("active_lane")),
                "Findings": _finding_summary(repo.get("findings") or []),
                "Branch": _string(repo.get("branch")),
                "Head SHA": _string(repo.get("head_sha")),
                "Scanner Schema": _string(repo.get("planning_schema")),
                "Source": _string(repo.get("source")),
            }
        )
    return sorted(rows, key=lambda row: row["Repo Key"])


def _row_properties(row: dict) -> dict:
    properties = row.get("properties")
    return properties if isinstance(properties, dict) else row


def _page_id(row: dict) -> str | None:
    value = row.get("page_id") or row.get("id") or row.get("url")
    return _string(value) or None


def _legacy_key(properties: dict, desired_name_map: dict[str, str]) -> str | None:
    key = _string(properties.get("Repo Key")).casefold()
    if key:
        return key
    name = _string(properties.get("Repo")).casefold()
    return desired_name_map.get(name)


def _material_diff(current: dict, desired: dict) -> dict:
    return {
        field: desired.get(field, "")
        for field in MATERIAL_FIELDS
        if _string(current.get(field)) != _string(desired.get(field))
    }


def build_upsert_plan(portfolio_index: dict, existing_rows: list[dict]) -> dict:
    """Plan create/update/noop actions keyed by repo identity.

    Existing legacy rows without ``Repo Key`` are adopted by unique repo-name
    match so the first keyed sync updates them instead of creating duplicates.
    """
    desired = desired_rows(portfolio_index)
    desired_by_key = {row["Repo Key"]: row for row in desired}
    desired_name_map = {row["Repo"].casefold(): row["Repo Key"] for row in desired}

    existing_by_key: dict[str, list[dict]] = {}
    for row in existing_rows:
        properties = _row_properties(row)
        key = _legacy_key(properties, desired_name_map)
        if key:
            existing_by_key.setdefault(key, []).append(row)

    creates: list[dict] = []
    updates: list[dict] = []
    noops: list[dict] = []
    conflicts: list[dict] = []

    for key, properties in desired_by_key.items():
        matches = existing_by_key.get(key, [])
        if not matches:
            creates.append({"repo_key": key, "properties": properties})
            continue
        if len(matches) > 1:
            conflicts.append(
                {
                    "repo_key": key,
                    "code": "duplicate_repo_key",
                    "page_ids": [_page_id(row) for row in matches],
                }
            )
            continue

        row = matches[0]
        current = _row_properties(row)
        changes = _material_diff(current, properties)
        page_id = _page_id(row)
        if changes:
            updates.append(
                {
                    "repo_key": key,
                    "page_id": page_id,
                    "properties": properties,
                    "changes": changes,
                }
            )
        else:
            noops.append({"repo_key": key, "page_id": page_id})

    return {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "creates": creates,
        "updates": updates,
        "noops": noops,
        "conflicts": conflicts,
        "counts": {
            "create": len(creates),
            "update": len(updates),
            "noop": len(noops),
            "conflict": len(conflicts),
        },
    }
