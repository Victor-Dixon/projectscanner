"""
MODULE: report_generator
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

import datetime as dt
import json
import logging
import re
from pathlib import Path
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class ReportGenerator:
    """SSOT report and context export helpers."""

    # Concept: TODO - Explain the core idea behind __init__
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def __init__(self, project_root: Path, analysis: Dict[str, Dict], output_dir: Path | None = None):
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        self.project_root = Path(project_root).resolve()
        self.output_dir = Path(output_dir).resolve() if output_dir else self.project_root
        self.analysis = analysis
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", self.project_root.name)
        self.analysis_file = f"project_analysis_{name}.json"
        self.context_file = f"chatgpt_project_context_{name}.json"

    # Concept: TODO - Explain the core idea behind load_existing_report
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def load_existing_report(self, report_path: Path) -> Dict:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        if report_path.exists():
            try:
                with report_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:  # pragma: no cover
                pass
        return {}

    # Concept: TODO - Explain the core idea behind save_report
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def save_report(self) -> Dict[str, Dict]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        report_path = self.output_dir / self.analysis_file
        existing_report = self.load_existing_report(report_path)
        merged = {**existing_report, **self.analysis}
        try:
            with report_path.open("w", encoding="utf-8") as f:
                json.dump(merged, f, indent=4)
            logger.info("✅ Merged analysis saved to: %s", report_path)
        except Exception as exc:  # pragma: no cover
            logger.error("❌ Error writing analysis report: %s", exc)
        self.save_snapshot_contract(merged)
        return merged

    def save_snapshot_contract(self, merged: Dict[str, Dict] | None = None) -> Path:
        """Write CI/ingest-compatible ``analysis.json`` with schema version."""
        from .snapshot_contract import build_snapshot_analysis

        payload_source = merged if merged is not None else self.analysis
        payload = build_snapshot_analysis(payload_source)
        contract_path = self.output_dir / "analysis.json"
        contract_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("✅ Snapshot contract saved to: %s", contract_path)
        return contract_path

    # Concept: TODO - Explain the core idea behind generate_init_files
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def generate_init_files(self, overwrite: bool = True):
    # Concept: TODO - Purpose of generate_init_files
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        for file, result in self.analysis.items():
            if result.get("language") != ".py":
                continue
            path = self.project_root / file
            if path.name == "__init__.py":
                continue
            init_file = path.parent / "__init__.py"
            if init_file.exists() and not overwrite:
                continue
            try:
                init_file.touch(exist_ok=True)
            except Exception as exc:  # pragma: no cover
                logger.error("❌ Could not create %s: %s", init_file, exc)

    # Concept: TODO - Explain the core idea behind export_bare_repo_metadata
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def export_bare_repo_metadata(self, run_git: Callable[..., tuple[int, str]]) -> None:
    # Concept: TODO - Purpose of export_bare_repo_metadata
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        code1, commit_count = run_git(self.project_root, "rev-list", "--count", "--all")
        code2, last_commit = run_git(self.project_root, "log", "-1", "--format=%ci")
        code3, branches = run_git(self.project_root, "for-each-ref", "refs/heads", "--format=%(refname:short)")
        payload = {
            "type": "bare_repo_metadata",
            "project_root": str(self.project_root),
            "generated_at": str(dt.datetime.now()),
            "commit_count": int(commit_count) if code1 == 0 and commit_count.isdigit() else 0,
            "last_commit": last_commit if code2 == 0 else "",
            "branches": [line for line in branches.splitlines() if line.strip()] if code3 == 0 else [],
            "note": "Bare repository detected. No working tree source files were scanned.",
        }
        out = self.output_dir / "bare_repo_metadata.json"
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Concept: TODO - Explain the core idea behind load_existing_chatgpt_context
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def load_existing_chatgpt_context(self, context_path: Path) -> Dict:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        if context_path.exists():
            try:
                with context_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:  # pragma: no cover
                pass
        return {}

    # Concept: TODO - Explain the core idea behind export_chatgpt_context
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 39 lines > 30 limit)
    def export_chatgpt_context(
    # Concept: TODO - Purpose of export_chatgpt_context
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        self,
        template_path: str = None,
        output_path: str | None = None,
        split_by: str = "directory",
        max_files_per_chunk: int = 100,
    ):
        context_path = self.output_dir / (output_path or self.context_file)
        if template_path is None:
            existing_context = self.load_existing_chatgpt_context(context_path)
            payload = {
                "project_root": str(self.project_root),
                "num_files_analyzed": len(self.analysis),
                "analysis_details": self.analysis,
            }
            merged = {**existing_context, **payload}
            context_path.write_text(json.dumps(merged, indent=4), encoding="utf-8")
            self._export_context_chunks(split_by=split_by, max_files_per_chunk=max_files_per_chunk)
            return

        try:
            from jinja2 import Template
            template_content = Path(template_path).read_text(encoding="utf-8")
            t = Template(template_content)
            context_dict = {
                "project_root": str(self.project_root),
                "analysis": self.analysis,
                "num_files_analyzed": len(self.analysis),
            }
            rendered = t.render(context=context_dict)
            context_path.write_text(rendered, encoding="utf-8")
            logger.info("✅ Rendered ChatGPT context to: %s", output_path)
        except ImportError:
            logger.error("⚠️ Jinja2 not installed. Run `pip install jinja2` and re-try.")
        except Exception as exc:  # pragma: no cover
            logger.error("❌ Error rendering Jinja template: %s", exc)

    # Concept: TODO - Explain the core idea behind _export_context_chunks
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _export_context_chunks(self, split_by: str = "directory", max_files_per_chunk: int = 100) -> None:
    # Concept: TODO - Purpose of _export_context_chunks
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        reports_dir = self.output_dir / "runtime" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        items = list(self.analysis.items())

        if split_by == "none":
            chunks = [(f"project_context_chunk_{i // max_files_per_chunk + 1}.json", dict(items[i:i + max_files_per_chunk]))
                      for i in range(0, len(items), max_files_per_chunk)]
        else:
            grouped: Dict[str, Dict] = {}
            for path, data in self.analysis.items():
                key = Path(path).suffix.lower().lstrip(".") if split_by == "language" else (Path(path).parts[0] if len(Path(path).parts) > 1 else "_root_")
                grouped.setdefault(key, {})[path] = data
            chunks = [(f"project_context_{k}.json", v) for k, v in grouped.items()]

        index: List[Dict] = []
        for filename, payload in chunks:
            (reports_dir / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")
            index.append({"path": filename, "file_count": len(payload)})

        (reports_dir / "project_context_index.json").write_text(
            json.dumps({"chunks": index, "total_files": len(self.analysis), "generated_at": str(dt.datetime.now())}, indent=2),
            encoding="utf-8",
        )
