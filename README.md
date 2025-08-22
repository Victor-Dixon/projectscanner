# Project Scanner

[![Status](https://img.shields.io/badge/status-active-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

> Rapid codebase insight through automated structural analysis.

Project Scanner is an experimental tool for scanning and analyzing local
codebases. It can generate simple summaries of files, functions and classes and
optionally export context that can be used with large language models. The
application is under active development and many advanced ideas discussed in
earlier versions of the documentation—such as revenue analysis, strategic
planning, or automated deployments—are not implemented.

## Key Features

- Scan a project directory and collect basic structural information.
- Export optional context files for use with large language models.
- Experimental GUI for launching scans.
- Lightweight "quick scan" command that writes a JSON summary.

## Quick Start

### GUI Mode

```bash
python main.py --gui
```

### Command Line

```bash
# Quick scan a single project
python main.py --quick-scan /path/to/project

# Unified scanner with optional context export
python main.py --scan /path/to/project --export-context --split-by directory
```

## Project Structure

```
project-scanner/
├── src/                           # Core source code
├── scripts/                       # Entry point scripts
├── docs/                          # Documentation
├── tests/                         # Test files
├── config/                        # Configuration files
└── requirements.txt               # Python dependencies
```

## Development Notes

- Package initialization handles missing optional modules to allow the tool to
  run in minimal environments.

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/project-scanner.git
   cd project-scanner
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application**

   ```bash
   python main.py --gui
   ```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file
for details.

## Acknowledgments

- Built with Python and modern web technologies
- Integrates with the GitHub API for repository analysis

## Support

For support and questions:

- Create an issue in the GitHub repository
- Check the documentation in the `docs/` folder

---

**Project Scanner is in an early stage. Expect rough edges and incomplete
features.**

