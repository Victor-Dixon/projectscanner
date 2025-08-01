#!/usr/bin/env python3
"""
Enhanced GitHub Library Scanner - Scan all repositories (public and private) from a GitHub account.
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


class EnhancedGitHubLibraryScanner:
    """Scans all repositories (public and private) from a GitHub account."""
    
    def __init__(self, github_username: str, github_token: Optional[str] = None, output_dir: str = "github_library_enhanced"):
        self.github_username = github_username
        self.github_token = github_token
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create local temp directory within project
        self.temp_dir = Path("temp_repos")
        self.temp_dir.mkdir(exist_ok=True)
        
        self.library_file = self.output_dir / "github_library_enhanced.json"
        self.scan_log_file = self.output_dir / "scan_log_enhanced.json"
        
        self.library = self.load_library()
        self.scan_log = self.load_scan_log()
    
    def load_library(self) -> Dict:
        """Load existing library data."""
        if self.library_file.exists():
            try:
                with self.library_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Warning: Could not load existing library: {e}")
        return {}
    
    def save_library(self):
        """Save library data."""
        try:
            with self.library_file.open('w', encoding='utf-8') as f:
                json.dump(self.library, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving library: {e}")
    
    def load_scan_log(self) -> Dict:
        """Load scan log data."""
        if self.scan_log_file.exists():
            try:
                with self.scan_log_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Warning: Could not load scan log: {e}")
        return {"scanned_repos": [], "failed_repos": [], "last_scan": None}
    
    def save_scan_log(self):
        """Save scan log data."""
        try:
            with self.scan_log_file.open('w', encoding='utf-8') as f:
                json.dump(self.scan_log, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving scan log: {e}")
    
    def get_user_repositories(self) -> List[Dict]:
        """Get all repositories (public and private) for the GitHub user."""
        try:
            import requests
            
            # GitHub API endpoint for user repositories
            # Use authenticated endpoint to get both public and private repos
            if self.github_token:
                url = "https://api.github.com/user/repos"
            else:
                url = f"https://api.github.com/users/{self.github_username}/repos"
            
            headers = {}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
                print(f"Using GitHub token for private repository access")
            else:
                print(f"No GitHub token provided - only public repositories will be scanned")
            
            print(f"Fetching repositories for user: {self.github_username}")
            
            all_repos = []
            page = 1
            
            while True:
                params = {'page': page, 'per_page': 100}
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                repos = response.json()
                if not repos:
                    break
                
                all_repos.extend(repos)
                page += 1
                
                # Rate limiting
                if 'X-RateLimit-Remaining' in response.headers:
                    remaining = int(response.headers['X-RateLimit-Remaining'])
                    if remaining < 10:
                        print(f"Rate limit warning: {remaining} requests remaining")
            
            print(f"Found {len(all_repos)} repositories")
            
            # Count public vs private
            public_count = sum(1 for repo in all_repos if not repo.get('private', False))
            private_count = sum(1 for repo in all_repos if repo.get('private', False))
            
            print(f"  • Public repositories: {public_count}")
            print(f"  • Private repositories: {private_count}")
            
            return all_repos
            
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
        is_private = repo_data.get('private', False)
        
        # Create a unique identifier
        unique_id = f"{owner}_{repo_name}"
        if is_private:
            unique_id += "_private"
        
        # Clean the name for file system
        clean_name = "".join(c for c in unique_id if c.isalnum() or c in ('_', '-')).rstrip()
        
        return clean_name
    
    def clone_repository(self, repo_url: str, temp_dir: Path) -> Path:
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
    
    def scan_repository(self, repo_data: Dict, force_rescan: bool = False) -> bool:
        """Scan a single repository."""
        repo_name = repo_data['name']
        repo_url = repo_data['clone_url']
        is_private = repo_data.get('private', False)
        unique_name = self.generate_repo_name(repo_data)
        
        print(f"\nScanning repository: {repo_name}")
        if is_private:
            print(f"   PRIVATE REPOSITORY")
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
            clone_path = self.clone_repository(repo_url, repo_temp_dir)
            
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
                'private': is_private,
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
                'private': is_private,
                'scanned_at': datetime.now().isoformat()
            })
            
            print(f"   Successfully scanned {len(scanner.analysis)} files")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error analyzing {repo_name}: {e}")
            
            # Update scan log with failure
            self.scan_log['failed_repos'].append({
                'name': repo_name,
                'unique_id': unique_name,
                'private': is_private,
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
                    if git_objects.exists():
                        try:
                            shutil.rmtree(git_objects, ignore_errors=True)
                        except Exception:
                            pass  # Ignore cleanup errors for git objects
                    
                    # Remove the temp directory
                    shutil.rmtree(repo_temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"   Warning: Could not clean up temporary directory: {e}")
    
    def scan_all_repositories(self, force_rescan: bool = False, max_repos: Optional[int] = None):
        """Scan all repositories for the GitHub user."""
        print(f"Starting enhanced scan of repositories for user: {self.github_username}")
        
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
        
        print(f"\nEnhanced scan completed!")
        print(f"  • Successful scans: {successful_scans}")
        print(f"  • Failed scans: {failed_scans}")
        print(f"  • Total repositories: {len(repos)}")
        
        # Update last scan timestamp
        self.scan_log['last_scan'] = datetime.now().isoformat()
        self.save_scan_log()
    
    def generate_library_summary(self) -> Dict:
        """Generate a summary of the library."""
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
            files_scanned = analysis.get('file_count', 0)
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
    
    def export_library_summary(self, output_file: str = "enhanced_library_summary.json"):
        """Export a summary of the library."""
        summary = self.generate_library_summary()
        
        output_path = self.output_dir / output_file
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Enhanced library summary exported to: {output_path}")


def main():
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python github_library_scanner_private.py <github_username> [github_token] [output_dir]")
        sys.exit(1)
    
    username = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "github_library_enhanced"
    
    scanner = EnhancedGitHubLibraryScanner(username, token, output_dir)
    scanner.scan_all_repositories()
    scanner.export_library_summary()


if __name__ == "__main__":
    main() 