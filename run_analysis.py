#!/usr/bin/env python3
"""
Project Scanner - Analysis Entry Point

Run advanced analysis tools.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    parser = argparse.ArgumentParser(description="Project Scanner Analysis Tools")
    parser.add_argument("--skill-tree", action="store_true", help="Generate skill tree")
    parser.add_argument("--github-analysis", action="store_true", help="Run GitHub analysis")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive analysis")
    
    args = parser.parse_args()
    
    if args.skill_tree:
        from tools.skill_tree_generator import main as skill_tree_main
        skill_tree_main()
    elif args.github_analysis:
        from scanners.github_library_scanner import main as github_main
        github_main()
    elif args.comprehensive:
        from analyzers.comprehensive_project_analyzer import main as comprehensive_main
        comprehensive_main()
    else:
        print("Please specify an analysis type: --skill-tree, --github-analysis, or --comprehensive")

if __name__ == "__main__":
    main()
