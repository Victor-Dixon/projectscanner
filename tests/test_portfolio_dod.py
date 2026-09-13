"""Regression tests for the portfolio Definition-of-Done evaluator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from projectscanner.dod import (
    STATUS_BLOCKED,
    STATUS_DONE,
    STATUS_DONE_WITH_KEEP,
    STATUS_NOT_READY,
    evaluate_definition_of_done,
    evaluate_from_registry,
    load_json,
)

REGISTRY = Path(__file__).resolve().parents[1] / "portfolio" / "dod"
CONTRACT = REGISTRY / "contract.json"
PROFILES = REGISTRY / "profiles.json"
KEYS = REGISTRY / "repository_keys.json"


def _profile(**overrides):
    profile = {
        "repository": "projectscanner",
        "mvp": "headless evidence producer",
        "done_when": ["relevant_tests_green", "completion_receipt_written"],
    }
    profile.update(overrides)
    return profile


def test_all_evidence_true_is_done():
    result = evaluate_definition_of_done(
        _profile(),
        {"relevant_tests_green": True, "completion_receipt_written": True},
    )
    assert result["status"] == STATUS_DONE
    assert result["failed"] == []
    assert result["unknown"] == []


def test_missing_evidence_is_not_ready_not_pass():
    result = evaluate_definition_of_done(_profile(), {"relevant_tests_green": True})
    assert result["status"] == STATUS_NOT_READY
    assert result["unknown"] == ["completion_receipt_written"]
    assert result["checks"]["completion_receipt_written"]["status"] == "UNKNOWN"


def test_false_evidence_blocks_and_outranks_unknown():
    result = evaluate_definition_of_done(
        _profile(),
        {"relevant_tests_green": False},
    )
    assert result["status"] == STATUS_BLOCKED
    assert result["failed"] == ["relevant_tests_green"]
    assert result["unknown"] == ["completion_receipt_written"]


def test_truthy_non_true_evidence_is_not_a_pass():
    """Only literal True counts; "yes"/1-ish values must not silently pass."""
    result = evaluate_definition_of_done(
        _profile(),
        {"relevant_tests_green": "yes", "completion_receipt_written": True},
    )
    assert result["status"] == STATUS_NOT_READY


def test_intentional_keep_reported_when_otherwise_done():
    result = evaluate_definition_of_done(
        _profile(),
        {
            "relevant_tests_green": True,
            "completion_receipt_written": True,
            "intentional_keep": True,
        },
    )
    assert result["status"] == STATUS_DONE_WITH_KEEP


def test_specialized_requirements_are_evaluated_without_duplication():
    result = evaluate_definition_of_done(
        _profile(specialized_done=["relevant_tests_green", "headless_scan_reproducible"]),
        {"relevant_tests_green": True, "completion_receipt_written": True},
    )
    assert result["unknown"] == ["headless_scan_reproducible"]
    assert list(result["checks"]).count("relevant_tests_green") == 1


def test_result_declares_no_mutation_authority():
    result = evaluate_definition_of_done(_profile(), {})
    assert result["evidence_only"] is True
    assert result["mutation_authority"] is False
    assert result["schema_version"] == "dreamos.repository-dod-result.v1"


def test_registry_evaluation_applies_common_requirements():
    contract = load_json(CONTRACT)
    repository = next(iter(load_json(PROFILES)["profiles"]))
    result = evaluate_from_registry(CONTRACT, PROFILES, repository, {})

    assert result["repository"] == repository
    assert result["status"] == STATUS_NOT_READY
    assert set(contract["common_requirements"]).issubset(result["checks"])


def test_registry_evaluation_rejects_unknown_repository():
    with pytest.raises(KeyError):
        evaluate_from_registry(CONTRACT, PROFILES, "not-a-repository", {})


def test_contract_declares_portfolio_of_twenty_five_keys():
    contract = load_json(CONTRACT)
    keys = load_json(KEYS)["repositories"]

    assert contract["portfolio_size"] == 25
    assert len(keys) == 25
    assert len(set(keys)) == 25


def test_every_profile_names_a_registered_repository_and_an_mvp():
    keys = set(load_json(KEYS)["repositories"])
    profiles = load_json(PROFILES)["profiles"]

    assert profiles, "profiles registry must not be empty"
    for name, profile in profiles.items():
        assert name in keys, f"profile for unregistered repository: {name}"
        assert profile.get("mvp"), f"profile missing MVP statement: {name}"


def test_registry_files_are_valid_json_objects():
    for path in (CONTRACT, PROFILES, KEYS, REGISTRY / "schema.json"):
        assert isinstance(json.loads(path.read_text(encoding="utf-8")), dict)


def test_load_json_rejects_non_object(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(ValueError):
        load_json(bad)
