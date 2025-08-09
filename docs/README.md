# Project Scanner

A comprehensive tool for analyzing and understanding codebases, with support for GitHub library scanning, skill tree generation, and advanced project insights.

## Features

- **Project Analysis**: Deep analysis of codebases with ChatGPT context generation
- **GitHub Library Scanning**: Scan and analyze entire GitHub user repositories
- **Skill Tree Generation**: Visual representation of technical skills and knowledge
- **GUI Interface**: User-friendly graphical interface for all tools
- **Command Line Tools**: Powerful CLI for automation and scripting

## Quick Start

### GUI Mode
```bash
python run_gui.py
```

### Command Line Scanner
```bash
python run_scanner.py /path/to/project
```

### GitHub Analysis
```bash
python run_analysis.py --github-analysis
```

### Skill Tree Generation
```bash
python run_analysis.py --skill-tree
```

## Project Structure

```
project-scanner/
├── src/                    # Source code
│   ├── core/              # Core scanner functionality
│   ├── analyzers/         # Analysis tools
│   ├── scanners/          # GitHub and library scanners
│   ├── tools/             # Utility tools
│   ├── wizards/           # Setup wizards
│   └── gui/               # GUI components
├── scripts/               # Entry point scripts
├── data/                  # Analysis data and reports
├── docs/                  # Documentation
├── tests/                 # Test files
└── config/                # Configuration files
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the GUI: `python run_gui.py`

## Usage

### GUI Mode
1. Launch the GUI: `python run_gui.py`
2. Configure your scanning options
3. Click "START PROCESSING" to begin analysis
4. View results in the tabs

### Command Line
- Scan a project: `python run_scanner.py /path/to/project`
- Generate skill tree: `python run_analysis.py --skill-tree`
- Analyze GitHub: `python run_analysis.py --github-analysis`

## Configuration

### GitHub Token Setup
1. Run: `python setup_private_repos.bat` (Windows) or `./setup_private_repos.sh` (Linux/Mac)
2. Follow the wizard to configure your GitHub token
3. Set appropriate permissions for repository access

## Features

### Project Analysis
- File structure analysis
- Code complexity metrics
- Technology stack detection
- ChatGPT context generation

### GitHub Library Scanning
- Scan entire GitHub user repositories
- Public and private repository support
- Repository metadata analysis
- Library summary generation

### Skill Tree Generation
- Visual skill representation
- Technology categorization
- Knowledge base analysis
- Export capabilities

### GUI Features
- Modern, responsive interface
- Real-time progress tracking
- Multiple analysis views
- Export and import capabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
