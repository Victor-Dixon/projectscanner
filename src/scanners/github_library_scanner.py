"""
MODULE: github_library_scanner
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""
GitHub Library Scanner - Scan all repositories from a GitHub account and build a library.
"""

import sys
import json
import tempfile
import shutil
import time
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from core.projectscanner import ProjectScanner


# Concept: TODO - Explain the core idea behind clone_repository
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def clone_repository(repo_url: str, temp_dir: Path) -> Path:
# Concept: TODO - Purpose of clone_repository
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation details
    """Clone a GitHub repository to a temporary directory."""
    try:
        # Extract repo name from URL
        repo_name = repo_url.split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        clone_path = temp_dir / repo_name
        
        # Clone the repository
        subprocess.run([
            'git', 'clone', repo_url, str(clone_path)
        ], check=True, capture_output=True)
        
        return clone_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clone repository: {e.stderr.decode()}")
    except Exception as e:
        raise Exception(f"Error cloning repository: {str(e)}")


class GitHubLibraryScanner:
    """Scans all repositories from a GitHub account and builds a library."""
# Concept: TODO - clone_repository
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation
# Concept: TODO - Purpose of clone_repository
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
# Concept: TODO - Purpose of clone_repository
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    
    # Concept: TODO - Explain the core idea behind __init__
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def __init__(self, github_username: str, output_dir: str = "github_library_enhanced"):
    # Concept: TODO - Purpose of __init__
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        self.github_username = github_username
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create local temp directory within project
        self.temp_dir = Path("temp_repos")
        self.temp_dir.mkdir(exist_ok=True)
        
        self.library_file = self.output_dir / "github_library_enhanced.json"
        self.scan_log_file = self.output_dir / "scan_log.json"
        
        self.library = self.load_library()
        self.scan_log = self.load_scan_log()
    
    # Concept: TODO - Explain the core idea behind load_library
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def load_library(self) -> Dict:
    # Concept: TODO - Purpose of load_library
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation details
        """Load existing library data."""
        if self.library_file.exists():
            try:
                with self.library_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load existing library: {e}")
        return {}
    
    # Concept: TODO - Explain the core idea behind save_library
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def save_library(self):
        """Save library data."""
    # Concept: TODO - load_library
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation
    # Concept: TODO - Purpose of load_library
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        try:
            with self.library_file.open('w', encoding='utf-8') as f:
                json.dump(self.library, f, indent=2)
        except Exception as e:
            print(f"Error saving library: {e}")
    
    # Concept: TODO - Explain the core idea behind load_scan_log
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def load_scan_log(self) -> Dict:
    # Concept: TODO - Purpose of load_scan_log
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation details
        """Load scan log data."""
        if self.scan_log_file.exists():
            try:
                with self.scan_log_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load scan log: {e}")
        return {"scanned_repos": [], "failed_repos": [], "last_scan": None}
    
    # Concept: TODO - Explain the core idea behind save_scan_log
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def save_scan_log(self):
        """Save scan log data."""
    # Concept: TODO - load_scan_log
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation
    # Concept: TODO - Purpose of load_scan_log
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        try:
            with self.scan_log_file.open('w', encoding='utf-8') as f:
                json.dump(self.scan_log, f, indent=2)
        except Exception as e:
            print(f"Error saving scan log: {e}")
    
    # Concept: TODO - Explain the core idea behind get_user_repositories
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def get_user_repositories(self) -> List[Dict]:
        """Get all repositories for the GitHub user."""
        try:
            import requests
            
            # GitHub API endpoint for user repositories
            url = f"https://api.github.com/users/{self.github_username}/repos"
    # Concept: TODO - Purpose of get_user_repositories
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
            
            print(f"Fetching repositories for user: {self.github_username}")
            
            response = requests.get(url)
            response.raise_for_status()
            
            repos = response.json()
            print(f"Found {len(repos)} repositories")
            
            return repos
            
        except ImportError:
            print("Error: requests library not found. Install with: pip install requests")
            return []
        except Exception as e:
            print(f"Error fetching repositories: {e}")
            return []
    
    # Concept: TODO - Explain the core idea behind generate_repo_name
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def generate_repo_name(self, repo_data: Dict) -> str:
        """Generate a unique name for the repository analysis."""
    # Concept: TODO - Purpose of get_user_repositories
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        repo_name = repo_data['name']
        owner = repo_data['owner']['login']
        
        # Create a unique identifier
        unique_id = f"{owner}_{repo_name}"
        
        # Clean the name for file system
        clean_name = "".join(c for c in unique_id if c.isalnum() or c in ('_', '-')).rstrip()
        
        return clean_name
    
    # Concept: TODO - Explain the core idea behind scan_repository
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 117 lines > 30 limit)
    def scan_repository(self, repo_data: Dict, force_rescan: bool = False) -> bool:
    # Concept: TODO - Purpose of scan_repository
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation details
        """Scan a single repository."""
        repo_name = repo_data['name']
        repo_url = repo_data['clone_url']
        unique_name = self.generate_repo_name(repo_data)
        
        print(f"\nScanning repository: {repo_name}")
        print(f"   URL: {repo_url}")
        print(f"   Unique ID: {unique_name}")
        
        # Check if already scanned and not forcing rescan
        if unique_name in self.library and not force_rescan:
            print(f"   Already scanned, skipping...")
            return True
        
        # Create repository-specific temp directory within project
        repo_temp_dir = self.temp_dir / unique_name
        if repo_temp_dir.exists():
            shutil.rmtree(repo_temp_dir)
        repo_temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Clone the repository
            print(f"   Cloning repository...")
            clone_path = clone_repository(repo_url, repo_temp_dir)
            
            # Create repository-specific output directory
            repo_output_dir = self.output_dir / unique_name
            repo_output_dir.mkdir(exist_ok=True)
            
            # Scan the repository
            print(f"   Starting analysis...")
            scanner = ProjectScanner(
                project_root=str(clone_path),
                output_dir=str(repo_output_dir)
            )
            
            scanner.scan_project()
            scanner.categorize_agents()
            scanner.report_generator.save_report()
            scanner.export_chatgpt_context()
            
            # Load the generated reports
            analysis_file = scanner.report_generator.analysis_file
            context_file = scanner.report_generator.context_file
            
            analysis_path = repo_output_dir / analysis_file
            context_path = repo_output_dir / context_file
            
            # Read the analysis data
            analysis_data = {}
            context_data = {}
            
            if analysis_path.exists():
                with analysis_path.open('r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
            
            if context_path.exists():
                with context_path.open('r', encoding='utf-8') as f:
                    context_data = json.load(f)
            
            # Store in library
            self.library[unique_name] = {
                'name': repo_name,
                'url': repo_url,
                'owner': repo_data['owner']['login'],
                'description': repo_data.get('description', ''),
                'language': repo_data.get('language', ''),
                'private': repo_data.get('private', False),
                'fork': repo_data.get('fork', False),
                'created_at': repo_data.get('created_at', ''),
                'updated_at': repo_data.get('updated_at', ''),
                'analysis': analysis_data,
                'context': context_data,
                'scanned_at': datetime.now().isoformat()
            }
            
            # Update scan log
            self.scan_log['scanned_repos'].append({
                'name': repo_name,
                'unique_id': unique_name,
                'scanned_at': datetime.now().isoformat()
            })
            
            print(f"   Successfully scanned {len(scanner.analysis)} files")
            
            return True
            
        except Exception as e:
            print(f"   Error scanning repository: {e}")
            
            # Update scan log with failure
            self.scan_log['failed_repos'].append({
                'name': repo_name,
                'unique_id': unique_name,
                'error': str(e),
                'failed_at': datetime.now().isoformat()
            })
            
            return False
            
        finally:
            # Clean up temporary directory
            try:
                if repo_temp_dir.exists():
                    # On Windows, git objects might be locked - try to remove them first
                    git_objects = repo_temp_dir / ".git" / "objects"
    # Concept: TODO - scan_repository
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation
    # Concept: TODO - Purpose of scan_repository
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
                    if git_objects.exists():
                        try:
                            shutil.rmtree(git_objects, ignore_errors=True)
                        except Exception:
                            pass  # Ignore cleanup errors for git objects
                    
                    # Remove the temp directory
                    shutil.rmtree(repo_temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"   Warning: Could not clean up temporary directory: {e}")
    
    # Concept: TODO - Explain the core idea behind scan_all_repositories
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 55 lines > 30 limit)
    def scan_all_repositories(self, force_rescan: bool = False, max_repos: Optional[int] = None):
        """Scan all repositories for the GitHub user."""
    # Concept: TODO - Purpose of scan_repository
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        print(f"Starting scan of repositories for user: {self.github_username}")
        
        # Get all repositories
        repos = self.get_user_repositories()
        
        if not repos:
            print("No repositories found or error fetching repositories.")
            return
        
        # Limit repositories if specified
        if max_repos:
            repos = repos[:max_repos]
            print(f"Limiting scan to {max_repos} repositories")
        
        print(f"Scanning {len(repos)} repositories...")
        
        # Track progress
        successful_scans = 0
        failed_scans = 0
        
        for i, repo in enumerate(repos, 1):
            print(f"\nProgress: {i}/{len(repos)}")
            
            try:
                if self.scan_repository(repo, force_rescan):
                    successful_scans += 1
                else:
                    failed_scans += 1
            except Exception as e:
                print(f"   Unexpected error scanning {repo['name']}: {e}")
                failed_scans += 1
            
            # Save progress periodically
            if i % 10 == 0:
                self.save_library()
                self.save_scan_log()
                print("Progress saved...")
        
        # Final save
        self.save_library()
        self.save_scan_log()
        
        print(f"\nScan completed!")
        print(f"  • Successful scans: {successful_scans}")
        print(f"  • Failed scans: {failed_scans}")
        print(f"  • Total repositories: {len(repos)}")
        
        # Update last scan timestamp
        self.scan_log['last_scan'] = datetime.now().isoformat()
        self.save_scan_log()
    
    # Concept: TODO - Explain the core idea behind generate_library_summary
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 44 lines > 30 limit)
    def generate_library_summary(self) -> Dict:
        """Generate a summary of the library."""
    # Concept: TODO - Purpose of scan_all_repositories
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        summary = {
            'total_repositories': len(self.library),
            'public_repositories': 0,
            'private_repositories': 0,
            'languages': {},
            'total_files_scanned': 0,
            'scan_timestamp': self.scan_log.get('last_scan'),
            'repositories': []
        }
        
        for repo_id, repo_data in self.library.items():
            # Count public/private
            if repo_data.get('private', False):
                summary['private_repositories'] += 1
            else:
                summary['public_repositories'] += 1
            
            # Count languages
            language = repo_data.get('language', 'Unknown')
            summary['languages'][language] = summary['languages'].get(language, 0) + 1
            
            # Count files
            analysis = repo_data.get('analysis', {})
            if isinstance(analysis, dict):
                files_scanned = analysis.get('file_count', len(analysis))
            else:
                files_scanned = 0
            summary['total_files_scanned'] += files_scanned
            
            # Add repository info
            summary['repositories'].append({
                'name': repo_data['name'],
                'id': repo_id,
                'language': language,
                'files_scanned': files_scanned,
                'private': repo_data.get('private', False)
            })
        
        return summary
    
    # Concept: TODO - Explain the core idea behind export_library_summary
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def export_library_summary(self, output_file: str = "library_summary.json"):
        """Export a summary of the library."""
    # Concept: TODO - Purpose of generate_library_summary
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        summary = self.generate_library_summary()
        
        output_path = self.output_dir / output_file
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Library summary exported to: {output_path}")


# Concept: TODO - Explain the core idea behind main
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def main():
# Concept: TODO
# Trade-off: TODO
# Execution: TODO
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python github_library_scanner.py <github_username> [output_dir]")
        sys.exit(1)
    
    username = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "github_library_enhanced"
# Concept: TODO - main
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation
# Concept: TODO - Purpose of main
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    
    scanner = GitHubLibraryScanner(username, output_dir)
    scanner.scan_all_repositories()
    scanner.export_library_summary()


if __name__ == "__main__":
    main() 
# Concept: TODO - Purpose of main
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach