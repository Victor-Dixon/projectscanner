"""
MODULE: deploy_agent_policy
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""
Agent Policy Deployment Script
Propagates the agent policy framework across all repositories.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class AgentPolicyDeployer:
    """Deploys agent policy framework across repositories."""
    
    # Concept: TODO - Explain the core idea behind __init__
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def __init__(self, github_library_path: str):
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        self.github_library_path = Path(github_library_path)
        self.template_files = [
            "AGENTS.md",
            ".pre-commit-config.yaml",
            ".github/workflows/agent-enforcer.yml"
        ]
        self.script_files = [
            "scripts/loc_checker.py",
            "scripts/complexity_checker.py", 
            "scripts/oop_checker.py",
            "scripts/agents_md_checker.py"
        ]
        self.stats = {
            'total_repos': 0,
            'updated_repos': 0,
            'failed_repos': 0,
            'skipped_repos': 0
        }
    
    # Concept: TODO - Explain the core idea behind get_repository_list
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def get_repository_list(self) -> List[Path]:
    # Concept: TODO - Purpose of get_repository_list
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation details
        """Get list of all repositories from github_library."""
        repos = []
        
        if not self.github_library_path.exists():
            print(f"❌ GitHub library path not found: {self.github_library_path}")
            return repos
        
        # Get all directories in github_library
        for item in self.github_library_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                repos.append(item)
        
        return repos
    
    # Concept: TODO - Explain the core idea behind copy_template_files
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 43 lines > 30 limit)
    def copy_template_files(self, repo_path: Path) -> bool:
        """Copy template files to repository."""
    # Concept: TODO - get_repository_list
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation
    # Concept: TODO - Purpose of get_repository_list
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        try:
            # Create scripts directory if it doesn't exist
            scripts_dir = repo_path / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            
            # Copy template files
            for template_file in self.template_files:
                src = Path(template_file)
                dst = repo_path / template_file
                
                if src.exists():
                    # Create parent directories if needed
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    print(f"   ✅ Copied {template_file}")
                else:
                    print(f"   ❌ Template file not found: {template_file}")
                    return False
            
            # Copy script files
            for script_file in self.script_files:
                src = Path(script_file)
                dst = repo_path / script_file
                
                if src.exists():
                    # Create parent directories if needed
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    print(f"   ✅ Copied {script_file}")
                else:
                    print(f"   ❌ Script file not found: {script_file}")
                    return False
            
            return True
        
        except Exception as e:
            print(f"   ❌ Error copying files: {e}")
            return False
    
    # Concept: TODO - Explain the core idea behind install_pre_commit_hooks
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 36 lines > 30 limit)
    def install_pre_commit_hooks(self, repo_path: Path) -> bool:
        """Install pre-commit hooks in repository."""
    # Concept: TODO - Purpose of copy_template_files
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        try:
            # Check if pre-commit is installed
            result = subprocess.run(
                ["pre-commit", "--version"],
                capture_output=True,
                text=True,
                cwd=repo_path
            )
            
            if result.returncode != 0:
                print(f"   ⚠️  pre-commit not installed, skipping hook installation")
                return True  # Not a failure, just skip
            
            # Install hooks
            result = subprocess.run(
                ["pre-commit", "install"],
                capture_output=True,
                text=True,
                cwd=repo_path
            )
            
            if result.returncode == 0:
                print(f"   ✅ Installed pre-commit hooks")
                return True
            else:
                print(f"   ❌ Failed to install pre-commit hooks: {result.stderr}")
                return False
        
        except Exception as e:
            print(f"   ❌ Error installing pre-commit hooks: {e}")
            return False
    
    # Concept: TODO - Explain the core idea behind create_requirements_txt
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 48 lines > 30 limit)
    def create_requirements_txt(self, repo_path: Path) -> bool:
        """Create or update requirements.txt with necessary dependencies."""
    # Concept: TODO - Purpose of install_pre_commit_hooks
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        try:
            requirements_file = repo_path / "requirements.txt"
            
            # Define required packages for agent policy
            required_packages = [
                "pre-commit>=3.0.0",
                "black>=23.0.0",
                "ruff>=0.0.270",
                "bandit>=1.7.5",
                "mypy>=1.4.0",
                "radon>=5.1.0",  # For complexity analysis
                "wily>=1.21.0"    # For code metrics
            ]
            
            # Read existing requirements if they exist
            existing_packages = []
            if requirements_file.exists():
                with open(requirements_file, 'r') as f:
                    existing_packages = [line.strip() for line in f if line.strip()]
            
            # Add new packages if not already present
            new_packages = []
            for package in required_packages:
                if not any(package.split('>=')[0] in existing for existing in existing_packages):
                    new_packages.append(package)
            
            # Write updated requirements
            with open(requirements_file, 'a') as f:
                if new_packages:
                    f.write("\n# Agent Policy Enforcement Dependencies\n")
                    for package in new_packages:
                        f.write(f"{package}\n")
            
            if new_packages:
                print(f"   ✅ Updated requirements.txt with {len(new_packages)} new packages")
            else:
                print(f"   ✅ requirements.txt already up to date")
            
            return True
        
        except Exception as e:
            print(f"   ❌ Error updating requirements.txt: {e}")
            return False
    
    # Concept: TODO - Explain the core idea behind update_readme
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 61 lines > 30 limit)
    def update_readme(self, repo_path: Path) -> bool:
        """Update README.md with agent policy information."""
    # Concept: TODO - Purpose of create_requirements_txt
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        try:
            readme_file = repo_path / "README.md"
            
            # Create or update README
            readme_content = f"""# {repo_path.name}

## Agent Policy Compliance

This repository follows the **Agent Policy & Enforcement Framework** to ensure high-quality, maintainable code.

### Standards
- **OOP**: All code must be class-based
- **SRP**: Single Responsibility Principle enforced
- **LOC Limits**: Core <= 350, GUI <= 500 lines
- **Complexity**: Functions <= 10, Classes <= 15 complexity

### Quality Tools
- **Pre-commit hooks**: Automatic code quality checks
- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **Bandit**: Security vulnerability scanning
- **Custom checks**: LOC, complexity, OOP structure

### Documentation
- See `AGENTS.md` for detailed policy guidelines
- Check `.pre-commit-config.yaml` for enforcement rules

### Getting Started
```bash
# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run checks manually
pre-commit run --all-files
```

---
*This repository is part of the Agent Policy Enforcement Framework.*
"""
    # Concept: TODO - Purpose of update_readme
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
            
            # Write README
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            
            print(f"   ✅ Updated README.md")
            return True
        
        except Exception as e:
            print(f"   ❌ Error updating README.md: {e}")
            return False
    
    # Concept: TODO - Explain the core idea behind deploy_to_repository
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def deploy_to_repository(self, repo_path: Path) -> bool:
    # Concept: TODO - Purpose of deploy_to_repository
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation details
        """Deploy agent policy framework to a single repository."""
        print(f"📁 Processing: {repo_path.name}")
        
        try:
            # Copy template files
            if not self.copy_template_files(repo_path):
                return False
            
            # Install pre-commit hooks
            if not self.install_pre_commit_hooks(repo_path):
                return False
            
            # Update requirements.txt
            if not self.create_requirements_txt(repo_path):
                return False
            
            # Update README.md
            if not self.update_readme(repo_path):
                return False
            
            print(f"   ✅ Successfully deployed to {repo_path.name}")
            return True
        
        except Exception as e:
            print(f"   ❌ Error deploying to {repo_path.name}: {e}")
            return False
    
    # Concept: TODO - Explain the core idea behind run
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 42 lines > 30 limit)
    def execute_deployment(self, dry_run: bool = False) -> int:
        """Deploy agent policy framework to all repositories."""
    # Concept: TODO - deploy_to_repository
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation
    # Concept: TODO - Purpose of deploy_to_repository
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        repos = self.get_repository_list()
        
        if not repos:
            print("❌ No repositories found to process")
            return 1
        
        print(f"🚀 Starting deployment to {len(repos)} repositories")
        print("=" * 60)
        
        for repo_path in repos:
            self.stats['total_repos'] += 1
            
            if dry_run:
                print(f"📁 [DRY RUN] Would process: {repo_path.name}")
                self.stats['skipped_repos'] += 1
                continue
            
            if self.deploy_to_repository(repo_path):
                self.stats['updated_repos'] += 1
            else:
                self.stats['failed_repos'] += 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT SUMMARY")
        print("=" * 60)
        print(f"Total repositories: {self.stats['total_repos']}")
        print(f"Successfully updated: {self.stats['updated_repos']}")
        print(f"Failed: {self.stats['failed_repos']}")
        print(f"Skipped (dry run): {self.stats['skipped_repos']}")
        
        if self.stats['failed_repos'] > 0:
            print(f"\n❌ {self.stats['failed_repos']} repositories failed deployment")
            return 1
        
        print(f"\n✅ Successfully deployed to {self.stats['updated_repos']} repositories!")
        return 0


# Concept: TODO - Explain the core idea behind main
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def main():
    """Main entry point for agent policy deployment."""
    # Concept: TODO - Purpose of execute_deployment
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
    parser = argparse.ArgumentParser(description="Deploy agent policy framework")
    parser.add_argument("--github-library", default="github_library",
                       help="Path to GitHub library directory")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    deployer = AgentPolicyDeployer(args.github_library)
    exit_code = deployer.run(dry_run=args.dry_run)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 
# Concept: TODO - Purpose of main
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach