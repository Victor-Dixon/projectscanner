# Project Scanner PRD

## Overview
Project Scanner delivers rapid, language-agnostic insight into codebases by generating structured JSON summaries and optional LLM context.

## Goals
- Map unfamiliar repositories quickly.
- Provide exportable context for large language models.
- Offer a minimal GUI for non-terminal users.

## Current Status
- Python, Rust, JavaScript, and TypeScript parsers available.
- Incremental caching and multithreaded scanning in place.
- PyQt5 GUI for viewing results.
- Context export for ChatGPT and similar models.

## Problem Statement
Developers often need quick insight into unfamiliar repositories. Manually exploring source files is time-consuming. Project Scanner automates static analysis so teams can rapidly understand project structure and feed the data into automation workflows.

## Solution Overview
- Multi-language parsing using ASTs (Python) and optional tree-sitter parsers (Rust/JS/TS)
- Incremental caching to skip unchanged files
- Concurrent file processing via worker threads
- Agent categorisation of Python classes by maturity and type
- Export of simplified context for ChatGPT or other LLM prompts
- Optional PyQt5 GUI viewer for generated JSON

## Key Features
1. Command-line interface to scan projects and manage options
2. Report generator merges analysis results and writes JSON files
3. Plugin-style language analyser for multiple languages
4. Support for generating `__init__.py` files after analysis
5. ChatGPT context export for LLM integrations

## User Stories
- As a developer, I can scan a repository to obtain an overview of its modules and classes.
- As an AI engineer, I can export simplified context to feed into an LLM prompt.
- As a researcher, I can quickly compare project structures across languages.

## Non-Goals
- Runtime or dynamic code analysis
- Automatic code generation or refactoring
- Deep language-specific metrics beyond simple complexity counts

## Success Metrics
- CLI produces valid JSON summaries for supported languages
- All unit tests pass (`pytest`)
- Scanning a medium-sized project (100+ files) finishes within a few minutes on a typical laptop

## Future Enhancements
- Packaging optional tree-sitter grammars for Rust and JavaScript
- Support for additional languages via plugins
- More granular complexity metrics and lint-style suggestions
