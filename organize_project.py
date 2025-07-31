#!/usr/bin/env python3
"""
Project Scanner - Project Organization Script

This script organizes and cleans up the project structure for better maintainability.
"""

import os
import shutil
import json
import glob
from pathlib import Path
from typing import Dict, List, Set
import argparse

class ProjectOrganizer:
    """Organizes the project structure for better maintainability."""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.organized_files = []
        self.cleaned_files = []
        self.errors = []
        
        # Define organization structure
        self.structure = {
            'src': {
                'core': ['projectscanner/'],
                'analyzers': [
                    'comprehensive_project_analyzer.py',
                    'deep_project_insights.py',
                    'proper_insights_analyzer.py',
                    'fixed_insights_analyzer.py',
                    'enhanced_skill_analyzer.py',
                    'deep_github_analysis.py'
                ],
                'scanners': [
                    'github_library_scanner.py',
                    'github_library_scanner_private.py',
                    'analyze_github_library.py'
                ],
                'tools': [
                    'skill_tree_generator.py',
                    'skill_tree_viewer.py',
                    'data_inspector.py',
                    'debug_analysis_status.py',
                    'check_token_permissions.py'
                ],
                'wizards': [
                    'github_token_wizard.py',
                    'github_token_wizard_gui.py',
                    'demo_gui_wizard.py',
                    'demo_wizard.py'
                ],
                'gui': [
                    'demo_gui.py',
                    'run_gui.py'
                ]
            },
            'scripts': [
                'main.py',
                'run_gui.bat',
                'run_gui.sh',
                'setup_private_repos.bat',
                'setup_private_repos.sh',
                'setup_private_repos_gui.bat',
                'setup_private_repos_gui.sh',
                'view_skill_tree.bat',
                'view_skill_tree.sh'
            ],
            'data': {
                'analysis': [
                    'comprehensive_analysis/',
                    'deep_insights/',
                    'fixed_insights/',
                    'proper_insights/',
                    'skill_analysis/',
                    'thea_analysis/'
                ],
                'libraries': [
                    'github_library/',
                    'github_library_enhanced/',
                    'test_github_library/',
                    'test_library_management/'
                ],
                'reports': [
                    '*.json',
                    '*.md'
                ]
            },
            'docs': [
                '*.md',
                '*.txt'
            ],
            'tests': [
                'tests/',
                'test_*.py'
            ],
            'config': [
                'requirements.txt',
                '.gitignore',
                'LICENSE'
            ]
        }
        
        # Files to clean up (temporary or redundant)
        self.files_to_clean = [
            '__pycache__/',
            '*.pyc',
            '*.pyo',
            '*.log',
            'dependency_cache.json',
            'interview_summary.txt',
            'validation_report.md',
            'project_scanner.py'
        ]
        
        # Large files that should be moved to data/reports
        self.large_files = [
            'deep_github_insights_report.json',
            'thea_project_analysis.json',
            'thea_chatgpt_context.json',
            'project_analysis_projectscanner.json',
            'chatgpt_project_context_projectscanner.json'
        ]

    def organize_project(self, dry_run: bool = False) -> Dict:
        """Organize the project structure."""
        print("🔧 Starting project organization...")
        
        if dry_run:
            print("📋 DRY RUN MODE - No files will be moved")
        
        # Create directory structure
        self._create_directories(dry_run)
        
        # Move files to appropriate directories
        self._organize_files(dry_run)
        
        # Clean up unnecessary files
        self._cleanup_files(dry_run)
        
        # Create new main entry points
        self._create_entry_points(dry_run)
        
        # Update imports and references
        if not dry_run:
            self._update_references()
        
        return {
            'organized_files': self.organized_files,
            'cleaned_files': self.cleaned_files,
            'errors': self.errors
        }

    def _create_directories(self, dry_run: bool):
        """Create the new directory structure."""
        directories = [
            'src/core',
            'src/analyzers',
            'src/scanners',
            'src/tools',
            'src/wizards',
            'src/gui',
            'scripts',
            'data/analysis',
            'data/libraries',
            'data/reports',
            'docs',
            'tests',
            'config'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            if not dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")

    def _organize_files(self, dry_run: bool):
        """Move files to their appropriate directories."""
        for category, items in self.structure.items():
            if category == 'src':
                for subcategory, files in items.items():
                    self._move_files_to_category(files, f"src/{subcategory}", dry_run)
            else:
                self._move_files_to_category(items, category, dry_run)

    def _move_files_to_category(self, files: List[str], category: str, dry_run: bool):
        """Move files to a specific category directory."""
        target_dir = self.project_root / category
        
        for file_pattern in files:
            if file_pattern.endswith('/'):
                # Directory
                source_dir = self.project_root / file_pattern[:-1]
                if source_dir.exists():
                    # Skip if trying to move a directory into itself
                    if source_dir.name == category:
                        print(f"⚠️  Skipping {file_pattern} - would move into itself")
                        continue
                    
                    target_subdir = target_dir / source_dir.name
                    if not dry_run:
                        if target_subdir.exists():
                            shutil.rmtree(target_subdir)
                        shutil.move(str(source_dir), str(target_subdir))
                    self.organized_files.append(f"{file_pattern} -> {category}/")
                    print(f"📦 Moved directory: {file_pattern} -> {category}/")
            else:
                # File
                source_files = list(self.project_root.glob(file_pattern))
                for source_file in source_files:
                    if source_file.is_file():
                        target_file = target_dir / source_file.name
                        if not dry_run:
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(source_file), str(target_file))
                        self.organized_files.append(f"{source_file.name} -> {category}/")
                        print(f"📄 Moved file: {source_file.name} -> {category}/")

    def _cleanup_files(self, dry_run: bool):
        """Clean up unnecessary files."""
        for pattern in self.files_to_clean:
            files_to_remove = list(self.project_root.glob(pattern))
            for file_path in files_to_remove:
                if file_path.is_file():
                    if not dry_run:
                        file_path.unlink()
                    self.cleaned_files.append(str(file_path))
                    print(f"🗑️  Removed: {file_path}")
                elif file_path.is_dir():
                    if not dry_run:
                        shutil.rmtree(file_path)
                    self.cleaned_files.append(str(file_path))
                    print(f"🗑️  Removed directory: {file_path}")

    def _create_entry_points(self, dry_run: bool):
        """Create new main entry points."""
        entry_points = {
            'main.py': self._create_main_entry(),
            'run_scanner.py': self._create_scanner_entry(),
            'run_gui.py': self._create_gui_entry(),
            'run_analysis.py': self._create_analysis_entry()
        }
        
        for filename, content in entry_points.items():
            file_path = self.project_root / filename
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            print(f"📝 Created entry point: {filename}")

    def _create_main_entry(self) -> str:
        """Create the main entry point."""
        return '''#!/usr/bin/env python3
"""
Project Scanner - Main Entry Point

A comprehensive tool for analyzing and understanding codebases.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.gui import main

if __name__ == "__main__":
    main()
'''

    def _create_scanner_entry(self) -> str:
        """Create the scanner entry point."""
        return '''#!/usr/bin/env python3
"""
Project Scanner - Command Line Scanner

Run project analysis from command line.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.scanner import ProjectScanner

def main():
    parser = argparse.ArgumentParser(description="Project Scanner CLI")
    parser.add_argument("project_path", help="Path to project to scan")
    parser.add_argument("--output", "-o", help="Output directory", default=".")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    scanner = ProjectScanner(
        project_root=args.project_path,
        output_dir=args.output
    )
    
    def progress_callback(message):
        if args.verbose:
            print(message)
    
    scanner.scan_project(progress_callback=progress_callback)
    print("Scan completed successfully!")

if __name__ == "__main__":
    main()
'''

    def _create_gui_entry(self) -> str:
        """Create the GUI entry point."""
        return '''#!/usr/bin/env python3
"""
Project Scanner - GUI Entry Point

Launch the graphical user interface.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gui.main import main

if __name__ == "__main__":
    main()
'''

    def _create_analysis_entry(self) -> str:
        """Create the analysis entry point."""
        return '''#!/usr/bin/env python3
"""
Project Scanner - Analysis Entry Point

Run advanced analysis tools.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    parser = argparse.ArgumentParser(description="Project Scanner Analysis Tools")
    parser.add_argument("--skill-tree", action="store_true", help="Generate skill tree")
    parser.add_argument("--github-analysis", action="store_true", help="Run GitHub analysis")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive analysis")
    
    args = parser.parse_args()
    
    if args.skill_tree:
        from tools.skill_tree_generator import main as skill_tree_main
        skill_tree_main()
    elif args.github_analysis:
        from scanners.github_library_scanner import main as github_main
        github_main()
    elif args.comprehensive:
        from analyzers.comprehensive_project_analyzer import main as comprehensive_main
        comprehensive_main()
    else:
        print("Please specify an analysis type: --skill-tree, --github-analysis, or --comprehensive")

if __name__ == "__main__":
    main()
'''

    def _update_references(self):
        """Update import statements and file references."""
        # This would update import statements in moved files
        # For now, we'll just note that this needs to be done
        print("⚠️  Note: Import statements may need to be updated in moved files")

    def create_readme(self, dry_run: bool = False):
        """Create a comprehensive README file."""
        readme_content = '''# Project Scanner

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
projectscanner/
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
'''
        
        readme_path = self.project_root / "README.md"
        if not dry_run:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
        print("📝 Created comprehensive README.md")

    def create_requirements(self, dry_run: bool = False):
        """Create an updated requirements.txt file."""
        requirements_content = '''# Core dependencies
PyQt5>=5.15.0
requests>=2.25.0
gitpython>=3.1.0

# Analysis and processing
openai>=0.27.0
networkx>=2.5
matplotlib>=3.3.0
seaborn>=0.11.0

# Data handling
pandas>=1.3.0
numpy>=1.21.0

# Visualization
plotly>=5.0.0
graphviz>=0.17

# Development and testing
pytest>=6.0.0
black>=21.0.0
flake8>=3.8.0

# Documentation
sphinx>=4.0.0
sphinx-rtd-theme>=0.5.0
'''
        
        requirements_path = self.project_root / "requirements.txt"
        if not dry_run:
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(requirements_content)
        print("📝 Updated requirements.txt")

def main():
    """Main function for project organization."""
    parser = argparse.ArgumentParser(description="Organize Project Scanner project structure")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    organizer = ProjectOrganizer(args.project_root)
    
    print("🔧 Project Scanner Organization Tool")
    print("=" * 50)
    
    # Organize the project
    result = organizer.organize_project(dry_run=args.dry_run)
    
    # Create documentation
    organizer.create_readme(dry_run=args.dry_run)
    organizer.create_requirements(dry_run=args.dry_run)
    
    # Print summary
    print("\n📊 Organization Summary")
    print("=" * 30)
    print(f"📦 Files organized: {len(result['organized_files'])}")
    print(f"🗑️  Files cleaned: {len(result['cleaned_files'])}")
    print(f"❌ Errors: {len(result['errors'])}")
    
    if result['errors']:
        print("\n❌ Errors encountered:")
        for error in result['errors']:
            print(f"  - {error}")
    
    if args.dry_run:
        print("\n⚠️  This was a dry run. No files were actually moved.")
        print("Run without --dry-run to actually organize the project.")
    else:
        print("\n✅ Project organization completed successfully!")
        print("📝 Note: You may need to update import statements in moved files.")

if __name__ == "__main__":
    main() 