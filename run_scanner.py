#!/usr/bin/env python3
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
