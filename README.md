# ProjectScanner

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ProjectScanner is a lightweight tool for generating a structured overview of a codebase. It scans Python, Rust and JavaScript/TypeScript files and produces JSON reports that are easy to feed into language models or other automation systems. The project demonstrates multithreaded file processing, AST analysis and incremental caching.

## Key Features

- **Multi‑language parsing** – Python, Rust and JS/TS support
- **Concurrent scanning** – worker threads handle files in parallel
- **Incremental caching** – skip previously processed files
- **Agent categorisation** – classify Python classes by maturity level and type
- **ChatGPT context export** – minimal JSON payload for LLM prompts
- **Enhanced GUI** – comprehensive interface for scanning directories and GitHub repositories
- **Project Library** – store and manage multiple project analyses
- **Complexity metrics** – reports include simple complexity counts and lint suggestions

## Architecture Overview

```
CLI -> ProjectScanner -> MultibotManager -> BotWorker threads
                 |            |
                 |            +-- FileProcessor (hashing & caching)
                 |            |  
                 |            +-- LanguageAnalyzer (AST parsing)
                 +-- ReportGenerator (JSON export)
```

The CLI creates a `ProjectScanner` which spawns `BotWorker` threads via `MultibotManager`. Each worker uses `LanguageAnalyzer` and `FileProcessor` to parse and cache results, then `ReportGenerator` merges everything into JSON.

## Setup

1. Clone this repository and install the package in editable mode:
   ```bash
   pip install -e .
   ```
2. Install `PyQt5` for the enhanced GUI:
   ```bash
   pip install PyQt5
   ```

## Usage

### Main Entry Point

The application can be run in two modes:

```bash
# GUI mode (default)
python main.py

# CLI mode
python main.py --cli --project-root . --categorize-agents
```

### Command Line Interface

Run the scanner from a project directory:

```bash
project-scanner --project-root .
```

The command creates two files in the root:

- `project_analysis_<name>.json` – merged summary of all files
- `chatgpt_project_context_<name>.json` – reduced context for ChatGPT

Useful flags:

- `--categorize-agents` – add maturity/agent type details to classes
- `--generate-init` – automatically create `__init__.py` files
- `--no-chatgpt-context` – skip the ChatGPT context export
- `--output-dir` – directory to store generated JSON reports

### Enhanced GUI

Launch the enhanced GUI for a comprehensive scanning experience:

```bash
# Using Python directly
python main.py --gui
# or simply (GUI is default)
python main.py

# Using provided scripts
# Windows:
run_gui.bat

# Unix/Linux:
./run_gui.sh
```

### GitHub Library Scanner

#### Public Repositories Only
Scan all public repositories from a GitHub account and build a library:

```bash
# Scan all repositories for a GitHub user
python github_library_scanner.py YOUR_USERNAME

# Scan with options
python github_library_scanner.py YOUR_USERNAME --max-repos 50 --force-rescan

# Generate summary only
python github_library_scanner.py YOUR_USERNAME --summary-only
```

#### Public + Private Repositories (Enhanced)
To scan both public and private repositories, use the enhanced scanner with GitHub Personal Access Token:

##### Easy Setup Wizard (Recommended)

###### GUI Version (Easiest)
```bash
# Windows
setup_private_repos_gui.bat

# Unix/Linux/Mac
./setup_private_repos_gui.sh

# Or directly
python github_token_wizard_gui.py
```

###### Command Line Version
```bash
# Windows
setup_private_repos.bat

# Unix/Linux/Mac
./setup_private_repos.sh

# Or directly
python github_token_wizard.py
```

##### Manual Setup
1. Create a GitHub Personal Access Token (see `GITHUB_TOKEN_GUIDE.md`)
2. Run the enhanced scanner:
```bash
python github_library_scanner_private.py YOUR_USERNAME --token YOUR_TOKEN
```

##### Enhanced Scanner Features
- ✅ **Public repositories**: All metadata and code analysis
- ✅ **Private repositories**: All metadata and code analysis  
- 📊 **Separate tracking** of public vs private projects
- 🔒 **Privacy indicators** in the library
- 🔐 **Token-based authentication** for private repos

#### GUI Features:

1. **Directory Scanning**
   - Browse and select any directory on your system
   - Scan local projects with progress tracking
   - View detailed analysis results in a tree structure

2. **GitHub Repository Scanning**
   - Enter any GitHub repository URL
   - Automatically clones and scans the repository
   - Supports both HTTPS and SSH URLs
   - Temporary cloning with automatic cleanup

3. **GitHub Library Scanning**
   - Scan entire GitHub accounts (all repositories)
   - Build comprehensive library of project analyses
   - Automatic naming and storage management
   - Progress tracking and error handling
   - Force rescan and repository limits

4. **Project Library Management**
   - Save scan results to a local library
   - View all scanned projects with statistics
   - Export/import library data
   - Delete projects from the library
   - Quick access to previous scan results

5. **Real-time Progress Tracking**
   - Live progress updates during scanning
   - Background processing with thread safety
   - Error handling and user feedback

6. **Results Viewer**
   - Tree-based display of analysis data
   - Separate tabs for current scan, library, and GitHub library
   - File, class, and function statistics
   - Export individual scan results

## Running Tests

Tests are written with `pytest` and cover the core analysis logic. Execute:

```bash
pytest
```

## Contributing & License

Contributions are welcome via pull requests. This project is released under the [MIT License](LICENSE).

