import json
from datetime import UTC, datetime
from pathlib import Path

from projectscanner.export_intelligence import write_bundle
from projectscanner.planning_contract import SCHEMA_VERSION, inspect_planning_contract


def _write(repo: Path, name: str, content: str) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_complete_planning_set(repo: Path) -> None:
    _write(repo, "MASTER_TASK_LIST.md", "# Tasks\n\nLast synchronized: 2026-08-12\n")
    _write(repo, "MASTER_TASK_LOG.md", "# Log\n\nLast synchronized: 2026-08-12\n")
    _write(
        repo,
        "NEXT_UP.md",
        "# Next\n\nLast synchronized: 2026-08-12\n\n"
        "## Immediate actions\n\n"
        "1. **Stabilize fleet planning contract.** Emit normalized evidence.\n"
        "2. Verify portfolio export.\n",
    )
    _write(repo, "docs/DOMAIN_MODEL.md", "# Domain\n\nLast synchronized: 2026-08-12\n")


def test_planning_contract_normalizes_active_lane(tmp_path: Path) -> None:
    _write_complete_planning_set(tmp_path)

    result = inspect_planning_contract(
        tmp_path,
        generated_at=datetime(2026, 8, 12, tzinfo=UTC),
    )

    assert result["schema_version"] == SCHEMA_VERSION
    assert result["contract_status"] == "PASS"
    assert result["domain_model"] == "docs/DOMAIN_MODEL.md"
    assert result["active_lane"] == "Stabilize fleet planning contract"
    assert len(result["next_actions"]) == 2
    assert result["findings"] == []


def test_planning_contract_reports_missing_authority_files(tmp_path: Path) -> None:
    _write(tmp_path, "NEXT_UP.md", "# Next\n")

    result = inspect_planning_contract(tmp_path)

    assert result["contract_status"] == "FAIL"
    codes = {item["code"] for item in result["findings"]}
    assert "missing_required_file" in codes
    assert "missing_domain_model" in codes
    assert "missing_immediate_actions" in codes


def test_planning_contract_warns_on_date_drift_and_action_overflow(tmp_path: Path) -> None:
    _write(tmp_path, "MASTER_TASK_LIST.md", "Last synchronized: 2026-08-11\n")
    _write(tmp_path, "MASTER_TASK_LOG.md", "Last synchronized: 2026-08-12\n")
    actions = "\n".join(f"{idx}. Task {idx}" for idx in range(1, 7))
    _write(
        tmp_path,
        "NEXT_UP.md",
        f"Last synchronized: 2026-08-12\n\n## Immediate actions\n\n{actions}\n",
    )
    _write(tmp_path, "DOMAIN_MODEL.md", "Last synchronized: 2026-08-12\n")

    result = inspect_planning_contract(tmp_path)

    assert result["contract_status"] == "WARN"
    codes = {item["code"] for item in result["findings"]}
    assert codes == {"planning_sync_date_drift", "too_many_immediate_actions"}


def test_planning_contract_warns_when_required_file_is_pointer(tmp_path: Path) -> None:
    _write_complete_planning_set(tmp_path)
    _write(
        tmp_path,
        "MASTER_TASK_LOG.md",
        "# Log\n\nLast synchronized: 2026-08-12\n\n"
        "Status: Non-canonical compatibility pointer\n",
    )

    result = inspect_planning_contract(tmp_path)

    assert result["contract_status"] == "WARN"
    assert result["findings"] == [
        {
            "severity": "warning",
            "code": "required_file_is_pointer",
            "path": "MASTER_TASK_LOG.md",
        }
    ]


def test_portfolio_bundle_contains_planning_contract(tmp_path: Path) -> None:
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    _write_complete_planning_set(repo)
    _write(repo, "README.md", "# Demo\n")
    _write(repo, "PRD.md", "# PRD\n")
    _write(repo, "ROADMAP.md", "# Roadmap\n")
    out_root = tmp_path / "out"

    write_bundle(repo, out_root)

    planning = json.loads((out_root / repo.name / "planning_contract.json").read_text())
    context = json.loads((out_root / repo.name / "chatgpt_context.json").read_text())
    assert planning["contract_status"] == "PASS"
    assert planning["active_lane"] == "Stabilize fleet planning contract"
    assert context["current_state"]["planning_contract_status"] == "PASS"
    assert context["operator_guidance"]["safe_next_action"] == "maintain"
