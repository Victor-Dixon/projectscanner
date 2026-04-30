"""
MODULE: main
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""
Project Scanner - Main Entry Point

A comprehensive tool for analyzing and understanding codebases.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.projectscanner.gui import main

if __name__ == "__main__":
    main()
