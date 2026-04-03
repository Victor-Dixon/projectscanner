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
    parser.add_argument("--export-context", action="store_true", help="Export ChatGPT context after scan")
    parser.add_argument("--split-by", choices=["directory", "language", "none"], default="directory", help="How to split context output")
    parser.add_argument("--max-files-per-chunk", type=int, default=100, help="Max files per chunk when split-by=none")
    parser.add_argument("--generate-init", action="store_true", help="Auto-generate __init__.py files after scan")
    parser.add_argument("--quick-scan", type=str, help="Fast drop-in scan (writes project_analysis.json in target dir)")
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
            from core.projectscanner import ProjectScanner
            target = Path(args.scan).resolve()
            scanner = ProjectScanner(project_root=target)
            scanner.scan_project()
            if args.generate_init:
                scanner.generate_init_files()
            if args.export_context:
                scanner.export_chatgpt_context()
            print(f"\n✅ Scan complete. Results saved to: {scanner.output_dir}")
        except Exception as e:
            print(f"Error running scan: {e}")
    elif args.quick_scan:
        try:
            from core.projectscanner import ProjectScanner
            target = Path(args.quick_scan).resolve()
            scanner = ProjectScanner(project_root=target)
            scanner.scan_project()
        except Exception as e:
            print(f"Error running quick scan: {e}")
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
