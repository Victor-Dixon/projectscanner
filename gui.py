#!/usr/bin/env python3
"""
Project Scanner - GUI Entry Point

Entry point for GUI operations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """GUI entry point."""
    try:
        from gui.main.enhanced_gui import launch_gui
        launch_gui()
    except ImportError as e:
        print(f"GUI module not found: {e}")
        print("Please check installation.")

if __name__ == "__main__":
    main()
