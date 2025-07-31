#!/usr/bin/env python3
"""
Main entry point for ProjectScanner application.
"""

import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from projectscanner.gui import main as gui_main
from projectscanner.cli import main as cli_main


def main():
    """Main entry point that decides whether to run CLI or GUI."""
    parser = argparse.ArgumentParser(
        description="ProjectScanner - Code analysis tool with GUI and CLI interfaces"
    )
    parser.add_argument(
        "--gui", 
        action="store_true", 
        help="Launch the graphical user interface"
    )
    parser.add_argument(
        "--cli", 
        action="store_true", 
        help="Run in command-line interface mode"
    )
    
    # Parse only the first argument to avoid conflicts with CLI arguments
    if len(sys.argv) > 1 and sys.argv[1] in ['--gui', '--cli']:
        args, remaining = parser.parse_known_args()
    else:
        args = parser.parse_args([])
        remaining = sys.argv[1:]
    
    if args.gui or (not args.cli and len(sys.argv) == 1):
        # Run GUI mode (default if no arguments)
        print("Starting ProjectScanner GUI...")
        gui_main()
    else:
        # Run CLI mode
        print("Starting ProjectScanner CLI...")
        # Pass remaining arguments to CLI
        sys.argv = [sys.argv[0]] + remaining
        cli_main()


if __name__ == "__main__":
    main() 