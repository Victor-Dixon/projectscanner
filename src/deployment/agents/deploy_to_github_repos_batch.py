#!/usr/bin/env python3
"""
GitHub Repository Agent Policy Deployment Script (Batch Version)
Clones actual GitHub repositories, applies agent policy framework, and pushes changes.
Processes repositories in batches with better error handling.
"""

import argparse
import json
import shutil
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple


class GitHubRepoBatchDeployer:
    """Deploys agent policy framework to actual GitHub repositories in batches."""
    
    def __init__(self, github_username: str, github_token: str = None, batch_size: int = 5):
        self.github_username = github_username
        self.github_token = github_token
        self.batch_size = batch_size
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
            'skipped_repos': 0,
            'processed_repos': []
        }
        self.temp_dir = Path("temp_github_deploy")
    
    def load_token_from_config(self) -> str:
        """Load GitHub token from projectscanner config."""
        try:
            config_file = Path("config/github_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    token = config.get('token')
                    if token:
                        print(f"✅ Loaded GitHub token from projectscanner config")
                        return token
        except Exception as e:
            print(f"⚠️  Could not load token from config: {e}")
        return None
    
    def get_github_repos(self) -> List[str]:
        """Get list of repositories from GitHub API with pagination."""
        repos = []
        
        # Try to load token from projectscanner config
        if not self.github_token:
            self.github_token = self.load_token_from_config()
        
        # GitHub API endpoint - use different endpoints for authenticated vs unauthenticated
        if self.github_token:
            # Authenticated endpoint - includes private repos
            base_url = "https://api.github.com/user/repos"
            headers = ["-H", f"Authorization: token {self.github_token}"]
        else:
            # Unauthenticated endpoint - public repos only
            base_url = f"https://api.github.com/users/{self.github_username}/repos"
            headers = []
        
        page = 1
        per_page = 100  # Maximum allowed by GitHub API
        
        try:
            while True:
                # Build URL with pagination
                api_url = f"{base_url}?page={page}&per_page={per_page}"
                curl_cmd = ["curl", "-s"] + headers + [api_url]
                
                # Use curl to get repos (with authentication for private repos)
                result = subprocess.run(
                    curl_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    
                    # If no data returned, we've reached the end
                    if not data:
                        break
                    
                    for repo in data:
                        if not repo.get('fork', False):  # Skip forked repos
                            repos.append(repo['name'])
                    
                    # If we got fewer than per_page results, we've reached the end
                    if len(data) < per_page:
                        break
                    
                    page += 1
                else:
                    print(f"❌ Error fetching page {page}: {result.stderr}")
                    break
            
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
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                print(f"   ✅ Cloned {repo_name}")
                return repo_path
            else:
                print(f"   ❌ Failed to clone {repo_name}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Timeout cloning {repo_name}")
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
                cwd=repo_path,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"   ❌ Failed to add files: {result.stderr}")
                return False
            
            # Commit changes
            result = subprocess.run(
                ["git", "commit", "-m", "Add Agent Policy & Enforcement Framework"],
                capture_output=True,
                text=True,
                cwd=repo_path,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"   ❌ Failed to commit: {result.stderr}")
                return False
            
            # Push to GitHub
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True,
                cwd=repo_path,
                timeout=60
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
                    cwd=repo_path,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Pushed changes to GitHub (master branch)")
                    return True
                else:
                    print(f"   ❌ Failed to push: {result.stderr}")
                    return False
        
        except subprocess.TimeoutExpired:
            print(f"   ❌ Timeout during git operations")
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
    
    def run_batch(self, repos: List[str], start_index: int = 0) -> int:
        """Deploy agent policy framework to a batch of repositories."""
        # Create temp directory
        self.temp_dir.mkdir(exist_ok=True)
        
        if not repos:
            print("❌ No repositories found to process")
            return 1
        
        end_index = min(start_index + self.batch_size, len(repos))
        batch_repos = repos[start_index:end_index]
        
        print(f"🚀 Processing batch {start_index//self.batch_size + 1}")
        print(f"📦 Repositories {start_index + 1}-{end_index} of {len(repos)}")
        print("=" * 60)
        
        for i, repo_name in enumerate(batch_repos, start_index + 1):
            self.stats['total_repos'] += 1
            
            if self.deploy_to_repository(repo_name):
                self.stats['updated_repos'] += 1
                self.stats['processed_repos'].append(repo_name)
            else:
                self.stats['failed_repos'] += 1
            
            # Add a small delay between repositories
            if i < end_index:
                print("   ⏳ Waiting 2 seconds before next repository...")
                time.sleep(2)
        
        # Clean up temp directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        # Print batch summary
        print("\n" + "=" * 60)
        print(f"📊 BATCH SUMMARY (Repos {start_index + 1}-{end_index})")
        print("=" * 60)
        print(f"Successfully updated: {self.stats['updated_repos'] - (start_index//self.batch_size) * self.batch_size}")
        print(f"Failed: {self.stats['failed_repos'] - (start_index//self.batch_size) * self.batch_size}")
        
        return 0
    
    def run(self, dry_run: bool = False, start_batch: int = 0) -> int:
        """Deploy agent policy framework to all repositories in batches."""
        # Get repositories
        repos = self.get_github_repos()
        
        if not repos:
            print("❌ No repositories found to process")
            return 1
        
        if dry_run:
            print(f"📁 [DRY RUN] Found {len(repos)} repositories")
            for i, repo in enumerate(repos, 1):
                print(f"   {i}. {repo}")
            return 0
        
        total_batches = (len(repos) + self.batch_size - 1) // self.batch_size
        start_index = start_batch * self.batch_size
        
        print(f"🚀 Starting deployment to {len(repos)} repositories")
        print(f"📦 Processing in batches of {self.batch_size}")
        print(f"🔄 Total batches: {total_batches}")
        print(f"📍 Starting from batch {start_batch + 1}")
        
        return self.run_batch(repos, start_index)


def main():
    """Main entry point for GitHub repository deployment."""
    parser = argparse.ArgumentParser(description="Deploy agent policy framework to GitHub repositories in batches")
    parser.add_argument("--username", required=True,
                        help="GitHub username")
    parser.add_argument("--token", 
                        help="GitHub personal access token (optional)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without making changes")
    parser.add_argument("--batch-size", type=int, default=5,
                        help="Number of repositories to process per batch (default: 5)")
    parser.add_argument("--start-batch", type=int, default=0,
                        help="Start from batch number (0-based, default: 0)")
    
    args = parser.parse_args()
    
    deployer = GitHubRepoBatchDeployer(args.username, args.token, args.batch_size)
    exit_code = deployer.run(dry_run=args.dry_run, start_batch=args.start_batch)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 