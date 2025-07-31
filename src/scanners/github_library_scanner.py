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

from core.projectscanner.scanner import ProjectScanner


def clone_repository(repo_url: str, temp_dir: Path) -> Path:
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
    
    def __init__(self, github_username: str, output_dir: str = "github_library"):
        self.github_username = github_username
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.library_file = self.output_dir / "github_library.json"
        self.scan_log_file = self.output_dir / "scan_log.json"
        
        # Load existing library
        self.library = self.load_library()
        self.scan_log = self.load_scan_log()
        
    def load_library(self) -> Dict:
        """Load existing library data."""
        if self.library_file.exists():
            try:
                with self.library_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load existing library: {e}")
        return {}
    
    def save_library(self):
        """Save library data."""
        try:
            with self.library_file.open('w', encoding='utf-8') as f:
                json.dump(self.library, f, indent=2)
        except Exception as e:
            print(f"Error saving library: {e}")
    
    def load_scan_log(self) -> Dict:
        """Load scan log data."""
        if self.scan_log_file.exists():
            try:
                with self.scan_log_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load scan log: {e}")
        return {"scanned_repos": [], "failed_repos": [], "last_scan": None}
    
    def save_scan_log(self):
        """Save scan log data."""
        try:
            with self.scan_log_file.open('w', encoding='utf-8') as f:
                json.dump(self.scan_log, f, indent=2)
        except Exception as e:
            print(f"Error saving scan log: {e}")
    
    def get_user_repositories(self) -> List[Dict]:
        """Get all repositories for the GitHub user."""
        try:
            import requests
            
            # GitHub API endpoint for user repositories
            url = f"https://api.github.com/users/{self.github_username}/repos"
            
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
    
    def generate_repo_name(self, repo_data: Dict) -> str:
        """Generate a unique name for the repository analysis."""
        repo_name = repo_data['name']
        owner = repo_data['owner']['login']
        
        # Create a unique identifier
        unique_id = f"{owner}_{repo_name}"
        
        # Clean the name for file system
        clean_name = "".join(c for c in unique_id if c.isalnum() or c in ('_', '-')).rstrip()
        
        return clean_name
    
    def scan_repository(self, repo_data: Dict, force_rescan: bool = False) -> bool:
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
        
        # Create temporary directory for cloning
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Clone the repository
            print(f"   Cloning repository...")
            clone_path = clone_repository(repo_url, temp_dir)
            
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
                'repo_name': repo_name,
                'owner': repo_data['owner']['login'],
                'repo_url': repo_url,
                'description': repo_data.get('description', ''),
                'language': repo_data.get('language', ''),
                'stars': repo_data.get('stargazers_count', 0),
                'forks': repo_data.get('forks_count', 0),
                'created_at': repo_data.get('created_at', ''),
                'updated_at': repo_data.get('updated_at', ''),
                'scan_date': datetime.now().isoformat(),
                'analysis_file': str(analysis_path),
                'context_file': str(context_path),
                'file_count': len(analysis_data),
                'analysis_data': analysis_data,
                'context_data': context_data
            }
            
            # Update scan log
            self.scan_log['scanned_repos'].append({
                'unique_name': unique_name,
                'repo_name': repo_name,
                'scan_date': datetime.now().isoformat(),
                'status': 'success'
            })
            
            print(f"   Successfully scanned {len(analysis_data)} files")
            return True
            
        except Exception as e:
            print(f"   Error scanning repository: {e}")
            
            # Update scan log with failure
            self.scan_log['failed_repos'].append({
                'unique_name': unique_name,
                'repo_name': repo_name,
                'scan_date': datetime.now().isoformat(),
                'error': str(e)
            })
            
            return False
            
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"   Warning: Could not clean up temporary directory: {e}")
    
    def scan_all_repositories(self, force_rescan: bool = False, max_repos: Optional[int] = None):
        """Scan all repositories for the GitHub user."""
        print(f"Starting GitHub Library Scanner")
        print(f"User: {self.github_username}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Force Rescan: {force_rescan}")
        
        # Get all repositories
        repos = self.get_user_repositories()
        
        if not repos:
            print("No repositories found or error occurred")
            return
        
        # Limit repositories if specified
        if max_repos:
            repos = repos[:max_repos]
            print(f"Limiting scan to {max_repos} repositories")
        
        # Update scan log
        self.scan_log['last_scan'] = datetime.now().isoformat()
        
        # Scan each repository
        successful_scans = 0
        failed_scans = 0
        
        for i, repo in enumerate(repos, 1):
            print(f"\nProgress: {i}/{len(repos)}")
            
            if self.scan_repository(repo, force_rescan):
                successful_scans += 1
            else:
                failed_scans += 1
            
            # Save progress periodically
            if i % 10 == 0:
                self.save_library()
                self.save_scan_log()
                print(f"Progress saved...")
            
            # Small delay to be respectful to GitHub API
            time.sleep(1)
        
        # Final save
        self.save_library()
        self.save_scan_log()
        
        print(f"\nScan completed!")
        print(f"Successful scans: {successful_scans}")
        print(f"Failed scans: {failed_scans}")
        print(f"Library saved to: {self.library_file}")
        print(f"Scan log saved to: {self.scan_log_file}")
    
    def generate_library_summary(self) -> Dict:
        """Generate a summary of the library."""
        summary = {
            'total_repos': len(self.library),
            'total_files': sum(repo.get('file_count', 0) for repo in self.library.values()),
            'languages': {},
            'topics': {},
            'scan_stats': {
                'successful_scans': len(self.scan_log.get('scanned_repos', [])),
                'failed_scans': len(self.scan_log.get('failed_repos', [])),
                'last_scan': self.scan_log.get('last_scan')
            }
        }
        
        # Count languages
        for repo in self.library.values():
            lang = repo.get('language', 'Unknown')
            summary['languages'][lang] = summary['languages'].get(lang, 0) + 1
        
        return summary
    
    def export_library_summary(self, output_file: str = "library_summary.json"):
        """Export a summary of the library."""
        summary = self.generate_library_summary()
        
        summary_file = self.output_dir / output_file
        with summary_file.open('w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Library summary exported to: {summary_file}")
        return summary


def main():
    """Main function for GitHub library scanning."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scan all repositories from a GitHub account and build a library"
    )
    parser.add_argument("username", help="GitHub username to scan")
    parser.add_argument("--output-dir", default="github_library", help="Output directory for library")
    parser.add_argument("--force-rescan", action="store_true", help="Force rescan of already scanned repositories")
    parser.add_argument("--max-repos", type=int, help="Maximum number of repositories to scan")
    parser.add_argument("--summary-only", action="store_true", help="Only generate library summary")
    
    args = parser.parse_args()
    
    # Create scanner
    scanner = GitHubLibraryScanner(args.username, args.output_dir)
    
    if args.summary_only:
        # Only generate summary
        summary = scanner.generate_library_summary()
        print("Library Summary:")
        print(json.dumps(summary, indent=2))
        scanner.export_library_summary()
    else:
        # Scan all repositories
        scanner.scan_all_repositories(
            force_rescan=args.force_rescan,
            max_repos=args.max_repos
        )
        
        # Generate summary
        summary = scanner.generate_library_summary()
        print("\nFinal Library Summary:")
        print(json.dumps(summary, indent=2))
        scanner.export_library_summary()


if __name__ == "__main__":
    main() 