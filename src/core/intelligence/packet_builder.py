"""Build projectscanner_intelligence_packet.v1 from repo telemetry."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .dirty_classifier import aggregate_dirty_classes, classify_path, git_status_paths
from .generated_classifier import detect_experiment_boundary, runtime_noise_ratio
from .manifest_paths import PACKET_SCHEMA, packet_path_for_repo
from .packet_validation import intelligence_packet_canonical_sha256, validate_intelligence_packet

# Lane derivation from dirty-class dominance
LANE_MAP: dict[str, list[str]] = {
    "runtime_state": [
        "runtime_state_isolation_001",
        "projectscanner_runtime_heatmap_001",
    ],
    "generated_reports": [
        "generated_report_archival_001",
        "experiment_generated_file_separator_001",
    ],
    "generated_runtime": [
        "projectscanner_generated_file_classifier_001",
        "runtime_state_isolation_001",
    ],
    "experiment_overlay": [
        "projectscanner_experiment_boundary_engine_001",
        "experiment_isolation_boundary_001",
    ],
    "source_code": [
        "projectscanner_task_derivation_engine_001",
        "autonomous_patch_validator_001",
    ],
    "archive_material": [
        "governance_archive_review_001",
    ],
}

OWNERSHIP_ONTOLOGY: dict[str, dict[str, Any]] = {
    "DreamVault": {
        "canonical_owner": "DreamVault",
        "owns": ["governance", "runtime/tasks", "runtime/contracts", "data/reports"],
    },
    "projectscanner": {
        "canonical_owner": "projectscanner",
        "owns": ["repo intelligence", "repo topology", "ecosystem graph"],
    },
    "AgentTools": {
        "canonical_owner": "AgentTools",
        "owns": ["MCP", "integrations", "dashboards"],
    },
    "Dream.os-Core": {
        "canonical_owner": "Dream.os-Core",
        "owns": ["runtime contracts", "orchestration primitives"],
    },
    "DreamOS": {
        "canonical_owner": "DreamOS",
        "owns": ["runtime contracts", "transport", "swarm execution"],
    },
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _git_meta(repo_root: Path) -> dict[str, Any]:
    meta: dict[str, Any] = {"is_repo": False, "branch": "", "dirty_count": 0, "untracked_count": 0}
    try:
        inside = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return meta
        meta["is_repo"] = True
        branch = subprocess.run(
            ["git", "-C", str(repo_root), "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        meta["branch"] = branch.stdout.strip() if branch.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return meta
    return meta


def _detect_technology(repo_root: Path) -> dict[str, Any]:
    langs: dict[str, int] = {}
    markers: list[str] = []
    ext_map = {
        ".py": "python",
        ".rs": "rust",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".go": "go",
        ".java": "java",
    }
    marker_files = {
        "pyproject.toml": "python-packaging",
        "package.json": "node",
        "Cargo.toml": "rust",
        "pytest.ini": "pytest",
        ".github/workflows": "ci",
    }
    # Keep this fast and deterministic: only scan high-signal folders.
    scan_roots = [
        repo_root / "src",
        repo_root / "scripts",
        repo_root / "tests",
        repo_root / "config",
        repo_root / "docs",
        repo_root / ".github",
    ]
    scan_roots = [p for p in scan_roots if p.exists()]
    if not scan_roots:
        scan_roots = [repo_root]

    skip_dir_names = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
        "logs",
        "runtime",
        "data",
        "temp_repos",
        "temp_scan",
        "temp_github_scan",
        "temp_github_deploy",
    }

    for base in scan_roots:
        for path in base.rglob("*"):
            try:
                if path.is_dir() and path.name in skip_dir_names:
                    continue
                if not path.is_file():
                    continue
            except OSError:
                continue

            rel = str(path.relative_to(repo_root)).replace("\\", "/")
            if any(seg in rel for seg in ("/.git/", "/node_modules/", "/__pycache__/")):
                continue

            ext = path.suffix.lower()
            if ext in ext_map:
                key = ext_map[ext]
                langs[key] = langs.get(key, 0) + 1
            for marker, label in marker_files.items():
                if rel == marker or rel.startswith(marker + "/"):
                    if label not in markers:
                        markers.append(label)
    return {"languages": dict(sorted(langs.items(), key=lambda x: -x[1])), "markers": sorted(markers)}


def _topology(repo_root: Path) -> dict[str, Any]:
    top_dirs: list[str] = []
    try:
        for child in sorted(repo_root.iterdir()):
            if child.is_dir() and child.name not in {".git", "__pycache__", "node_modules"}:
                top_dirs.append(child.name)
    except OSError:
        pass
    return {"depth": max((p.count("/") for p in top_dirs), default=0), "top_level_dirs": top_dirs[:24]}


def _resolve_ownership(repo_name: str) -> dict[str, Any]:
    for key, spec in OWNERSHIP_ONTOLOGY.items():
        if key.lower() == repo_name.lower() or repo_name.lower().startswith(key.lower()):
            return spec
    return {"canonical_owner": "unknown", "owns": []}


def _derive_risk(dirty_classes: dict[str, int], experiment: dict[str, Any]) -> str:
    total = sum(dirty_classes.values())
    if total == 0:
        return "low"
    noise = runtime_noise_ratio(dirty_classes)
    source = dirty_classes.get("source_code", 0)
    if experiment.get("is_experiment") and source > 20:
        return "critical"
    if noise > 0.75 and total > 30:
        return "high"
    if noise > 0.5 or total > 50:
        return "medium"
    return "low"


def _recommended_action(risk: str, dirty_classes: dict[str, int]) -> str:
    if dirty_classes.get("runtime_state", 0) > dirty_classes.get("source_code", 0):
        return "preserve_runtime_state"
    if dirty_classes.get("generated_reports", 0) > 10:
        return "archive_generated_reports_before_source_edits"
    if dirty_classes.get("experiment_overlay", 0) > 0:
        return "enforce_experiment_boundary_before_patch"
    if risk in ("high", "critical"):
        return "inspect_and_manifest_before_mutation"
    return "proceed_with_governed_patch"


def _candidate_lanes(dirty_classes: dict[str, int], risk: str) -> list[str]:
    lanes: list[str] = []
    for bucket, count in sorted(dirty_classes.items(), key=lambda x: -x[1]):
        if count == 0:
            continue
        for lane in LANE_MAP.get(bucket, []):
            if lane not in lanes:
                lanes.append(lane)
    if risk in ("high", "critical"):
        for lane in (
            "projectscanner_autonomous_patch_manifest_001",
            "autonomous_patch_validator_001",
        ):
            if lane not in lanes:
                lanes.append(lane)
    if not lanes:
        lanes.append("projectscanner_task_derivation_engine_001")
    return lanes[:12]


def _load_scan_artifact(repo_root: Path) -> Path | None:
    for candidate in sorted(repo_root.glob("project_analysis_*.json")):
        return candidate
    return None


class IntelligencePacketBuilder:
    """Normalize repo filesystem + git telemetry into intelligence packet v1."""

    def __init__(self, repo_root: Path | str):
        self.repo_root = Path(repo_root).resolve()

    def build(self) -> dict[str, Any]:
        repo_name = self.repo_root.name
        dirty_paths, status_stats = git_status_paths(self.repo_root)
        dirty_classes = aggregate_dirty_classes(dirty_paths)
        experiment = detect_experiment_boundary(self.repo_root, dirty_paths)
        git_meta = _git_meta(self.repo_root)
        git_meta["dirty_count"] = status_stats["dirty_count"]
        git_meta["untracked_count"] = status_stats["untracked_count"]

        risk = _derive_risk(dirty_classes, experiment)
        scan_artifact = _load_scan_artifact(self.repo_root)
        out_path = packet_path_for_repo(self.repo_root)

        packet: dict[str, Any] = {
            "schema": PACKET_SCHEMA,
            "repo": repo_name,
            "repo_root": str(self.repo_root),
            "generated_at": utc_now(),
            "git": git_meta,
            "dirty_classes": dirty_classes,
            "technology": _detect_technology(self.repo_root),
            "topology": _topology(self.repo_root),
            "experiment_boundary": experiment,
            "risk_level": risk,
            "recommended_action": _recommended_action(risk, dirty_classes),
            "candidate_lanes": _candidate_lanes(dirty_classes, risk),
            "ownership": _resolve_ownership(repo_name),
            "manifest_path": str(out_path),
        }
        if scan_artifact:
            packet["scan_artifact"] = str(scan_artifact)
        validate_intelligence_packet(packet)
        packet["canonical_sha256"] = intelligence_packet_canonical_sha256(packet)
        return packet

    def write(self, out_path: Path | None = None) -> Path:
        packet = self.build()
        target = out_path or packet_path_for_repo(self.repo_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return target


def build_intelligence_packet(repo_root: Path | str, out_path: Path | None = None) -> Path:
    return IntelligencePacketBuilder(repo_root).write(out_path)
