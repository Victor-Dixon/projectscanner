"""
MODULE: loc_checker
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""
Lines of Code (LOC) Checker for Agent Policy Enforcement
Enforces maximum line count limits for different file types.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class LOCChecker:
    """Enforces LOC limits for agent-generated code."""
    
    # Concept: TODO - Explain the core idea behind __init__
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def __init__(self, max_loc: int = 350, gui_max_loc: int = 500):
        self.max_loc = max_loc
        self.gui_max_loc = gui_max_loc
        self.violations = []
        
    # Concept: TODO - Explain the core idea behind count_lines
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def count_lines(self, file_path: Path) -> int:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """Count non-empty lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Count non-empty lines (excluding comments and whitespace)
                non_empty_lines = sum(1 for line in lines 
                                   if line.strip() and not line.strip().startswith('#'))
                return non_empty_lines
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return 0
    
    # Concept: TODO - Explain the core idea behind is_gui_file
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def is_gui_file(self, file_path: Path) -> bool:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """Determine if file is a GUI component."""
        gui_indicators = [
            'gui', 'ui', 'view', 'window', 'dialog', 'form',
            'frontend', 'interface', 'widget', 'component'
        ]
        
        file_name = file_path.name.lower()
        file_content = file_path.read_text(encoding='utf-8').lower()
        
        # Check filename
        for indicator in gui_indicators:
            if indicator in file_name:
                return True
        
        # Check content for GUI frameworks
        gui_frameworks = [
            'tkinter', 'pyqt', 'pyside', 'wx', 'kivy', 'dearpygui',
            'flask', 'django', 'fastapi', 'streamlit', 'gradio'
        ]
        
        for framework in gui_frameworks:
            if framework in file_content:
                return True
        
        return False
    
    # Concept: TODO - Explain the core idea behind check_file
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def check_file(self, file_path: Path) -> Tuple[bool, int, int]:
        """Check if file meets LOC requirements."""
    # Concept: TODO - Purpose of is_gui_file
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        if not file_path.exists():
            return False, 0, 0
        
        loc_count = self.count_lines(file_path)
        is_gui = self.is_gui_file(file_path)
        max_allowed = self.gui_max_loc if is_gui else self.max_loc
        
        return loc_count <= max_allowed, loc_count, max_allowed
    
    # Concept: TODO - Explain the core idea behind check_directory
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def check_directory(self, directory: Path) -> List[Dict]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """Check all Python files in directory."""
        violations = []
        
        for file_path in directory.rglob("*.py"):
            # Skip test files and virtual environments
            if any(part in str(file_path) for part in ['test', 'tests', '__pycache__', 'venv', '.venv']):
                continue
            
            is_compliant, loc_count, max_allowed = self.check_file(file_path)
            
            if not is_compliant:
                violations.append({
                    'file': str(file_path),
                    'loc': loc_count,
                    'max_allowed': max_allowed,
                    'is_gui': self.is_gui_file(file_path)
                })
        
        return violations
    
    # Concept: TODO - Explain the core idea behind run
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 44 lines > 30 limit)
    def execute_scan(self, paths: List[str]) -> int:
        """Run LOC check on specified paths."""
    # Concept: TODO - Purpose of check_directory
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        all_violations = []
        
        for path_str in paths:
            path = Path(path_str)
            if path.is_file():
                is_compliant, loc_count, max_allowed = self.check_file(path)
                if not is_compliant:
                    all_violations.append({
                        'file': str(path),
                        'loc': loc_count,
                        'max_allowed': max_allowed,
                        'is_gui': self.is_gui_file(path)
                    })
            elif path.is_dir():
                all_violations.extend(self.check_directory(path))
        
        # Report violations
        if all_violations:
            print("❌ LOC VIOLATIONS DETECTED:")
            print("=" * 60)
            
            for violation in all_violations:
                file_type = "GUI" if violation['is_gui'] else "Core"
                print(f"📁 {violation['file']}")
                print(f"   Type: {file_type}")
                print(f"   Lines: {violation['loc']} (max: {violation['max_allowed']})")
                print(f"   Excess: {violation['loc'] - violation['max_allowed']} lines")
                print()
            
            print("🔧 RECOMMENDATIONS:")
            print("- Break large files into smaller modules")
            print("- Extract utility functions to separate files")
            print("- Use composition to reduce class complexity")
            print("- Consider using design patterns for large components")
            
            return 1
        
        print("✅ All files meet LOC requirements!")
        return 0


# Concept: TODO - Explain the core idea behind main
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def main():
    """Main entry point for LOC checker."""
    # Concept: TODO - Purpose of execute_scan
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
    parser = argparse.ArgumentParser(description="Check Lines of Code limits")
    parser.add_argument("paths", nargs="+", help="Files or directories to check")
    parser.add_argument("--max-loc", type=int, default=350, 
                       help="Maximum LOC for core modules")
    parser.add_argument("--gui-max-loc", type=int, default=500,
                       help="Maximum LOC for GUI modules")
    
    args = parser.parse_args()
    
    checker = LOCChecker(max_loc=args.max_loc, gui_max_loc=args.gui_max_loc)
    exit_code = checker.run(args.paths)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 
# Concept: TODO - Purpose of main
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach