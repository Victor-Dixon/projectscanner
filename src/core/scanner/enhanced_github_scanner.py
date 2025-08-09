#!/usr/bin/env python3
"""
Enhanced GitHub Library Scanner
Integrates comprehensive project analysis with GitHub repository scanning.
"""

import json
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
from collections import Counter

from enhanced_project_scanner import EnhancedProjectScanner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedGitHubScanner:
    """Enhanced GitHub scanner with comprehensive project analysis."""
    
    def __init__(self, github_username: str, output_dir: str = "github_library_enhanced"):
        self.github_username = github_username
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create temp directory for cloning
        self.temp_dir = Path("temp_scan")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Output files
        self.library_file = self.output_dir / "github_library_enhanced.json"
        self.scan_log_file = self.output_dir / "scan_log_enhanced.json"
        
        # Load existing data
        self.library = self.load_library()
        self.scan_log = self.load_scan_log()
    
    def load_library(self) -> Dict:
        """Load existing enhanced library."""
        if self.library_file.exists():
            try:
                with open(self.library_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load existing library: {e}")
        return {}
    
    def save_library(self):
        """Save enhanced library."""
        try:
            with open(self.library_file, 'w', encoding='utf-8') as f:
                json.dump(self.library, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving library: {e}")
    
    def load_scan_log(self) -> Dict:
        """Load scan log."""
        if self.scan_log_file.exists():
            try:
                with open(self.scan_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load scan log: {e}")
        return {
            "scanned_repos": [],
            "failed_repos": [],
            "last_scan": None,
            "total_repos": 0,
            "enhanced_analysis_count": 0
        }
    
    def save_scan_log(self):
        """Save scan log."""
        try:
            with open(self.scan_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.scan_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving scan log: {e}")
    
    def get_user_repositories(self) -> List[Dict]:
        """Get user repositories from GitHub API."""
        repos = []
        
        try:
            # Use GitHub API to get user repositories
            api_url = f"https://api.github.com/users/{self.github_username}/repos"
            
            result = subprocess.run(
                ["curl", "-s", api_url],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for repo in data:
                    repos.append({
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': repo.get('description', ''),
                        'language': repo.get('language'),
                        'private': repo['private'],
                        'fork': repo['fork'],
                        'stargazers_count': repo['stargazers_count'],
                        'forks_count': repo['forks_count'],
                        'size': repo['size'],
                        'topics': repo.get('topics', []),
                        'created_at': repo['created_at'],
                        'updated_at': repo['updated_at'],
                        'clone_url': repo['clone_url']
                    })
                
                logger.info(f"Found {len(repos)} repositories for {self.github_username}")
            else:
                logger.error(f"Failed to fetch repositories: {result.stderr}")
        
        except Exception as e:
            logger.error(f"Error fetching repositories: {e}")
        
        return repos
    
    def clone_repository(self, repo_data: Dict) -> Optional[Path]:
        """Clone a repository to temp directory."""
        try:
            repo_name = repo_data['name']
            clone_url = repo_data['clone_url']
            
            # Create repo directory
            repo_dir = self.temp_dir / repo_name
            
            # Remove existing clone if it exists
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            
            # Clone repository
            result = subprocess.run(
                ["git", "clone", clone_url, str(repo_dir)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Cloned {repo_name}")
                return repo_dir
            else:
                logger.error(f"❌ Failed to clone {repo_name}: {result.stderr}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Error cloning {repo_data['name']}: {e}")
            return None
    
    def scan_repository_enhanced(self, repo_data: Dict, repo_dir: Path) -> Dict:
        """Perform enhanced analysis of a repository."""
        try:
            # Use enhanced project scanner
            scanner = EnhancedProjectScanner(repo_dir)
            enhanced_analysis = scanner.scan_project()
            
            # Combine with basic repo data
            analysis_result = {
                'repository_info': repo_data,
                'enhanced_analysis': enhanced_analysis,
                'scan_timestamp': datetime.now().isoformat(),
                'analysis_version': 'enhanced_v1.0'
            }
            
            # Save individual analysis
            repo_id = f"{self.github_username}_{repo_data['name']}"
            analysis_file = self.output_dir / repo_id / f"enhanced_analysis_{repo_data['name']}.json"
            analysis_file.parent.mkdir(exist_ok=True)
            
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Enhanced analysis completed for {repo_data['name']}")
            return analysis_result
        
        except Exception as e:
            logger.error(f"❌ Error in enhanced analysis of {repo_data['name']}: {e}")
            return None
    
    def scan_all_repositories(self, force_rescan: bool = False, max_repos: Optional[int] = None):
        """Scan all repositories with enhanced analysis."""
        logger.info(f"🚀 Starting enhanced scan of repositories for {self.github_username}")
        
        # Get repositories
        repos = self.get_user_repositories()
        
        if not repos:
            logger.error("No repositories found")
            return
        
        # Limit repos if specified
        if max_repos:
            repos = repos[:max_repos]
        
        logger.info(f"📊 Found {len(repos)} repositories to scan")
        
        # Update scan log
        self.scan_log['last_scan'] = datetime.now().isoformat()
        self.scan_log['total_repos'] = len(repos)
        
        successful_scans = 0
        enhanced_analyses = 0
        
        for i, repo_data in enumerate(repos, 1):
            repo_name = repo_data['name']
            repo_id = f"{self.github_username}_{repo_name}"
            
            logger.info(f"📁 Processing {i}/{len(repos)}: {repo_name}")
            
            # Check if already scanned (unless force rescan)
            if not force_rescan and repo_id in self.library:
                logger.info(f"⏭️  Skipping {repo_name} (already scanned)")
                continue
            
            try:
                # Clone repository
                repo_dir = self.clone_repository(repo_data)
                if not repo_dir:
                    self.scan_log['failed_repos'].append({
                        'name': repo_name,
                        'error': 'Failed to clone',
                        'timestamp': datetime.now().isoformat()
                    })
                    continue
                
                # Perform enhanced analysis
                analysis_result = self.scan_repository_enhanced(repo_data, repo_dir)
                
                if analysis_result:
                    # Store in library
                    self.library[repo_id] = analysis_result
                    successful_scans += 1
                    enhanced_analyses += 1
                    
                    # Update scan log
                    self.scan_log['scanned_repos'].append({
                        'name': repo_name,
                        'timestamp': datetime.now().isoformat(),
                        'enhanced_analysis': True
                    })
                    
                    # Save progress periodically
                    if i % 5 == 0:
                        self.save_library()
                        self.save_scan_log()
                
                # Clean up cloned repository
                if repo_dir.exists():
                    shutil.rmtree(repo_dir)
            
            except Exception as e:
                logger.error(f"❌ Error processing {repo_name}: {e}")
                self.scan_log['failed_repos'].append({
                    'name': repo_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Final save
        self.save_library()
        self.save_scan_log()
        
        # Generate summary
        self.generate_enhanced_summary()
        
        logger.info(f"✅ Enhanced scan complete!")
        logger.info(f"📊 Results: {successful_scans} successful, {len(self.scan_log['failed_repos'])} failed")
        logger.info(f"🔍 Enhanced analyses: {enhanced_analyses}")
    
    def generate_enhanced_summary(self):
        """Generate enhanced library summary."""
        summary = {
            'total_repositories': len(self.library),
            'scan_timestamp': datetime.now().isoformat(),
            'repositories': [],
            'technology_summary': {},
            'purpose_categories': {},
            'maturity_distribution': {},
            'enhanced_features': {
                'comprehensive_analysis': True,
                'project_essence_extraction': True,
                'business_logic_analysis': True,
                'architecture_patterns': True,
                'dependency_analysis': True
            }
        }
        
        # Analyze all repositories
        all_technologies = Counter()
        all_purposes = Counter()
        all_maturity = Counter()
        
        for repo_id, repo_data in self.library.items():
            repo_info = repo_data.get('repository_info', {})
            enhanced_analysis = repo_data.get('enhanced_analysis', {})
            
            # Basic repo info
            repo_summary = {
                'id': repo_id,
                'name': repo_info.get('name', ''),
                'description': repo_info.get('description', ''),
                'language': repo_info.get('language'),
                'private': repo_info.get('private', False),
                'stars': repo_info.get('stargazers_count', 0),
                'forks': repo_info.get('forks_count', 0)
            }
            
            # Enhanced analysis data
            if 'enhanced_analysis' in repo_data:
                enhanced = repo_data['enhanced_analysis']
                
                # Extract technologies
                if 'dependencies' in enhanced:
                    deps = enhanced['dependencies']
                    for tech in deps.get('python_packages', []):
                        all_technologies[tech] += 1
                
                # Extract purpose
                if 'purpose_analysis' in enhanced:
                    purpose = enhanced['purpose_analysis']
                    primary_purpose = purpose.get('primary_function', 'Unknown')
                    all_purposes[primary_purpose] += 1
                
                # Extract maturity
                if 'maturity' in enhanced:
                    maturity = enhanced['maturity']
                    maturity_level = maturity.get('maturity_level', 'unknown')
                    all_maturity[maturity_level] += 1
                
                # Add enhanced data to summary
                if 'project_essence' in enhanced:
                    essence = enhanced['project_essence']
                    repo_summary['essence'] = {
                        'summary': essence.get('summary', ''),
                        'primary_purpose': essence.get('primary_purpose', ''),
                        'maturity': essence.get('maintenance_status', ''),
                        'quality_score': essence.get('technical_complexity', '')
                    }
            
            summary['repositories'].append(repo_summary)
        
        # Add summaries
        summary['technology_summary'] = dict(all_technologies.most_common(20))
        summary['purpose_categories'] = dict(all_purposes)
        summary['maturity_distribution'] = dict(all_maturity)
        
        # Save enhanced summary
        summary_file = self.output_dir / "enhanced_library_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Enhanced summary generated: {summary_file}")
        
        # Print summary
        print(f"\n📊 ENHANCED LIBRARY SUMMARY")
        print("=" * 60)
        print(f"Total repositories: {summary['total_repositories']}")
        print(f"Top technologies: {', '.join(list(summary['technology_summary'].keys())[:5])}")
        print(f"Purpose categories: {len(summary['purpose_categories'])}")
        print(f"Maturity levels: {dict(summary['maturity_distribution'])}")


def main():
    """Main entry point for enhanced GitHub scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced GitHub Library Scanner")
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("--output-dir", default="github_library_enhanced",
                        help="Output directory for enhanced analysis")
    parser.add_argument("--force-rescan", action="store_true",
                        help="Force rescan of all repositories")
    parser.add_argument("--max-repos", type=int,
                        help="Maximum number of repositories to scan")
    
    args = parser.parse_args()
    
    scanner = EnhancedGitHubScanner(args.username, args.output_dir)
    scanner.scan_all_repositories(
        force_rescan=args.force_rescan,
        max_repos=args.max_repos
    )


if __name__ == "__main__":
    main() 