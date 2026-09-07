"""CI cost sensor contract and safety regression tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.intelligence.ci_cost import inspect_ci, inspect_portfolio, write_ci_report


def workflow(root: Path, name: str, text: str) -> Path:
    directory = root / '.github' / 'workflows'
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(text, encoding='utf-8')
    return path


def test_hosted_runner_and_trigger_overlap(tmp_path):
    workflow(tmp_path, 'ci.yml', '''name: CI
on:
  push:
  pull_request:
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - run: pytest -q
''')
    result = inspect_ci(tmp_path, source_ref='abc123')
    assert result['schema'] == 'projectscanner.ci-cost.v1'
    assert result['evidence_complete'] is True
    assert result['workflows'][0]['events'] == {'push': {}, 'pull_request': {}}
    assert result['summary']['github_hosted_jobs'] == 1
    assert result['usage']['billed_usd'] is None
    assert {f['code'] for f in result['findings']} == {
        'GITHUB_HOSTED_RUNNER', 'POTENTIAL_DUPLICATE_PUSH_PR'}
    assert result['sources'][0]['source_ref'] == 'abc123'
    assert len(result['sources'][0]['sha256']) == 64


def test_self_hosted_matrix_and_unknown_are_distinct(tmp_path):
    workflow(tmp_path, 'matrix.yaml', '''on: workflow_dispatch
jobs:
  local:
    runs-on: [self-hosted, Linux, X64, dreamvault-vps]
  matrix:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-2022]
    runs-on: ${{ matrix.os }}
  dynamic:
    runs-on: ${{ vars.RUNNER }}
  reusable:
    uses: ./.github/workflows/reusable.yml
''')
    result = inspect_ci(tmp_path)
    kinds = {j['id']: j['runner']['classification'] for j in result['workflows'][0]['jobs']}
    assert kinds == {'local': 'self_hosted', 'matrix': 'github_hosted', 'dynamic': 'unknown', 'reusable': 'delegated'}
    assert result['summary']['unknown_or_delegated_jobs'] == 2
    assert result['summary']['github_hosted_jobs'] == 1
    assert result['summary']['self_hosted_jobs'] == 1


def test_matrix_exclusion_and_mixed_labels_do_not_claim_placement(tmp_path):
    workflow(tmp_path, 'ci.yml', '''on: push
jobs:
  matrix:
    strategy:
      matrix:
        os: [ubuntu-latest, self-hosted]
        exclude:
          - os: ubuntu-latest
    runs-on: ${{ matrix.os }}
  mixed:
    runs-on: [self-hosted, ubuntu-latest]
''')
    result = inspect_ci(tmp_path)
    assert result['summary']['github_hosted_jobs'] == 0
    assert result['summary']['unknown_or_delegated_jobs'] == 2
    assert result['summary']['github_hosted_possible_jobs'] == 2


def test_malformed_yaml_and_duplicate_keys_fail_closed(tmp_path):
    workflow(tmp_path, 'bad.yml', 'on: push\njobs: [\n')
    workflow(tmp_path, 'duplicate.yml', 'on: push\non: pull_request\njobs: {}\n')
    result = inspect_ci(tmp_path)
    assert result['evidence_complete'] is False
    assert len(result['workflows']) == 0
    assert len([f for f in result['findings'] if f['code'] == 'WORKFLOW_PARSE_ERROR']) == 2
    assert result['summary']['workflow_files'] == 2


def test_yaml_tags_are_not_executed(tmp_path):
    workflow(tmp_path, 'evil.yml', '!!python/object/apply:os.system ["touch /tmp/projectscanner-evil"]')
    result = inspect_ci(tmp_path)
    assert result['evidence_complete'] is False
    assert any(f['code'] == 'WORKFLOW_PARSE_ERROR' for f in result['findings'])


def test_pull_request_target_and_self_hosted_pr_require_security_review(tmp_path):
    workflow(tmp_path, 'ci.yml', '''on: [pull_request, pull_request_target]
permissions: write-all
jobs:
  test:
    runs-on: [self-hosted, Linux]
    steps:
      - uses: actions/checkout@v4
''')
    result = inspect_ci(tmp_path)
    codes = {f['code'] for f in result['findings']}
    assert 'PR_TARGET_SECURITY_REVIEW' in codes
    assert 'SELF_HOSTED_PR_SECURITY_REVIEW' in codes
    assert 'WRITE_PERMISSIONS_REVIEW' in codes
    assert all(f['authority_required'] for f in result['findings'])


def test_path_filters_are_not_assumed_duplicate(tmp_path):
    workflow(tmp_path, 'ci.yml', '''on:
  push:
    paths: [src/**]
  pull_request:
    paths: [docs/**]
jobs:
  test:
    runs-on: ubuntu-latest
''')
    result = inspect_ci(tmp_path)
    assert 'POTENTIAL_DUPLICATE_PUSH_PR' not in {f['code'] for f in result['findings']}


def test_cross_workflow_identical_jobs_flag_potential_duplicate(tmp_path):
    text = '''on:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest -q
'''
    workflow(tmp_path, 'a.yml', text)
    workflow(tmp_path, 'b.yml', text)
    result = inspect_ci(tmp_path)
    assert sum(f['code'] == 'POTENTIAL_DUPLICATE_WORKFLOW_JOB' for f in result['findings']) == 1
    assert result['summary']['job_count'] == 2


def test_usage_is_measured_only_when_supplied(tmp_path):
    data = {'schema': 'projectscanner.ci-usage.v1', 'source': 'github.actions.billing',
            'billing_source': 'billing-export-001', 'period': '2026-09',
            'billable_minutes': 42, 'billed_usd': 0.0}
    result = inspect_ci(tmp_path, usage=data)
    assert result['usage']['billable_minutes'] == 42
    assert result['usage']['billed_usd'] == 0.0
    assert result['usage']['measured'] is True
    assert result['summary']['job_count'] == 0
    for bad in ({'schema': 'wrong', 'source': 'x'},
                {**data, 'billable_minutes': -1},
                {**data, 'billed_usd': True},
                {**data, 'billing_source': None}):
        with pytest.raises(ValueError):
            inspect_ci(tmp_path, usage=bad)


def test_portfolio_is_sorted_and_rejects_traversal(tmp_path):
    projects = tmp_path / 'projects'
    (projects / 'b').mkdir(parents=True)
    (projects / 'a').mkdir()
    workflow(projects / 'a', 'ci.yml', 'on: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n')
    result = inspect_portfolio(projects)
    assert [r['repo'] for r in result['repos']] == ['a', 'b']
    assert result['summary']['github_hosted_jobs'] == 1
    with pytest.raises(ValueError):
        inspect_portfolio(projects, repos=['../other'])
    with pytest.raises(FileNotFoundError):
        inspect_portfolio(projects, repos=['missing'])
    output = write_ci_report(result, tmp_path / 'out' / 'ci.json')
    assert json.loads(output.read_text())['schema'] == 'projectscanner.ci-portfolio.v1'


def test_scan_never_executes_workflow_commands(tmp_path, monkeypatch):
    workflow(tmp_path, 'ci.yml', 'on: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: rm -rf /\n')
    import subprocess
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: pytest.fail('subprocess invoked'))
    assert inspect_ci(tmp_path)['summary']['job_count'] == 1


def test_no_workflows_is_not_a_claim_about_live_github(tmp_path):
    result = inspect_ci(tmp_path)
    assert result['summary']['workflow_count'] == 0
    assert result['usage']['availability'] == 'unavailable'
    assert result['governance']['migration_authorized'] is False
    assert result['source_ref'] is None


def test_symlinked_workflow_directory_is_incomplete(tmp_path):
    target = tmp_path / 'external'
    target.mkdir()
    root = tmp_path / 'repo'
    (root / '.github').mkdir(parents=True)
    (root / '.github/workflows').symlink_to(target, target_is_directory=True)
    report = inspect_ci(root)
    assert report['evidence_complete'] is False
    assert report['findings'][0]['code'] == 'WORKFLOW_DIRECTORY_SYMLINK'


def test_malformed_source_still_retains_digest(tmp_path):
    path = workflow(tmp_path, 'bad.yml', 'on: push\njobs: [\n')
    report = inspect_ci(tmp_path, source_ref='reviewed-head')
    import hashlib
    assert report['sources'] == [{'path': '.github/workflows/bad.yml',
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source_ref': 'reviewed-head'}]


def test_yaml_loader_does_not_change_global_safe_loader(tmp_path):
    import yaml
    assert yaml.safe_load('on: push') == {True: 'push'}
    workflow(tmp_path, 'ci.yml', 'on: push\njobs: {}\n')
    assert inspect_ci(tmp_path)['workflows'][0]['events'] == {'push': {}}
    assert yaml.safe_load('on: push') == {True: 'push'}


def test_usage_rejects_nonfinite_and_boolean_values(tmp_path):
    data = {'schema': 'projectscanner.ci-usage.v1', 'source': 'measured', 'billable_minutes': 1}
    for value in [float('nan'), float('inf'), float('-inf'), True]:
        with pytest.raises(ValueError):
            inspect_ci(tmp_path, usage={**data, 'billable_minutes': value})


def test_invalid_job_identifiers_are_incomplete(tmp_path):
    workflow(tmp_path, 'bad.yml', 'on: push\njobs:\n  1:\n    runs-on: ubuntu-latest\n  test:\n    runs-on: ubuntu-latest\n')
    report = inspect_ci(tmp_path)
    assert report['evidence_complete'] is False
    assert report['summary']['github_hosted_jobs'] == 0


def test_workflow_parent_symlink_and_nondirectory_fail_closed(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    root = tmp_path / 'repo'
    root.mkdir()
    (root / '.github').symlink_to(outside, target_is_directory=True)
    assert inspect_ci(root)['evidence_complete'] is False
    second = tmp_path / 'repo2'
    (second / '.github').mkdir(parents=True)
    (second / '.github/workflows').write_text('not a directory')
    assert inspect_ci(second)['evidence_complete'] is False
