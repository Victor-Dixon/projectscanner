#!/usr/bin/env python3
"""
GitHub Repository Agent Policy Deployment Script
Clones actual GitHub repositories, applies agent policy framework, and pushes changes.
"""

import argparse
import json
import shutil
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple


class GitHubRepoDeployer:
    """Deploys agent policy framework to actual GitHub repositories."""
    
    def __init__(self, github_username: str, github_token: str = None):
        self.github_username = github_username
        self.github_token = github_token
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
        self.temp_dir = Path("temp_github_deploy")
    
    def get_github_repos(self) -> List[str]:
        """Get list of repositories from GitHub API."""
        repos = []
        
        # GitHub API endpoint for user repos
        api_url = f"https://api.github.com/users/{self.github_username}/repos"
        
        try:
            # Use curl to get repos (works without authentication for public repos)
            result = subprocess.run(
                ["curl", "-s", api_url],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for repo in data:
                    if not repo.get('fork', False):  # Skip forked repos
                        repos.append(repo['name'])
            
            print(f"Found {len(repos)} repositories for {self.github_username}")
            return repos
            
        except Exception as e:
            print(f"❌ Error fetching repositories: {e}")
            return []
    
    def clone_repository(self, repo_name: str) -> Path:
        """Clone a repository to temp directory."""
        repo_path = self.temp_dir / repo_name
        
        # Remove existing clone if it exists
        if repo_path.exists():
            shutil.rmtree(repo_path)
        
        # Clone repository
        clone_url = f"https://github.com/{self.github_username}/{repo_name}.git"
        
        try:
            result = subprocess.run(
                ["git", "clone", clone_url, str(repo_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"   ✅ Cloned {repo_name}")
                return repo_path
            else:
                print(f"   ❌ Failed to clone {repo_name}: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error cloning {repo_name}: {e}")
            return None
    
    def copy_template_files(self, repo_path: Path) -> bool:
        """Copy template files to repository."""
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
    
    def install_pre_commit_hooks(self, repo_path: Path) -> bool:
        """Install pre-commit hooks in repository."""
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
    
    def create_requirements_txt(self, repo_path: Path) -> bool:
        """Create or update requirements.txt with necessary dependencies."""
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
    
    def update_readme(self, repo_path: Path) -> bool:
        """Update README.md with agent policy information."""
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
            
            # Write README
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            
            print(f"   ✅ Updated README.md")
            return True
        
        except Exception as e:
            print(f"   ❌ Error updating README.md: {e}")
            return False
    
    def commit_and_push(self, repo_path: Path, repo_name: str) -> bool:
        """Commit changes and push to GitHub."""
        try:
            # Add all files
            result = subprocess.run(
                ["git", "add", "."],
                capture_output=True,
                text=True,
                cwd=repo_path
            )
            
            if result.returncode != 0:
                print(f"   ❌ Failed to add files: {result.stderr}")
                return False
            
            # Commit changes
            result = subprocess.run(
                ["git", "commit", "-m", "Add Agent Policy & Enforcement Framework"],
                capture_output=True,
                text=True,
                cwd=repo_path
            )
            
            if result.returncode != 0:
                print(f"   ❌ Failed to commit: {result.stderr}")
                return False
            
            # Push to GitHub
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True,
                cwd=repo_path
            )
            
            if result.returncode == 0:
                print(f"   ✅ Pushed changes to GitHub")
                return True
            else:
                # Try master branch if main doesn't exist
                result = subprocess.run(
                    ["git", "push", "origin", "master"],
                    capture_output=True,
                    text=True,
                    cwd=repo_path
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Pushed changes to GitHub (master branch)")
                    return True
                else:
                    print(f"   ❌ Failed to push: {result.stderr}")
                    return False
        
        except Exception as e:
            print(f"   ❌ Error committing/pushing: {e}")
            return False
    
    def deploy_to_repository(self, repo_name: str) -> bool:
        """Deploy agent policy framework to a single repository."""
        print(f"📁 Processing: {repo_name}")
        
        try:
            # Clone repository
            repo_path = self.clone_repository(repo_name)
            if not repo_path:
                return False
            
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
            
            # Commit and push changes
            if not self.commit_and_push(repo_path, repo_name):
                return False
            
            print(f"   ✅ Successfully deployed to {repo_name}")
            return True
        
        except Exception as e:
            print(f"   ❌ Error deploying to {repo_name}: {e}")
            return False
    
    def run(self, dry_run: bool = False) -> int:
        """Deploy agent policy framework to all repositories."""
        # Create temp directory
        self.temp_dir.mkdir(exist_ok=True)
        
        # Get repositories
        repos = self.get_github_repos()
        
        if not repos:
            print("❌ No repositories found to process")
            return 1
        
        print(f"🚀 Starting deployment to {len(repos)} repositories")
        print("=" * 60)
        
        for repo_name in repos:
            self.stats['total_repos'] += 1
            
            if dry_run:
                print(f"📁 [DRY RUN] Would process: {repo_name}")
                self.stats['skipped_repos'] += 1
                continue
            
            if self.deploy_to_repository(repo_name):
                self.stats['updated_repos'] += 1
            else:
                self.stats['failed_repos'] += 1
        
        # Clean up temp directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
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


def main():
    """Main entry point for GitHub repository deployment."""
    parser = argparse.ArgumentParser(description="Deploy agent policy framework to GitHub repositories")
    parser.add_argument("--username", required=True,
                        help="GitHub username")
    parser.add_argument("--token", 
                        help="GitHub personal access token (optional)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    deployer = GitHubRepoDeployer(args.username, args.token)
    exit_code = deployer.run(dry_run=args.dry_run)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 