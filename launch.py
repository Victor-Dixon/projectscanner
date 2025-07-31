#!/usr/bin/env python3
"""
Project Scanner - Launcher Script

A simple launcher for all Project Scanner tools.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Project Scanner Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py gui                    # Launch GUI
  python launch.py scan /path/to/project  # Scan a project
  python launch.py github username        # Scan GitHub library
  python launch.py skill-tree             # Generate skill tree
  python launch.py organize               # Organize project structure
  python launch.py token-wizard           # Setup GitHub token
        """
    )
    
    parser.add_argument(
        'command',
        choices=['gui', 'scan', 'github', 'skill-tree', 'organize', 'token-wizard', 'help'],
        help='Command to run'
    )
    
    parser.add_argument(
        'args',
        nargs='*',
        help='Additional arguments for the command'
    )
    
    # Parse known args to allow additional arguments to pass through
    args, unknown = parser.parse_known_args()
    
    # Store unknown args for passing to subcommands
    sys.unknown_args = unknown
    
    if args.command == 'gui':
        launch_gui()
    elif args.command == 'scan':
        if not args.args:
            print("Error: Please provide a project path")
            print("Usage: python launch.py scan /path/to/project")
            sys.exit(1)
        launch_scanner(args.args[0])
    elif args.command == 'github':
        if not args.args:
            print("Error: Please provide a GitHub username")
            print("Usage: python launch.py github username")
            sys.exit(1)
        launch_github_analysis(args.args[0])
    elif args.command == 'skill-tree':
        launch_skill_tree()
    elif args.command == 'organize':
        launch_organize()
    elif args.command == 'token-wizard':
        launch_token_wizard()
    elif args.command == 'help':
        show_help()

def launch_gui():
    """Launch the GUI."""
    print("Launching Project Scanner GUI...")
    try:
        subprocess.run([sys.executable, "run_gui.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching GUI: {e}")
        sys.exit(1)

def launch_scanner(project_path):
    """Launch the scanner."""
    print(f"Scanning project: {project_path}")
    try:
        # Pass all additional arguments to the scanner
        cmd = [sys.executable, "run_scanner.py", project_path]
        # Add any unknown arguments
        if hasattr(sys, 'unknown_args'):
            cmd.extend(sys.unknown_args)
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error scanning project: {e}")
        sys.exit(1)

def launch_github_analysis(username):
    """Launch GitHub analysis."""
    print(f"Analyzing GitHub libraries for user: {username}")
    try:
        # Call the github scanner directly with the username
        subprocess.run([sys.executable, "src/scanners/github_library_scanner.py", username], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error analyzing GitHub: {e}")
        sys.exit(1)

def launch_skill_tree():
    """Launch skill tree generation."""
    print("Generating skill tree...")
    try:
        subprocess.run([sys.executable, "run_analysis.py", "--skill-tree"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating skill tree: {e}")
        sys.exit(1)

def launch_organize():
    """Launch project organization."""
    print("Organizing project structure...")
    try:
        subprocess.run([sys.executable, "organize_project.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error organizing project: {e}")
        sys.exit(1)

def launch_token_wizard():
    """Launch the GitHub token wizard."""
    print("Launching GitHub Token Wizard...")
    try:
        subprocess.run([sys.executable, "run_token_wizard.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching token wizard: {e}")
        sys.exit(1)

def show_help():
    """Show detailed help information."""
    help_text = """
Project Scanner - Advanced Code Analysis Tool
============================================

This tool provides comprehensive analysis of codebases, GitHub libraries,
and generates skill trees for technical knowledge visualization.

Available Commands:
------------------

GUI Mode:
  python launch.py gui
  Launches the graphical user interface for easy project analysis.

Project Scanning:
  python launch.py scan /path/to/project
  Scans a local project directory and generates analysis reports.

GitHub Analysis:
  python launch.py github username
  Analyzes all repositories from a GitHub user.

Skill Tree Generation:
  python launch.py skill-tree
  Generates a visual skill tree from analyzed projects.

Project Organization:
  python launch.py organize
  Organizes the project structure for better maintainability.

GitHub Token Setup:
  python launch.py token-wizard
  Launches the GitHub token setup wizard for private repository access.

Quick Start:
-----------
1. Launch GUI: python launch.py gui
2. Configure your scanning options
3. Click "START PROCESSING" to begin analysis
4. View results in the tabs

Features:
---------
• Deep code analysis with ChatGPT context generation
• GitHub library scanning (public and private repos)
• Visual skill tree generation
• Modern GUI interface
• Command-line tools for automation
• Comprehensive reporting

For more information, see README.md
"""
    print(help_text)

if __name__ == "__main__":
    main() 