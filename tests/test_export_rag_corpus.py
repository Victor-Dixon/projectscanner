from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from scripts.export_rag_corpus import (
    SCHEMA_VERSION,
    classify_domain,
    discover_files,
    export_repo,
    repo_provenance,
)


def test_classify_domain_routes_dreamos_and_trading() -> None:
    assert classify_domain("DreamOS", "runtime/planner.py") == "dreamos_core"
    assert classify_domain("tradingrobotplug", "docs/tsla_strategy.md") == "trading"


def test_discover_files_excludes_generated_and_binary_paths(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    (tmp_path / "data.json").write_text("{}", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"not indexed")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "skip.md").write_text("skip", encoding="utf-8")

    relative = [p.relative_to(tmp_path).as_posix() for p in discover_files(tmp_path)]

    assert relative == ["data.json", "README.md"]


def test_export_repo_writes_provenance_rich_jsonl(tmp_path: Path) -> None:
    repo = tmp_path / "DreamOS"
    repo.mkdir()
    source = "Dream.OS uses ProjectScanner."
    (repo / "README.md").write_text(source, encoding="utf-8")
    output = tmp_path / "corpus.jsonl"

    count = export_repo(repo, output, authority="canonical_source", max_bytes=1024)

    assert count == 1
    records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    record = records[0]

    assert record["schema_version"] == SCHEMA_VERSION
    assert record["repo"] == "DreamOS"
    assert record["path"] == "README.md"
    assert record["domain"] == "dreamos_core"
    assert record["authority"] == "canonical_source"
    assert record["document_id"].startswith("sha256:")
    assert record["source_sha256"] == hashlib.sha256(source.encode("utf-8")).hexdigest()
    assert record["content_sha256"] == hashlib.sha256(record["content"].encode("utf-8")).hexdigest()
    assert record["terminology"]["Dream.OS"] == "DreamOS"
    assert record["terminology"]["ProjectScanner"] == "projectscanner"
    assert set(record["provenance"]) == {"branch", "head", "remote"}
    assert record["truncated"] is False


def test_export_repo_resolves_provenance_once_per_repo(tmp_path: Path) -> None:
    repo = tmp_path / "DreamOS"
    repo.mkdir()
    (repo / "one.md").write_text("one", encoding="utf-8")
    (repo / "two.md").write_text("two", encoding="utf-8")
    output = tmp_path / "corpus.jsonl"

    with patch("scripts.export_rag_corpus.repo_provenance", wraps=repo_provenance) as mocked:
        count = export_repo(repo, output, authority="canonical_source", max_bytes=1024)

    assert count == 2
    assert mocked.call_count == 1


def test_export_repo_marks_truncated_content_and_hashes_exported_text(tmp_path: Path) -> None:
    repo = tmp_path / "DreamOS"
    repo.mkdir()
    source = "abcdefghij"
    (repo / "notes.md").write_text(source, encoding="utf-8")
    output = tmp_path / "corpus.jsonl"

    export_repo(repo, output, authority="canonical_docs", max_bytes=4)
    record = json.loads(output.read_text(encoding="utf-8").strip())

    assert record["content"] == "abcd"
    assert record["truncated"] is True
    assert record["source_sha256"] == hashlib.sha256(source.encode("utf-8")).hexdigest()
    assert record["content_sha256"] == hashlib.sha256(b"abcd").hexdigest()
    assert record["document_id"] == f"sha256:{record['source_sha256']}"


def test_export_repo_hashes_decoded_replacement_text_for_non_utf8_source(tmp_path: Path) -> None:
    repo = tmp_path / "DreamOS"
    repo.mkdir()
    raw = b"hello\xffworld"
    (repo / "legacy.txt").write_bytes(raw)
    output = tmp_path / "corpus.jsonl"

    export_repo(repo, output, authority="canonical_source", max_bytes=1024)
    record = json.loads(output.read_text(encoding="utf-8").strip())

    assert record["source_sha256"] == hashlib.sha256(raw).hexdigest()
    assert record["content_sha256"] == hashlib.sha256(record["content"].encode("utf-8")).hexdigest()
    assert record["document_id"] == f"sha256:{record['source_sha256']}"
