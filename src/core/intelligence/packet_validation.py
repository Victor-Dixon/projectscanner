"""Validation and deterministic hashing for intelligence packets."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .manifest_paths import PACKET_SCHEMA


REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "schema",
    "repo",
    "repo_root",
    "generated_at",
    "git",
    "dirty_classes",
    "technology",
    "topology",
    "experiment_boundary",
    "risk_level",
    "recommended_action",
    "candidate_lanes",
    "ownership",
    "manifest_path",
)


def validate_intelligence_packet(packet: dict[str, Any]) -> None:
    if not isinstance(packet, dict):
        raise TypeError("packet must be a dict")
    if packet.get("schema") != PACKET_SCHEMA:
        raise ValueError(f"invalid schema: {packet.get('schema')}")

    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in packet]
    if missing:
        raise ValueError(f"missing required keys: {missing}")

    if not isinstance(packet.get("repo"), str) or not packet["repo"]:
        raise ValueError("repo must be non-empty string")
    if not isinstance(packet.get("repo_root"), str) or not packet["repo_root"]:
        raise ValueError("repo_root must be non-empty string")
    if not isinstance(packet.get("generated_at"), str) or not packet["generated_at"]:
        raise ValueError("generated_at must be non-empty string")
    if not isinstance(packet.get("manifest_path"), str) or not packet["manifest_path"]:
        raise ValueError("manifest_path must be non-empty string")

    if not isinstance(packet.get("git"), dict):
        raise ValueError("git must be an object")
    if not isinstance(packet.get("dirty_classes"), dict):
        raise ValueError("dirty_classes must be an object")
    if not isinstance(packet.get("technology"), dict):
        raise ValueError("technology must be an object")
    if not isinstance(packet.get("topology"), dict):
        raise ValueError("topology must be an object")
    if not isinstance(packet.get("experiment_boundary"), dict):
        raise ValueError("experiment_boundary must be an object")
    if not isinstance(packet.get("candidate_lanes"), list):
        raise ValueError("candidate_lanes must be a list")

    risk = packet.get("risk_level")
    if risk not in ("low", "medium", "high", "critical"):
        raise ValueError(f"invalid risk_level: {risk}")


def _canonical_packet_for_hash(packet: dict[str, Any]) -> dict[str, Any]:
    # Remove volatile keys and anything path-dependent that changes across machines.
    drop = {
        "generated_at",
        "manifest_path",
        "repo_root",
        "scan_artifact",
        "canonical_sha256",
    }
    out: dict[str, Any] = {}
    for k, v in packet.items():
        if k in drop:
            continue
        out[k] = v
    return out


def intelligence_packet_canonical_sha256(packet: dict[str, Any]) -> str:
    validate_intelligence_packet(packet)
    canonical = _canonical_packet_for_hash(packet)
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return hashlib.sha256(blob).hexdigest()

