#!/usr/bin/env python3
"""
Project Scanner - Main Entry Point

This is the main entry point for the Project Scanner application.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Project Scanner - Portfolio Analysis Tool")
    parser.add_argument("--gui", action="store_true", help="Launch GUI mode")
    parser.add_argument("--scan", type=str, help="Scan specific project path")
    parser.add_argument("--analyze", action="store_true", help="Run portfolio analysis")
    parser.add_argument("--strategic", action="store_true", help="Generate strategic plan")
    
    args = parser.parse_args()
    
    if args.gui:
        try:
            from src.gui.main.enhanced_gui import launch_gui
            launch_gui()
        except ImportError:
            print("GUI module not found. Please check installation.")
    elif args.scan:
        try:
            from src.core.scanner.enhanced_project_scanner import EnhancedProjectScanner
            scanner = EnhancedProjectScanner()
            scanner.scan_project(args.scan)
        except ImportError:
            print("Scanner module not found. Please check installation.")
    elif args.analyze:
        try:
            from src.core.analysis.analyze_portfolio import analyze_portfolio
            analyze_portfolio()
        except ImportError:
            print("Analysis module not found. Please check installation.")
    elif args.strategic:
        try:
            from src.strategic.strategic_plan import generate_strategic_plan
            generate_strategic_plan()
        except ImportError:
            print("Strategic module not found. Please check installation.")
    else:
        # Default to GUI
        try:
            from src.gui.main.enhanced_gui import launch_gui
            launch_gui()
        except ImportError:
            print("GUI module not found. Please check installation.")

if __name__ == "__main__":
    main()
