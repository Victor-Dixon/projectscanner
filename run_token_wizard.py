#!/usr/bin/env python3
"""
GitHub Token Wizard Launcher
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from wizards.github_token_wizard import main

if __name__ == "__main__":
    main() 