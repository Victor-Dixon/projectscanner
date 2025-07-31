#!/usr/bin/env python3
"""
Project Scanner - GUI Entry Point

Launch the graphical user interface.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.projectscanner.gui import main

if __name__ == "__main__":
    main()
