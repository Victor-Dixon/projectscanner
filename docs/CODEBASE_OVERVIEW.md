# Codebase Overview

This document summarizes the main modules of ProjectScanner and serves as the repository's current architecture overview.

## Architecture summary

ProjectScanner is a Python scanner and reporting tool. The canonical scanner implementation lives under `src/core/projectscanner/`; older overlays and copied repositories under `archive/`, `github_library/`, `github_library_enhanced/`, and `temp_repos/` are evidence or historical inputs, not active architecture.

The runtime shape is:

1. CLI or utility entrypoints receive a repository path.
2. Scanner orchestration walks the target tree, applies ignore/cache rules, and delegates file parsing.
3. File processors and language analyzers extract structural signals such as functions, classes, routes, hashes, and file metadata.
4. Report generation writes machine-readable outputs for downstream consumers.
5. DreamVault and governance lanes consume those outputs but remain the source of truth for portfolio decisions.

## Ownership boundaries

| Area | Owner |
|---|---|
| Scanning mechanics, parser orchestration, cache behavior | ProjectScanner |
| Portfolio intelligence storage and promotion decisions | DreamVault |
| Operator/control-plane tooling that invokes scanners | AgentTools |
| Runtime/swarm execution | DreamOS |

## Verification

Use `pytest -q` for the local regression gate. Documentation-only updates should also pass `git diff --check`.

## project_scanner.py
Entry point that forwards to `project-scanner.cli.main`.

## project-scanner/cli.py
Defines the command line interface. Parses arguments and orchestrates the scanning process using `project-scanner`.

## project-scanner/scanner.py
High-level orchestrator. Handles scanning directories, delegating to `FileProcessor` and `LanguageAnalyzer`. Manages worker threads through `MultibotManager` and writes results via `ReportGenerator`.

## project-scanner/file_processor.py
Provides helper functions to hash files, skip virtual environments and other directories, and cache results to avoid reprocessing unchanged files.

## project-scanner/language_analyzer.py
Parses source files. Uses Python's `ast` module and optional tree-sitter parsers for Rust and JavaScript/TypeScript. Extracts functions, classes and web routes.

## project-scanner/report_generator.py
Merges analysis results and writes JSON reports. Can also generate `__init__.py` files and export simplified context for ChatGPT.

## project-scanner/bots.py
Implements `BotWorker` threads and `MultibotManager` for concurrent processing.

## project-scanner/gui.py
A small PyQt5 application to view the generated JSON files in a tree widget.

## tests/
Contains unit tests for the analyzer and helper functions. Run `pytest` to execute them.

