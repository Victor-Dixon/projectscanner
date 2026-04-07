"""Workflow scan mode normalization helpers (SSOT)."""

from __future__ import annotations

DEFAULT_MODE = "manual"

_MODE_ALIASES = {
    "nightly": "nightly",
    "schedule": "nightly",
    "scheduled": "nightly",
    "pr": "pr",
    "pull_request": "pr",
    "pull-request": "pr",
    "release": "release",
    "tag": "release",
    "main": "main",
    "push_main": "main",
    "manual": "manual",
    "workflow_dispatch": "manual",
    "dispatch": "manual",
}


def normalize_workflow_mode(raw_mode: str | None) -> str:
    """Normalize workflow scan modes into canonical values.

    Unknown or missing values fall back to ``DEFAULT_MODE``.
    """
    if raw_mode is None:
        return DEFAULT_MODE

    normalized = str(raw_mode).strip().lower()
    if not normalized:
        return DEFAULT_MODE

    return _MODE_ALIASES.get(normalized, DEFAULT_MODE)


def derive_workflow_mode(event_name: str | None, ref_type: str | None, ref_name: str | None) -> str:
    """Derive workflow mode from GitHub event metadata."""
    event = (event_name or "").strip().lower()
    if event == "schedule":
        return "nightly"
    if event == "pull_request":
        return "pr"

    ref_kind = (ref_type or "").strip().lower()
    if ref_kind == "tag":
        return "release"

    branch = (ref_name or "").strip().lower()
    if branch == "main":
        return "main"

    return DEFAULT_MODE
