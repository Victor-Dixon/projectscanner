#!/usr/bin/env python3
"""
Project Scanner - GUI Main Module

Main entry point for the GUI application.
"""

import sys
from pathlib import Path

# Add the core module to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from core.projectscanner.gui import main

if __name__ == "__main__":
    main() 