#!/usr/bin/env python3
"""
AGENTS.md Checker for Agent Policy Enforcement
Ensures AGENTS.md file exists in repository.
"""

import argparse
import sys
from pathlib import Path


class AgentsMDChecker:
    """Checks for AGENTS.md file in repository."""
    
    def __init__(self):
        self.violations = []
    
    def check_repository(self, repo_path: Path) -> bool:
        """Check if AGENTS.md exists in repository."""
        agents_md_path = repo_path / "AGENTS.md"
        
        if not agents_md_path.exists():
            self.violations.append({
                'repository': str(repo_path),
                'message': "AGENTS.md file is missing"
            })
            return False
        
        # Check if file has content
        try:
            content = agents_md_path.read_text(encoding='utf-8')
            if len(content.strip()) < 100:  # Minimum content requirement
                self.violations.append({
                    'repository': str(repo_path),
                    'message': "AGENTS.md file is too short (minimum 100 characters)"
                })
                return False
        except Exception as e:
            self.violations.append({
                'repository': str(repo_path),
                'message': f"Error reading AGENTS.md: {e}"
            })
            return False
        
        return True
    
    def run(self, paths: list) -> int:
        """Run AGENTS.md check on specified paths."""
        all_violations = []
        
        for path_str in paths:
            path = Path(path_str)
            if path.is_dir():
                if not self.check_repository(path):
                    all_violations.extend(self.violations)
                    self.violations = []
        
        # Report violations
        if all_violations:
            print("❌ AGENTS.md VIOLATIONS DETECTED:")
            print("=" * 50)
            
            for violation in all_violations:
                print(f"📁 {violation['repository']}")
                print(f"   ❌ {violation['message']}")
                print()
            
            print("🔧 RECOMMENDATIONS:")
            print("- Copy AGENTS.md template to repository root")
            print("- Ensure file contains policy guidelines")
            print("- Update file with repository-specific rules")
            
            return 1
        
        print("✅ All repositories have AGENTS.md file!")
        return 0


def main():
    """Main entry point for AGENTS.md checker."""
    parser = argparse.ArgumentParser(description="Check for AGENTS.md files")
    parser.add_argument("paths", nargs="+", help="Directories to check")
    
    args = parser.parse_args()
    
    checker = AgentsMDChecker()
    exit_code = checker.run(args.paths)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 