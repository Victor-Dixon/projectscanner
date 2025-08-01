#!/usr/bin/env python3
"""
Enhanced GitHub Library Scanner - Can scan both public and private repositories.
"""

import json
import sys
import tempfile
import shutil
import time
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from core.projectscanner.scanner import ProjectScanner
from scanners.github_library_scanner import clone_repository


class EnhancedGitHubLibraryScanner:
    """Scans all repositories (public and private) from a GitHub account."""
    
    def __init__(self, github_username: str, github_token: Optional[str] = None, output_dir: str = "github_library_enhanced"):
        self.github_username = github_username
        self.github_token = github_token
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.library_file = self.output_dir / "github_library_enhanced.json"
        self.scan_log_file = self.output_dir / "scan_log_enhanced.json"
        
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
        
        # Create temporary directory for cloning
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Clone the repository
            print(f"   Cloning repository...")
            
            # Use SSH URL for private repos if token is provided
            if is_private and self.github_token:
                # For private repos, we need to use HTTPS with token
                clone_url = repo_url.replace('https://', f'https://{self.github_token}@')
            else:
                clone_url = repo_url
            
            clone_path = clone_repository(clone_url, temp_dir)
            
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
                'is_private': is_private,
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
                'is_private': is_private,
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
                'is_private': is_private,
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
        print(f"Starting Enhanced GitHub Library Scanner")
        print(f"User: {self.github_username}")
        print(f"Token provided: {'Yes' if self.github_token else 'No'}")
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
        public_scans = 0
        private_scans = 0
        
        for i, repo in enumerate(repos, 1):
            print(f"\nProgress: {i}/{len(repos)}")
            
            if self.scan_repository(repo, force_rescan):
                successful_scans += 1
                if repo.get('private', False):
                    private_scans += 1
                else:
                    public_scans += 1
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
        
        print(f"\nEnhanced scan completed!")
        print(f"Successful scans: {successful_scans}")
        print(f"Failed scans: {failed_scans}")
        print(f"Public repositories: {public_scans}")
        print(f"Private repositories: {private_scans}")
        print(f"Library saved to: {self.library_file}")
        print(f"Scan log saved to: {self.scan_log_file}")
    
    def generate_library_summary(self) -> Dict:
        """Generate a summary of the library."""
        summary = {
            'total_repos': len(self.library),
            'total_files': sum(repo.get('file_count', 0) for repo in self.library.values()),
            'public_repos': sum(1 for repo in self.library.values() if not repo.get('is_private', False)),
            'private_repos': sum(1 for repo in self.library.values() if repo.get('is_private', False)),
            'languages': {},
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
    
    def export_library_summary(self, output_file: str = "enhanced_library_summary.json"):
        """Export a summary of the library."""
        summary = self.generate_library_summary()
        
        summary_file = self.output_dir / output_file
        with summary_file.open('w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Enhanced library summary exported to: {summary_file}")
        return summary


def main():
    """Main function for enhanced GitHub library scanning."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scan all repositories (public and private) from a GitHub account"
    )
    parser.add_argument("username", help="GitHub username to scan")
    parser.add_argument("--token", help="GitHub Personal Access Token for private repository access")
    parser.add_argument("--output-dir", default="github_library_enhanced", help="Output directory for library")
    parser.add_argument("--force-rescan", action="store_true", help="Force rescan of already scanned repositories")
    parser.add_argument("--max-repos", type=int, help="Maximum number of repositories to scan")
    parser.add_argument("--summary-only", action="store_true", help="Only generate library summary")
    
    args = parser.parse_args()
    
    # Create scanner
    scanner = EnhancedGitHubLibraryScanner(args.username, args.token, args.output_dir)
    
    if args.summary_only:
        # Only generate summary
        summary = scanner.generate_library_summary()
        print("📊 Enhanced Library Summary:")
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
        print("\n📊 Final Enhanced Library Summary:")
        print(json.dumps(summary, indent=2))
        scanner.export_library_summary()


if __name__ == "__main__":
    main() 