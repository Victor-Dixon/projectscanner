"""Read-only GitHub Actions configuration and cost evidence sensor.

ProjectScanner owns interpretation, not workflow mutation or runner authority.
All runner and cost conclusions retain their evidence and uncertainty.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "projectscanner.ci-cost.v1"
HOSTED = re.compile(r"^(?:ubuntu|windows|macos)-(?:latest|[0-9][A-Za-z0-9.\-]*|slim)$", re.I)
MATRIX = re.compile(r"^\$\{\{\s*matrix\.([A-Za-z_][A-Za-z0-9_-]*)\s*\}\}$")
MAX_WORKFLOW_BYTES = 1_048_576


def _loader():
    """Use YAML 1.2-like booleans without losing GitHub's `on` key."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("CI inspection requires PyYAML; install projectscanner[ci]") from exc

    class WorkflowLoader(yaml.SafeLoader):
        pass

    WorkflowLoader.yaml_implicit_resolvers = {
        key: [(tag, regex) for tag, regex in values
              if tag != "tag:yaml.org,2002:bool"]
        for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }
    WorkflowLoader.add_implicit_resolver(
        "tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$", re.I), list("tTfF")
    )

    def unique_mapping(loader, node):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=True)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    None, None, "invalid mapping key", key_node.start_mark
                ) from exc
            if key in result:
                raise yaml.constructor.ConstructorError(None, None, f"duplicate key: {key}", key_node.start_mark)
            result[key] = loader.construct_object(value_node, deep=True)
        return result

    WorkflowLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
    return yaml, WorkflowLoader


def _load_workflow(text: str) -> dict[str, Any]:
    yaml, loader = _loader()
    try:
        result = yaml.load(text, Loader=loader)
    except yaml.YAMLError as exc:
        raise ValueError("invalid workflow YAML") from exc
    if not isinstance(result, dict):
        raise ValueError("workflow root must be a mapping")
    return result


def _events(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        return {value: {}}
    if isinstance(value, list):
        return {str(item): {} for item in value if isinstance(item, str)}
    if isinstance(value, dict):
        return {str(k): v or {} for k, v in value.items()}
    return {}


def _runner_values(value: Any, strategy: Any) -> tuple[list[str], bool]:
    """Resolve only literal labels and a directly referenced static matrix axis."""
    if isinstance(value, dict):
        value = value.get("labels", [])
    values = value if isinstance(value, list) else [value]
    resolved: list[str] = []
    unknown = False
    matrix = strategy.get("matrix", {}) if isinstance(strategy, dict) else {}
    for item in values:
        if not isinstance(item, str):
            unknown = True
            continue
        match = MATRIX.fullmatch(item)
        if match:
            axis = match.group(1)
            possibilities = matrix.get(axis) if isinstance(matrix, dict) else None
            if not isinstance(possibilities, list) or not possibilities:
                unknown = True
                continue
            for candidate in possibilities:
                if isinstance(candidate, str) and "${{" not in candidate:
                    resolved.append(candidate)
                else:
                    unknown = True
            includes = matrix.get("include", [])
            if isinstance(includes, list):
                for entry in includes:
                    if isinstance(entry, dict) and axis in entry:
                        candidate = entry[axis]
                        if isinstance(candidate, str) and "${{" not in candidate:
                            resolved.append(candidate)
                        else:
                            unknown = True
            if matrix.get("exclude"):
                unknown = True  # Exclusions are not evaluated in this bounded sensor.
        elif "${{" in item:
            unknown = True
        else:
            resolved.append(item)
    return sorted(set(resolved)), unknown


def _runner(value: Any, strategy: Any) -> dict[str, Any]:
    labels, unknown = _runner_values(value, strategy)
    hosted = any(HOSTED.match(label) for label in labels)
    self_hosted = "self-hosted" in labels
    other = [label for label in labels if label != "self-hosted" and not HOSTED.match(label)]
    if hosted and self_hosted:
        kind = "unknown"
        unknown = True
    elif hosted and not unknown and not other:
        kind = "github_hosted"
    elif self_hosted and not unknown:
        kind = "self_hosted"
    else:
        kind = "unknown"
    return {"classification": kind, "labels": labels, "unresolved": unknown,
            "github_hosted_possible": hosted, "self_hosted_declared": self_hosted}


def _permissions(value: Any) -> dict[str, Any]:
    if value is None:
        return {"classification": "unspecified", "write_scopes": []}
    if value == "write-all":
        return {"classification": "write_all", "write_scopes": ["*"]}
    if value == "read-all":
        return {"classification": "read_all", "write_scopes": []}
    if isinstance(value, dict):
        scopes = sorted(str(k) for k, v in value.items() if v == "write")
        return {"classification": "scoped", "write_scopes": scopes}
    return {"classification": "unknown", "write_scopes": []}


def _finding(code: str, source: str, subject: str, evidence: dict[str, Any],
             action: str, severity: str = "review") -> dict[str, Any]:
    return {"code": code, "severity": severity, "source": source,
            "subject": subject, "evidence": evidence, "recommended_action": action,
            "authority_required": True}


def _overlap(events: dict[str, Any]) -> bool:
    if "push" not in events or "pull_request" not in events:
        return False
    push, pr = events["push"], events["pull_request"]
    if not isinstance(push, dict) or not isinstance(pr, dict):
        return True
    if push.get("paths") or push.get("paths-ignore") or pr.get("paths") or pr.get("paths-ignore"):
        return False  # Unknown overlap: do not assert duplicate execution.
    push_branches = push.get("branches")
    pr_branches = pr.get("branches")
    if push_branches is None or pr_branches is None:
        return True
    if not isinstance(push_branches, list) or not isinstance(pr_branches, list):
        return False
    return bool(set(push_branches) & set(pr_branches))


def _inspect_workflow(path: str, data: dict[str, Any]) -> dict[str, Any]:
    events = _events(data.get("on"))
    jobs = data.get("jobs", {})
    findings: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    if not isinstance(jobs, dict) or any(not isinstance(key, str) for key in jobs):
        raise ValueError("jobs must be a mapping with string identifiers")
    concurrency = data.get("concurrency")
    if _overlap(events):
        findings.append(_finding("POTENTIAL_DUPLICATE_PUSH_PR", path, "workflow",
            {"events": events}, "Review trigger overlap and path/branch filters; preserve required checks."))
    for job_id, job in sorted(jobs.items()):
        if not isinstance(job, dict):
            findings.append(_finding("UNSUPPORTED_JOB", path, str(job_id), {}, "Review job structure."))
            continue
        delegated = isinstance(job.get("uses"), str)
        runner = _runner(job.get("runs-on"), job.get("strategy")) if not delegated else {
            "classification": "delegated", "labels": [], "unresolved": True,
            "github_hosted_possible": False, "self_hosted_declared": False}
        permissions = _permissions(job.get("permissions", data.get("permissions")))
        fingerprint = hashlib.sha256(json.dumps(job, sort_keys=True, default=str).encode()).hexdigest()
        record = {"id": str(job_id), "job_fingerprint": fingerprint, "runner": runner, "uses": job.get("uses"),
                  "permissions": permissions, "continue_on_error": job.get("continue-on-error", False),
                  "container": bool(job.get("container")), "environment": job.get("environment")}
        records.append(record)
        subject = f"jobs.{job_id}"
        if "pull_request_target" in events:
            findings.append(_finding("PR_TARGET_SECURITY_REVIEW", path, subject,
                {"runner": runner["classification"], "permissions": permissions},
                "Review privileged PR trigger, checkout ref, token permissions, and untrusted code execution before runner migration.", "high"))
        if "pull_request" in events and runner["self_hosted_declared"]:
            findings.append(_finding("SELF_HOSTED_PR_SECURITY_REVIEW", path, subject,
                {"runner_labels": runner["labels"]},
                "Verify fork policy, ephemeral isolation, secrets, and runner trust boundaries before accepting untrusted PRs.", "high"))
        if runner["github_hosted_possible"]:
            findings.append(_finding("GITHUB_HOSTED_RUNNER", path, subject,
                {"labels": runner["labels"]}, "Review migration to an authorized self-hosted runner; verify tools, isolation, and exact-head checks."))
        if runner["classification"] in {"unknown", "delegated"}:
            findings.append(_finding("RUNNER_UNRESOLVED", path, subject,
                {"runner": runner, "uses": job.get("uses")}, "Resolve matrix expressions or reusable workflow targets before claiming runner placement."))
        if permissions["write_scopes"]:
            findings.append(_finding("WRITE_PERMISSIONS_REVIEW", path, subject,
                {"permissions": permissions}, "Review least privilege and trusted execution before changing runner placement."))
        if job.get("continue-on-error") is True:
            findings.append(_finding("ADVISORY_JOB_REVIEW", path, subject, {},
                "Check whether advisory execution is needed on every PR; preserve required-check semantics."))
        if job.get("uses") and str(job["uses"]).startswith("./.github/workflows/"):
            record["local_reusable_workflow"] = str(job["uses"])
    return {"path": path, "name": data.get("name", path), "events": events,
            "concurrency": concurrency, "permissions": _permissions(data.get("permissions")),
            "jobs": records, "findings": findings}


def _shared_automatic_trigger(left: dict[str, Any], right: dict[str, Any]) -> bool:
    automatic = {"push", "pull_request", "pull_request_target", "schedule", "workflow_run", "release", "merge_group"}
    for event in sorted(set(left) & set(right) & automatic):
        a, b = left[event], right[event]
        if a == b:
            return True
        if not isinstance(a, dict) or not isinstance(b, dict):
            continue
        if any(a.get(key) or b.get(key) for key in ("paths", "paths-ignore")):
            continue
        aa, bb = a.get("branches"), b.get("branches")
        if aa is None or bb is None:
            return True
        if isinstance(aa, list) and isinstance(bb, list) and set(aa) & set(bb):
            return True
    return False


def _cross_workflow_findings(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings = []
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            if not _shared_automatic_trigger(left["events"], right["events"]):
                continue
            for a in left["jobs"]:
                for b in right["jobs"]:
                    if a["job_fingerprint"] != b["job_fingerprint"]:
                        continue
                    findings.append(_finding("POTENTIAL_DUPLICATE_WORKFLOW_JOB", right["path"], b["id"],
                        {"other_workflow": left["path"], "other_job": a["id"],
                         "job_fingerprint": a["job_fingerprint"]},
                        "Review overlapping automatic triggers and identical job definitions; retain required check identities before consolidating."))
    return findings


def inspect_ci(repo_root: Path | str, *, source_ref: str | None = None,
               usage: dict[str, Any] | None = None) -> dict[str, Any]:
    """Inventory a repository without invoking git, gh, workflow execution or network APIs."""
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"repository directory does not exist: {root}")
    workflow_dir = root / ".github" / "workflows"
    records: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    workflow_files = 0
    if (root / ".github").is_symlink() or workflow_dir.is_symlink():
        findings.append(_finding("WORKFLOW_DIRECTORY_SYMLINK", ".github/workflows", "workflow",
            {}, "Inspect the linked workflow directory explicitly; inventory is incomplete.", "high"))
    elif workflow_dir.is_dir():
        for path in sorted(workflow_dir.iterdir()):
            if path.suffix.lower() not in {".yml", ".yaml"}:
                continue
            if not path.is_file():
                findings.append(_finding("WORKFLOW_PARSE_ERROR", path.relative_to(root).as_posix(),
                    "workflow", {"error_type": "NotAFile"},
                    "Inspect the workflow manually; CI inventory is incomplete.", "high"))
                continue
            rel = path.relative_to(root).as_posix()
            workflow_files += 1
            try:
                if path.is_symlink():
                    raise ValueError("workflow symlinks require explicit review")
                if path.stat().st_size > MAX_WORKFLOW_BYTES:
                    raise ValueError("workflow exceeds inspection size limit")
                raw = path.read_bytes()
                if len(raw) > MAX_WORKFLOW_BYTES:
                    raise ValueError("workflow exceeds inspection size limit")
                sources.append({"path": rel, "sha256": hashlib.sha256(raw).hexdigest(),
                                "source_ref": source_ref})
                data = _load_workflow(raw.decode("utf-8"))
                record = _inspect_workflow(rel, data)
                records.append(record)
                findings.extend(record["findings"])
            except (OSError, UnicodeError, ValueError) as exc:
                findings.append(_finding("WORKFLOW_PARSE_ERROR", rel, "workflow",
                    {"error_type": type(exc).__name__}, "Inspect the workflow manually; CI inventory is incomplete.", "high"))
    elif workflow_dir.exists():
        findings.append(_finding("WORKFLOW_PARSE_ERROR", ".github/workflows", "workflow",
            {"error_type": "NotADirectory"}, "Inspect the workflow directory manually; inventory is incomplete.", "high"))
    findings.extend(_cross_workflow_findings(records))
    job_count = sum(len(w["jobs"]) for w in records)
    hosted = sum(j["runner"]["classification"] == "github_hosted" for w in records for j in w["jobs"])
    self_hosted = sum(j["runner"]["classification"] == "self_hosted" for w in records for j in w["jobs"])
    unknown = job_count - hosted - self_hosted
    possible = sum(j["runner"]["github_hosted_possible"] for w in records for j in w["jobs"])
    report = {"schema": SCHEMA, "repo": root.name, "repo_root": str(root),
              "source_ref": source_ref, "generated_at": datetime.now(timezone.utc).isoformat(),
              "evidence_complete": not any(f["code"] in {"WORKFLOW_DIRECTORY_SYMLINK", "WORKFLOW_PARSE_ERROR"} for f in findings),
              "sources": sources, "workflows": records,
              "summary": {"workflow_count": len(records), "workflow_files": workflow_files, "job_count": job_count,
                          "github_hosted_jobs": hosted, "github_hosted_possible_jobs": possible, "self_hosted_jobs": self_hosted,
                          "unknown_or_delegated_jobs": unknown, "finding_count": len(findings)},
              "findings": findings,
              "usage": {"availability": "unavailable", "billable_minutes": None, "billed_usd": None},
              "migration_checks": ["verify exact-head required-check names and branch protection",
                                   "verify runner registration, online status, labels, capacity and toolchain",
                                   "verify trust boundaries, permissions, secret handling and ephemeral isolation",
                                   "verify release, deployment and environment protection gates",
                                   "run representative parity tests before authorizing workflow changes"],
              "governance": {"authority": "evidence_only", "workflow_mutation": False,
                             "runner_registration": False, "migration_authorized": False}}
    if usage is not None:
        report["usage"] = _validate_usage(usage)
    return report


def _validate_usage(usage: dict[str, Any]) -> dict[str, Any]:
    """Accept only explicit measured aggregates, never invented price multipliers."""
    if not isinstance(usage, dict) or usage.get("schema") != "projectscanner.ci-usage.v1":
        raise ValueError("expected projectscanner.ci-usage.v1")
    source = usage.get("source")
    if not isinstance(source, str) or not source:
        raise ValueError("usage source is required")
    if usage.get("billable_minutes") is None and usage.get("billed_usd") is None:
        raise ValueError("at least one measured usage value is required")
    if usage.get("billed_usd") is not None and not usage.get("billing_source"):
        raise ValueError("billed_usd requires an explicit billing_source")
    for key in ("billable_minutes", "billed_usd"):
        value = usage.get(key)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
            raise ValueError(f"invalid measured {key}")
    return {"availability": "provided", "source": source, "period": usage.get("period"),
            "billable_minutes": usage.get("billable_minutes"), "billed_usd": usage.get("billed_usd"),
            "billing_source": usage.get("billing_source"), "measured": True}


def inspect_portfolio(projects_root: Path | str, repos: list[str] | None = None,
                      *, usage: dict[str, Any] | None = None) -> dict[str, Any]:
    root = Path(projects_root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"projects root does not exist: {root}")
    names = repos if repos is not None else sorted(p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))
    records = []
    for name in sorted(set(names)):
        if not name or Path(name).name != name or name in {".", ".."}:
            raise ValueError("repository names must be direct children")
        repo = root / name
        if repo.is_symlink():
            raise ValueError("repository symlinks require explicit review")
        if not repo.is_dir():
            raise FileNotFoundError(f"repository is unavailable: {name}")
        records.append(inspect_ci(repo))
    return {"schema": "projectscanner.ci-portfolio.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "projects_root": str(root), "repo_count": len(records), "repos": records,
            "summary": {"github_hosted_jobs": sum(r["summary"]["github_hosted_jobs"] for r in records),
                        "self_hosted_jobs": sum(r["summary"]["self_hosted_jobs"] for r in records),
                        "unknown_or_delegated_jobs": sum(r["summary"]["unknown_or_delegated_jobs"] for r in records)},
            "usage": _validate_usage(usage) if usage is not None else {"availability": "unavailable"},
            "governance": {"authority": "evidence_only", "migration_authorized": False}}


def write_ci_report(report: dict[str, Any], output: Path | str) -> Path:
    target = Path(output).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
