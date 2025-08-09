#!/usr/bin/env python3
"""
Project Scanner - Scanner Entry Point

Entry point for scanning and analysis operations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Scanner entry point."""
    try:
        from core.scanner.enhanced_project_scanner import EnhancedProjectScanner
        # For now, just print that the scanner is available
        print("Enhanced Project Scanner is available!")
        print("Use: python main.py --scan /path/to/project")
    except ImportError as e:
        print(f"Scanner module not found: {e}")
        print("Please check installation.")

if __name__ == "__main__":
    main()
