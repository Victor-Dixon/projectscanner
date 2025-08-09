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
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in token wizard launcher: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 