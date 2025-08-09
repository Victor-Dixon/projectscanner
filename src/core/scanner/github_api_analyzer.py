#!/usr/bin/env python3
"""
GitHub API Analyzer
Uses GitHub API to analyze repositories without cloning
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

class GitHubAPIAnalyzer:
    """Analyzes GitHub repositories using the GitHub API."""
    
    def __init__(self, github_username: str = "Dadudekc"):
        self.github_username = github_username
        self.token = self.load_github_token()
        self.analysis_results = {}
        
    def load_github_token(self) -> Optional[str]:
        """Load GitHub token from projectscanner config."""
        try:
            config_file = Path("config/github_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('token')
        except Exception:
            pass
        return None
    
    def make_api_request(self, endpoint: str) -> Optional[Dict]:
        """Make a GitHub API request."""
        try:
            if self.token:
                api_url = f"https://api.github.com/{endpoint}"
                headers = ["-H", f"Authorization: token {self.token}"]
            else:
                api_url = f"https://api.github.com/{endpoint}"
                headers = []
            
            curl_cmd = ["curl", "-s"] + headers + [api_url]
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"⚠️ API request failed for {endpoint}: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error making API request to {endpoint}: {e}")
            return None
    
    def get_repository_list(self) -> List[Dict]:
        """Get list of repositories with metadata."""
        repos = []
        
        try:
            if self.token:
                endpoint = "user/repos"
            else:
                endpoint = f"users/{self.github_username}/repos"
            
            page = 1
            per_page = 100
            
            while True:
                url = f"{endpoint}?page={page}&per_page={per_page}"
                data = self.make_api_request(url)
                
                if not data:
                    break
                
                for repo in data:
                    if not repo.get('fork', False):
                        repos.append(repo)
                
                if len(data) < per_page:
                    break
                
                page += 1
                
        except Exception as e:
            print(f"⚠️ Error fetching repositories: {e}")
        
        return repos
    
    def get_repository_details(self, repo_name: str) -> Optional[Dict]:
        """Get detailed information about a specific repository."""
        endpoint = f"repos/{self.github_username}/{repo_name}"
        return self.make_api_request(endpoint)
    
    def get_repository_languages(self, repo_name: str) -> Dict[str, int]:
        """Get language statistics for a repository."""
        endpoint = f"repos/{self.github_username}/{repo_name}/languages"
        return self.make_api_request(endpoint) or {}
    
    def get_repository_topics(self, repo_name: str) -> List[str]:
        """Get topics/tags for a repository."""
        endpoint = f"repos/{self.github_username}/{repo_name}/topics"
        data = self.make_api_request(endpoint)
        return data.get('names', []) if data else []
    
    def get_repository_readme(self, repo_name: str) -> Optional[str]:
        """Get README content for a repository."""
        endpoint = f"repos/{self.github_username}/{repo_name}/readme"
        data = self.make_api_request(endpoint)
        if data and 'content' in data:
            import base64
            try:
                return base64.b64decode(data['content']).decode('utf-8')
            except:
                return None
        return None
    
    def get_repository_files(self, repo_name: str, path: str = "") -> List[Dict]:
        """Get file listing for a repository."""
        endpoint = f"repos/{self.github_username}/{repo_name}/contents/{path}"
        return self.make_api_request(endpoint) or []
    
    def analyze_repository(self, repo_data: Dict) -> Dict[str, Any]:
        """Analyze a single repository using API data."""
        repo_name = repo_data['name']
        
        analysis = {
            'name': repo_name,
            'full_name': repo_data['full_name'],
            'description': repo_data.get('description', ''),
            'html_url': repo_data['html_url'],
            'created_at': repo_data['created_at'],
            'updated_at': repo_data['updated_at'],
            'pushed_at': repo_data['pushed_at'],
            'size': repo_data['size'],
            'stargazers_count': repo_data['stargazers_count'],
            'forks_count': repo_data['forks_count'],
            'language': repo_data.get('language'),
            'has_issues': repo_data['has_issues'],
            'has_projects': repo_data['has_projects'],
            'has_downloads': repo_data['has_downloads'],
            'has_wiki': repo_data['has_wiki'],
            'has_pages': repo_data['has_pages'],
            'has_discussions': repo_data['has_discussions'],
            'fork': repo_data['fork'],
            'archived': repo_data['archived'],
            'disabled': repo_data['disabled'],
            'license': repo_data.get('license'),
            'allow_forking': repo_data['allow_forking'],
            'is_template': repo_data['is_template'],
            'web_commit_signoff_required': repo_data['web_commit_signoff_required'],
            'default_branch': repo_data['default_branch'],
            'permissions': repo_data.get('permissions', {}),
            'visibility': repo_data['visibility'],
            'analysis': {
                'languages': {},
                'topics': [],
                'readme_content': None,
                'file_structure': {},
                'technology_stack': [],
                'key_features': [],
                'development_stage': 'Unknown',
                'monetization_potential': 'Low',
                'business_value': 'Low',
                'project_category': 'General Development',
                'skill_domains': []
            }
        }
        
        # Get additional data
        print(f"   📊 Analyzing {repo_name}...")
        
        # Get languages
        languages = self.get_repository_languages(repo_name)
        analysis['analysis']['languages'] = languages
        
        # Get topics
        topics = self.get_repository_topics(repo_name)
        analysis['analysis']['topics'] = topics
        
        # Get README
        readme = self.get_repository_readme(repo_name)
        analysis['analysis']['readme_content'] = readme
        
        # Get file structure (root level)
        files = self.get_repository_files(repo_name)
        analysis['analysis']['file_structure'] = self.analyze_file_structure(files)
        
        # Analyze based on available data
        self.analyze_repository_characteristics(repo_name, analysis)
        
        return analysis
    
    def analyze_file_structure(self, files: List[Dict]) -> Dict[str, Any]:
        """Analyze file structure from API data."""
        structure = {
            'total_files': len(files),
            'file_types': defaultdict(int),
            'key_files': [],
            'has_config_files': False,
            'has_docs': False,
            'has_tests': False,
            'has_docker': False,
            'has_ci_cd': False
        }
        
        for file in files:
            if not isinstance(file, dict):
                continue
                
            filename = file.get('name', '').lower()
            file_type = file.get('type', 'file')
            
            if file_type == 'file':
                language = file.get('language', 'Unknown')
                structure['file_types'][language] += 1
                
                # Check for key files
                if filename in ['readme.md', 'readme.txt', 'readme']:
                    structure['key_files'].append('README')
                elif filename in ['requirements.txt', 'package.json', 'pom.xml', 'build.gradle']:
                    structure['key_files'].append('Dependencies')
                    structure['has_config_files'] = True
                elif filename in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
                    structure['key_files'].append('Docker')
                    structure['has_docker'] = True
                elif filename in ['.github/workflows', '.travis.yml', '.gitlab-ci.yml']:
                    structure['key_files'].append('CI/CD')
                    structure['has_ci_cd'] = True
                elif 'test' in filename or 'spec' in filename:
                    structure['key_files'].append('Tests')
                    structure['has_tests'] = True
                elif filename in ['docs', 'documentation', 'wiki']:
                    structure['key_files'].append('Documentation')
                    structure['has_docs'] = True
        
        return dict(structure)
    
    def analyze_repository_characteristics(self, repo_name: str, analysis: Dict):
        """Analyze repository characteristics based on available data."""
        name_lower = repo_name.lower()
        description = (analysis.get('description') or '').lower()
        topics = [topic.lower() for topic in analysis['analysis']['topics']]
        languages = list(analysis['analysis']['languages'].keys())
        file_structure = analysis['analysis']['file_structure']
        
        # Technology stack detection
        tech_stack = []
        if 'python' in languages:
            tech_stack.append('Python')
        if 'javascript' in languages:
            tech_stack.append('JavaScript')
        if 'typescript' in languages:
            tech_stack.append('TypeScript')
        if 'java' in languages:
            tech_stack.append('Java')
        if 'go' in languages:
            tech_stack.append('Go')
        if 'rust' in languages:
            tech_stack.append('Rust')
        
        # Framework detection from topics and description
        if any(term in topics or term in description for term in ['django', 'flask', 'fastapi']):
            tech_stack.append('Python Web Framework')
        if any(term in topics or term in description for term in ['react', 'vue', 'angular']):
            tech_stack.append('Frontend Framework')
        if any(term in topics or term in description for term in ['docker', 'kubernetes']):
            tech_stack.append('Containerization')
        if any(term in topics or term in description for term in ['aws', 'azure', 'gcp']):
            tech_stack.append('Cloud Platform')
        
        analysis['analysis']['technology_stack'] = tech_stack
        
        # Key features detection
        features = []
        if file_structure['has_docker']:
            features.append('Containerization')
        if file_structure['has_ci_cd']:
            features.append('CI/CD Pipeline')
        if file_structure['has_tests']:
            features.append('Testing')
        if file_structure['has_docs']:
            features.append('Documentation')
        if file_structure['has_config_files']:
            features.append('Dependency Management')
        
        # Detect features from topics and description
        if any(term in topics or term in description for term in ['api', 'rest', 'graphql']):
            features.append('API Development')
        if any(term in topics or term in description for term in ['auth', 'authentication', 'oauth']):
            features.append('User Authentication')
        if any(term in topics or term in description for term in ['database', 'sql', 'mongodb']):
            features.append('Database Integration')
        if any(term in topics or term in description for term in ['trading', 'finance', 'stock']):
            features.append('Financial/Trading')
        if any(term in topics or term in description for term in ['ai', 'ml', 'machine-learning']):
            features.append('AI/ML')
        if any(term in topics or term in description for term in ['bot', 'automation']):
            features.append('Automation')
        
        analysis['analysis']['key_features'] = features
        
        # Development stage assessment
        total_files = file_structure['total_files']
        if total_files < 10:
            analysis['analysis']['development_stage'] = 'Prototype'
        elif total_files < 50:
            analysis['analysis']['development_stage'] = 'Development'
        elif total_files < 200:
            analysis['analysis']['development_stage'] = 'Mature'
        else:
            analysis['analysis']['development_stage'] = 'Enterprise'
        
        # Monetization potential
        if any(term in name_lower for term in ['trading', 'finance', 'saas', 'platform']):
            analysis['analysis']['monetization_potential'] = 'High'
        elif 'AI/ML' in tech_stack or any(term in topics for term in ['ai', 'ml', 'machine-learning']):
            analysis['analysis']['monetization_potential'] = 'High'
        elif any(term in name_lower for term in ['tool', 'automation', 'productivity']):
            analysis['analysis']['monetization_potential'] = 'Medium'
        else:
            analysis['analysis']['monetization_potential'] = 'Low'
        
        # Business value
        monetization = analysis['analysis']['monetization_potential']
        if monetization == 'High' and total_files > 20:
            analysis['analysis']['business_value'] = 'High'
        elif monetization == 'Medium' and total_files > 10:
            analysis['analysis']['business_value'] = 'Medium'
        else:
            analysis['analysis']['business_value'] = 'Low'
        
        # Skill domains
        skill_domains = []
        if 'AI/ML' in tech_stack or any(term in topics for term in ['ai', 'ml', 'machine-learning']):
            skill_domains.append('AI/Machine Learning')
        if 'Frontend Framework' in tech_stack:
            skill_domains.append('Frontend Development')
        if 'Python Web Framework' in tech_stack:
            skill_domains.append('Backend Development')
        if 'Containerization' in tech_stack:
            skill_domains.append('DevOps/Infrastructure')
        if 'Cloud Platform' in tech_stack:
            skill_domains.append('Cloud Computing')
        if 'Financial/Trading' in features:
            skill_domains.append('Financial Technology')
        if 'Automation' in features:
            skill_domains.append('Process Automation')
        
        analysis['analysis']['skill_domains'] = skill_domains
        
        # Project category
        if any(term in name_lower for term in ['trading', 'stock', 'finance', 'robot', 'plug']):
            analysis['analysis']['project_category'] = 'Trading/Finance'
        elif any(term in name_lower for term in ['ai', 'ml', 'neural', 'model', 'gpt']):
            analysis['analysis']['project_category'] = 'AI/Machine Learning'
        elif any(term in name_lower for term in ['web', 'app', 'site', 'blog']):
            analysis['analysis']['project_category'] = 'Web Application'
        elif any(term in name_lower for term in ['bot', 'automation', 'script', 'tool']):
            analysis['analysis']['project_category'] = 'Automation Tool'
        elif any(term in name_lower for term in ['deploy', 'docker', 'kubernetes', 'infra']):
            analysis['analysis']['project_category'] = 'Infrastructure/DevOps'
        elif any(term in name_lower for term in ['lib', 'framework', 'sdk', 'api']):
            analysis['analysis']['project_category'] = 'Library/Framework'
        elif any(term in name_lower for term in ['game', 'sims', 'ttrpg', 'entertainment']):
            analysis['analysis']['project_category'] = 'Games/Entertainment'
        elif any(term in name_lower for term in ['productivity', 'focus', 'dream', 'organizer']):
            analysis['analysis']['project_category'] = 'Productivity Tool'
        else:
            analysis['analysis']['project_category'] = 'General Development'
    
    def analyze_all_repositories(self) -> Dict[str, Any]:
        """Analyze all repositories using GitHub API."""
        print("🔍 Analyzing all repositories using GitHub API...")
        
        # Get repository list
        repos = self.get_repository_list()
        print(f"📁 Found {len(repos)} repositories to analyze")
        
        successful_analyses = 0
        failed_analyses = 0
        
        for i, repo_data in enumerate(repos, 1):
            repo_name = repo_data['name']
            print(f"\n📦 Analyzing {i}/{len(repos)}: {repo_name}")
            
            try:
                analysis = self.analyze_repository(repo_data)
                self.analysis_results[repo_name] = analysis
                successful_analyses += 1
                print(f"   ✅ Successfully analyzed {repo_name}")
                
            except Exception as e:
                print(f"   ❌ Failed to analyze {repo_name}: {e}")
                failed_analyses += 1
                continue
        
        print(f"\n✅ Analysis complete! Successful: {successful_analyses}, Failed: {failed_analyses}")
        
        # Generate portfolio context
        self.generate_portfolio_context()
        
        # Save results
        self.save_analysis_results()
        
        return self.analysis_results
    
    def generate_portfolio_context(self):
        """Generate portfolio-level context."""
        self.portfolio_context = {
            'total_repositories': len(self.analysis_results),
            'total_size': sum(repo['size'] for repo in self.analysis_results.values()),
            'total_stars': sum(repo['stargazers_count'] for repo in self.analysis_results.values()),
            'total_forks': sum(repo['forks_count'] for repo in self.analysis_results.values()),
            'project_categories': defaultdict(list),
            'technology_ecosystem': defaultdict(Counter),
            'skill_domains': defaultdict(list),
            'business_opportunities': defaultdict(list),
            'development_stages': defaultdict(list),
            'top_languages': Counter(),
            'top_topics': Counter()
        }
        
        for repo_name, repo_data in self.analysis_results.items():
            # Categorize projects
            category = repo_data['analysis']['project_category']
            self.portfolio_context['project_categories'][category].append(repo_name)
            
            # Technology ecosystem
            for tech in repo_data['analysis']['technology_stack']:
                self.portfolio_context['technology_ecosystem']['technologies'][tech] += 1
            
            for lang, bytes_count in repo_data['analysis']['languages'].items():
                # Ensure bytes_count is an integer
                try:
                    bytes_count = int(bytes_count)
                    self.portfolio_context['technology_ecosystem']['languages'][lang] += bytes_count
                    self.portfolio_context['top_languages'][lang] += bytes_count
                except (ValueError, TypeError):
                    # If bytes_count is not a number, just count occurrences
                    self.portfolio_context['technology_ecosystem']['languages'][lang] += 1
                    self.portfolio_context['top_languages'][lang] += 1
            
            # Topics
            for topic in repo_data['analysis']['topics']:
                self.portfolio_context['top_topics'][topic] += 1
            
            # Skill domains
            for domain in repo_data['analysis']['skill_domains']:
                self.portfolio_context['skill_domains'][domain].append(repo_name)
            
            # Business opportunities
            monetization = repo_data['analysis']['monetization_potential']
            self.portfolio_context['business_opportunities'][monetization].append(repo_name)
            
            # Development stages
            stage = repo_data['analysis']['development_stage']
            self.portfolio_context['development_stages'][stage].append(repo_name)
    
    def save_analysis_results(self):
        """Save analysis results to files."""
        output_dir = Path("github_api_analysis")
        output_dir.mkdir(exist_ok=True)
        
        # Save detailed analysis results
        with open(output_dir / "detailed_analysis_results.json", 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        # Save portfolio context
        portfolio_data = {
            'portfolio_context': dict(self.portfolio_context),
            'analysis_timestamp': self.get_timestamp(),
            'total_repositories': len(self.analysis_results)
        }
        
        with open(output_dir / "portfolio_context.json", 'w') as f:
            json.dump(portfolio_data, f, indent=2)
        
        print(f"✅ Analysis results saved to {output_dir}/")
    
    def get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def generate_llm_context_for_project(self, repo_name: str) -> Dict[str, Any]:
        """Generate LLM context for a specific project."""
        if repo_name not in self.analysis_results:
            return {"error": f"Repository {repo_name} not found in analysis results"}
        
        repo_data = self.analysis_results[repo_name]
        
        # Generate natural language description
        description = self.generate_project_description(repo_name, repo_data)
        
        return {
            'project_overview': {
                'name': repo_name,
                'description': description,
                'github_url': repo_data['html_url'],
                'created_at': repo_data['created_at'],
                'updated_at': repo_data['updated_at'],
                'stars': repo_data['stargazers_count'],
                'forks': repo_data['forks_count'],
                'size': repo_data['size'],
                'development_stage': repo_data['analysis']['development_stage'],
                'business_value': repo_data['analysis']['business_value'],
                'monetization_potential': repo_data['analysis']['monetization_potential']
            },
            'technical_context': {
                'primary_language': repo_data['language'],
                'languages': repo_data['analysis']['languages'],
                'technologies': repo_data['analysis']['technology_stack'],
                'key_features': repo_data['analysis']['key_features'],
                'file_structure': repo_data['analysis']['file_structure'],
                'topics': repo_data['analysis']['topics']
            },
            'portfolio_context': {
                'category': repo_data['analysis']['project_category'],
                'skill_domains': repo_data['analysis']['skill_domains'],
                'similar_projects': self.find_similar_projects(repo_name, repo_data),
                'portfolio_position': self.assess_portfolio_position(repo_name, repo_data)
            },
            'business_context': {
                'market_opportunity': self.assess_market_opportunity(repo_data),
                'competitive_advantages': self.identify_competitive_advantages(repo_data),
                'development_priorities': self.suggest_development_priorities(repo_data)
            }
        }
    
    def generate_project_description(self, repo_name: str, repo_data: Dict) -> str:
        """Generate a natural language description of the project."""
        description = repo_data.get('description', '')
        if not description:
            description = f"{repo_name} is a software project"
        
        # Add technology information
        languages = list(repo_data['analysis']['languages'].keys())
        if languages:
            primary_lang = languages[0]
            description += f" built with {primary_lang}"
        
        # Add size information
        size = repo_data['size']
        if size > 1000:
            description += f". It's a substantial project ({size} KB)"
        elif size > 100:
            description += f". It's a medium-sized project ({size} KB)"
        else:
            description += f". It's a focused project ({size} KB)"
        
        # Add key features
        features = repo_data['analysis']['key_features']
        if features:
            feature_list = ', '.join(features[:3])
            description += f" featuring {feature_list}"
        
        description += "."
        return description
    
    def find_similar_projects(self, repo_name: str, repo_data: Dict) -> List[Dict]:
        """Find similar projects in the portfolio."""
        similar = []
        current_technologies = set(repo_data['analysis']['technology_stack'])
        current_domains = set(repo_data['analysis']['skill_domains'])
        current_topics = set(repo_data['analysis']['topics'])
        
        for other_repo, other_data in self.analysis_results.items():
            if other_repo == repo_name:
                continue
            
            other_technologies = set(other_data['analysis']['technology_stack'])
            other_domains = set(other_data['analysis']['skill_domains'])
            other_topics = set(other_data['analysis']['topics'])
            
            # Calculate similarity score
            tech_overlap = len(current_technologies & other_technologies)
            domain_overlap = len(current_domains & other_domains)
            topic_overlap = len(current_topics & other_topics)
            
            similarity_score = tech_overlap + domain_overlap + topic_overlap
            
            if similarity_score > 0:
                similar.append({
                    'name': other_repo,
                    'similarity_score': similarity_score,
                    'shared_technologies': list(current_technologies & other_technologies),
                    'shared_domains': list(current_domains & other_domains),
                    'shared_topics': list(current_topics & other_topics)
                })
        
        # Sort by similarity score and return top 5
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar[:5]
    
    def assess_portfolio_position(self, repo_name: str, repo_data: Dict) -> Dict[str, Any]:
        """Assess the project's position within the portfolio."""
        category = repo_data['analysis']['project_category']
        category_projects = self.portfolio_context['project_categories'].get(category, [])
        
        return {
            'category': category,
            'category_size': len(category_projects),
            'category_rank': category_projects.index(repo_name) + 1 if repo_name in category_projects else 0,
            'portfolio_percentage': len(category_projects) / len(self.analysis_results) * 100
        }
    
    def assess_market_opportunity(self, repo_data: Dict) -> Dict[str, Any]:
        """Assess market opportunity for the project."""
        monetization = repo_data['analysis']['monetization_potential']
        business_value = repo_data['analysis']['business_value']
        technologies = repo_data['analysis']['technology_stack']
        stars = repo_data['stargazers_count']
        
        opportunity = {
            'level': 'Low',
            'factors': [],
            'recommendations': []
        }
        
        if monetization == 'High' and business_value == 'High':
            opportunity['level'] = 'High'
            opportunity['factors'].append('High monetization potential')
            opportunity['factors'].append('Strong business value')
            opportunity['recommendations'].append('Prioritize for commercialization')
        
        if stars > 10:
            opportunity['factors'].append(f'Community interest ({stars} stars)')
            opportunity['recommendations'].append('Leverage community engagement')
        
        if 'AI/ML' in technologies:
            opportunity['factors'].append('AI/ML technology stack')
            opportunity['recommendations'].append('Leverage AI capabilities for competitive advantage')
        
        if 'Financial/Trading' in repo_data['analysis']['key_features']:
            opportunity['factors'].append('Financial technology domain')
            opportunity['recommendations'].append('Target fintech market opportunities')
        
        return opportunity
    
    def identify_competitive_advantages(self, repo_data: Dict) -> List[str]:
        """Identify competitive advantages of the project."""
        advantages = []
        technologies = repo_data['analysis']['technology_stack']
        features = repo_data['analysis']['key_features']
        topics = repo_data['analysis']['topics']
        
        if 'AI/ML' in technologies:
            advantages.append('AI-powered functionality')
        
        if 'Financial/Trading' in features:
            advantages.append('Domain expertise in financial technology')
        
        if 'Automation' in features:
            advantages.append('Process automation capabilities')
        
        if 'API Development' in features:
            advantages.append('API-first architecture')
        
        if 'User Authentication' in features:
            advantages.append('User management system')
        
        if repo_data['stargazers_count'] > 5:
            advantages.append('Community validation')
        
        if repo_data['forks_count'] > 0:
            advantages.append('Community adoption')
        
        return advantages
    
    def suggest_development_priorities(self, repo_data: Dict) -> List[str]:
        """Suggest development priorities for the project."""
        priorities = []
        development_stage = repo_data['analysis']['development_stage']
        features = repo_data['analysis']['key_features']
        topics = repo_data['analysis']['topics']
        
        if development_stage == 'Prototype':
            priorities.append('Core functionality development')
            priorities.append('Basic user interface')
            priorities.append('Essential features implementation')
        
        elif development_stage == 'Development':
            priorities.append('Feature completeness')
            priorities.append('User experience improvements')
            priorities.append('Testing and quality assurance')
        
        elif development_stage == 'Mature':
            priorities.append('Performance optimization')
            priorities.append('Scalability improvements')
            priorities.append('Advanced features')
        
        elif development_stage == 'Enterprise':
            priorities.append('Enterprise features')
            priorities.append('Security hardening')
            priorities.append('Integration capabilities')
        
        # Add specific priorities based on missing features
        if 'Testing' not in features:
            priorities.append('Add comprehensive testing')
        
        if 'Documentation' not in features:
            priorities.append('Add comprehensive documentation')
        
        if 'CI/CD Pipeline' not in features:
            priorities.append('Implement CI/CD pipeline')
        
        if repo_data['stargazers_count'] == 0:
            priorities.append('Build community engagement')
        
        return priorities


def main():
    """Main function to run the GitHub API analyzer."""
    analyzer = GitHubAPIAnalyzer()
    
    # Analyze all repositories
    analysis_results = analyzer.analyze_all_repositories()
    
    print(f"\n🎯 GitHub API Analysis Complete!")
    print(f"📊 Analyzed {len(analysis_results)} repositories")
    print(f"📁 Results saved to github_api_analysis/")
    
    # Example: Generate context for a specific project
    if analysis_results:
        example_project = list(analysis_results.keys())[0]
        context = analyzer.generate_llm_context_for_project(example_project)
        print(f"\n📋 Example context for {example_project}:")
        print(f"   Description: {context['project_overview']['description']}")
        print(f"   Technologies: {', '.join(context['technical_context']['technologies'])}")
        print(f"   Category: {context['portfolio_context']['category']}")


if __name__ == "__main__":
    main() 