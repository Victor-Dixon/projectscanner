# Codebase Overview

This document summarizes the main modules of project-scanner.

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

