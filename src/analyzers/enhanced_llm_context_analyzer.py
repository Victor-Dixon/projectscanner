#!/usr/bin/env python3
"""
Enhanced LLM Context Analyzer
Provides comprehensive context for LLMs to understand projects and portfolio
"""

import json
import os
import re
import ast
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from pathlib import Path

class EnhancedLLMContextAnalyzer:
    """Provides rich context for LLMs to understand projects and portfolio."""
    
    def __init__(self, library_path: str = "github_library_enhanced/github_library_enhanced.json"):
        self.library_path = library_path
        self.library_data = self.load_library()
        self.portfolio_context = self.analyze_portfolio_context()
        
    def load_library(self) -> Dict:
        """Load the scanned library data."""
        try:
            with open(self.library_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Library file not found: {self.library_path}")
            return {}
    
    def analyze_portfolio_context(self) -> Dict[str, Any]:
        """Analyze the entire portfolio for context."""
        context = {
            'portfolio_overview': {},
            'technology_ecosystem': defaultdict(Counter),
            'project_categories': defaultdict(list),
            'development_patterns': defaultdict(Counter),
            'skill_domains': defaultdict(list),
            'business_opportunities': defaultdict(list),
            'code_quality_metrics': defaultdict(list),
            'inter_project_dependencies': defaultdict(list)
        }
        
        total_repos = len(self.library_data)
        total_files = 0
        total_complexity = 0
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                file_count = len(files)
                total_files += file_count
                
                # Analyze project context
                project_context = self.analyze_single_project_context(repo_name, files)
                
                # Categorize project
                category = self.categorize_project_for_context(repo_name, project_context)
                context['project_categories'][category].append(repo_name)
                
                # Technology ecosystem
                for tech in project_context.get('technologies', []):
                    context['technology_ecosystem']['technologies'][tech] += 1
                
                for lang in project_context.get('languages', []):
                    context['technology_ecosystem']['languages'][lang] += 1
                
                # Skill domains
                for domain in project_context.get('skill_domains', []):
                    context['skill_domains'][domain].append(repo_name)
                
                # Business opportunities
                if project_context.get('monetization_potential'):
                    context['business_opportunities'][project_context['monetization_potential']].append(repo_name)
                
                # Code quality
                complexity = project_context.get('avg_complexity', 0)
                total_complexity += complexity
                context['code_quality_metrics']['complexity'].append({
                    'repo': repo_name,
                    'complexity': complexity,
                    'file_count': file_count
                })
        
        # Portfolio overview
        context['portfolio_overview'] = {
            'total_repositories': total_repos,
            'total_files': total_files,
            'avg_complexity': total_complexity / total_repos if total_repos > 0 else 0,
            'primary_language': self.get_most_common(context['technology_ecosystem']['languages']),
            'primary_technology': self.get_most_common(context['technology_ecosystem']['technologies'])
        }
        
        return context
    
    def analyze_single_project_context(self, repo_name: str, files: Dict) -> Dict[str, Any]:
        """Analyze a single project for rich context."""
        context = {
            'name': repo_name,
            'file_count': len(files),
            'languages': set(),
            'technologies': set(),
            'skill_domains': set(),
            'complexity_metrics': [],
            'architecture_patterns': set(),
            'monetization_potential': None,
            'development_stage': None,
            'key_features': [],
            'dependencies': set(),
            'business_value': None
        }
        
        total_complexity = 0
        file_complexities = []
        
        for file_path, file_data in files.items():
            # Language detection
            if 'language' in file_data and file_data['language']:
                context['languages'].add(file_data['language'])
            
            # Technology detection
            self.detect_technologies_from_file(file_path, file_data, context)
            
            # Complexity analysis
            complexity = file_data.get('complexity', 0)
            total_complexity += complexity
            file_complexities.append(complexity)
            
            # Architecture patterns
            self.detect_architecture_patterns(file_path, file_data, context)
            
            # Key features
            self.extract_key_features(file_path, file_data, context)
        
        # Calculate metrics
        if file_complexities:
            context['avg_complexity'] = sum(file_complexities) / len(file_complexities)
            context['max_complexity'] = max(file_complexities)
            context['complexity_metrics'] = file_complexities
        
        # Determine project characteristics
        context['development_stage'] = self.assess_development_stage(context)
        context['monetization_potential'] = self.assess_monetization_potential(context)
        context['business_value'] = self.assess_business_value(context)
        context['skill_domains'] = self.determine_skill_domains(context)
        
        # Convert sets to lists for JSON serialization
        context['languages'] = list(context['languages'])
        context['technologies'] = list(context['technologies'])
        context['skill_domains'] = list(context['skill_domains'])
        context['architecture_patterns'] = list(context['architecture_patterns'])
        context['dependencies'] = list(context['dependencies'])
        
        return context
    
    def detect_technologies_from_file(self, file_path: str, file_data: Dict, context: Dict):
        """Detect technologies from file path and content."""
        path_lower = file_path.lower()
        
        # Framework detection
        if 'django' in path_lower or 'django' in str(file_data):
            context['technologies'].add('Django')
        if 'flask' in path_lower or 'flask' in str(file_data):
            context['technologies'].add('Flask')
        if 'fastapi' in path_lower or 'fastapi' in str(file_data):
            context['technologies'].add('FastAPI')
        if 'react' in path_lower or 'vue' in path_lower or 'angular' in path_lower:
            context['technologies'].add('Frontend Framework')
        if 'docker' in path_lower or 'dockerfile' in path_lower:
            context['technologies'].add('Docker')
        if 'kubernetes' in path_lower or 'k8s' in path_lower:
            context['technologies'].add('Kubernetes')
        if 'aws' in path_lower or 's3' in path_lower or 'lambda' in path_lower:
            context['technologies'].add('AWS')
        if 'azure' in path_lower or 'gcp' in path_lower:
            context['technologies'].add('Cloud Platform')
        
        # Database detection
        if 'sql' in path_lower or 'postgres' in path_lower or 'mysql' in path_lower:
            context['technologies'].add('Database')
        if 'redis' in path_lower or 'mongodb' in path_lower:
            context['technologies'].add('NoSQL Database')
        
        # AI/ML detection
        if 'tensorflow' in path_lower or 'pytorch' in path_lower or 'sklearn' in path_lower:
            context['technologies'].add('Machine Learning')
        if 'openai' in path_lower or 'gpt' in path_lower or 'llm' in path_lower:
            context['technologies'].add('AI/LLM')
    
    def detect_architecture_patterns(self, file_path: str, file_data: Dict, context: Dict):
        """Detect architecture patterns from file structure and content."""
        path_lower = file_path.lower()
        
        # MVC pattern
        if any(term in path_lower for term in ['models', 'views', 'controllers']):
            context['architecture_patterns'].add('MVC')
        
        # Microservices
        if 'service' in path_lower or 'api' in path_lower:
            context['architecture_patterns'].add('Microservices')
        
        # Event-driven
        if 'event' in path_lower or 'queue' in path_lower or 'kafka' in path_lower:
            context['architecture_patterns'].add('Event-Driven')
        
        # Repository pattern
        if 'repository' in path_lower or 'repo' in path_lower:
            context['architecture_patterns'].add('Repository Pattern')
        
        # Clean Architecture
        if any(term in path_lower for term in ['domain', 'application', 'infrastructure']):
            context['architecture_patterns'].add('Clean Architecture')
    
    def extract_key_features(self, file_path: str, file_data: Dict, context: Dict):
        """Extract key features from file content."""
        content = str(file_data.get('content', ''))
        content_lower = content.lower()
        
        # Feature detection based on keywords
        features = []
        
        if any(term in content_lower for term in ['authentication', 'login', 'auth']):
            features.append('User Authentication')
        if any(term in content_lower for term in ['api', 'endpoint', 'route']):
            features.append('API Endpoints')
        if any(term in content_lower for term in ['database', 'model', 'schema']):
            features.append('Database Integration')
        if any(term in content_lower for term in ['ui', 'interface', 'frontend']):
            features.append('User Interface')
        if any(term in content_lower for term in ['test', 'spec', 'mock']):
            features.append('Testing')
        if any(term in content_lower for term in ['deploy', 'docker', 'ci/cd']):
            features.append('Deployment')
        if any(term in content_lower for term in ['trading', 'finance', 'stock']):
            features.append('Financial/Trading')
        if any(term in content_lower for term in ['ai', 'ml', 'neural', 'model']):
            features.append('AI/ML')
        if any(term in content_lower for term in ['automation', 'bot', 'script']):
            features.append('Automation')
        
        context['key_features'].extend(features)
    
    def categorize_project_for_context(self, repo_name: str, context: Dict) -> str:
        """Categorize project for better context understanding."""
        name_lower = repo_name.lower()
        technologies = context.get('technologies', [])
        skill_domains = context.get('skill_domains', [])
        
        # Trading/Finance projects
        if any(term in name_lower for term in ['trading', 'stock', 'finance', 'robot', 'plug']):
            return 'Trading/Finance'
        
        # AI/ML projects
        if any(term in name_lower for term in ['ai', 'ml', 'neural', 'model', 'gpt']):
            return 'AI/Machine Learning'
        
        # Web applications
        if any(term in name_lower for term in ['web', 'app', 'site', 'blog']):
            return 'Web Application'
        
        # Automation tools
        if any(term in name_lower for term in ['bot', 'automation', 'script', 'tool']):
            return 'Automation Tool'
        
        # Infrastructure/DevOps
        if any(term in name_lower for term in ['deploy', 'docker', 'kubernetes', 'infra']):
            return 'Infrastructure/DevOps'
        
        # Libraries/Frameworks
        if any(term in name_lower for term in ['lib', 'framework', 'sdk', 'api']):
            return 'Library/Framework'
        
        # Games/Entertainment
        if any(term in name_lower for term in ['game', 'sims', 'ttrpg', 'entertainment']):
            return 'Games/Entertainment'
        
        # Productivity tools
        if any(term in name_lower for term in ['productivity', 'focus', 'dream', 'organizer']):
            return 'Productivity Tool'
        
        return 'General Development'
    
    def assess_development_stage(self, context: Dict) -> str:
        """Assess the development stage of a project."""
        file_count = context.get('file_count', 0)
        complexity = context.get('avg_complexity', 0)
        features = context.get('key_features', [])
        
        if file_count < 10:
            return 'Prototype'
        elif file_count < 50:
            return 'Development'
        elif file_count < 200:
            return 'Mature'
        else:
            return 'Enterprise'
    
    def assess_monetization_potential(self, context: Dict) -> str:
        """Assess monetization potential of a project."""
        name_lower = context.get('name', '').lower()
        technologies = context.get('technologies', [])
        features = context.get('key_features', [])
        
        # High potential indicators
        if any(term in name_lower for term in ['trading', 'finance', 'saas', 'platform']):
            return 'High'
        if 'AI/LLM' in technologies or 'Machine Learning' in technologies:
            return 'High'
        if 'API Endpoints' in features and 'User Authentication' in features:
            return 'High'
        
        # Medium potential indicators
        if any(term in name_lower for term in ['tool', 'automation', 'productivity']):
            return 'Medium'
        if 'Web Application' in context.get('skill_domains', []):
            return 'Medium'
        
        return 'Low'
    
    def assess_business_value(self, context: Dict) -> str:
        """Assess the business value of a project."""
        monetization = context.get('monetization_potential', 'Low')
        file_count = context.get('file_count', 0)
        complexity = context.get('avg_complexity', 0)
        
        if monetization == 'High' and file_count > 50:
            return 'High'
        elif monetization == 'Medium' and file_count > 20:
            return 'Medium'
        else:
            return 'Low'
    
    def determine_skill_domains(self, context: Dict) -> List[str]:
        """Determine skill domains demonstrated by the project."""
        domains = set()
        technologies = context.get('technologies', [])
        features = context.get('key_features', [])
        
        if 'Machine Learning' in technologies or 'AI/LLM' in technologies:
            domains.add('AI/Machine Learning')
        
        if 'Frontend Framework' in technologies or 'User Interface' in features:
            domains.add('Frontend Development')
        
        if 'Django' in technologies or 'Flask' in technologies or 'FastAPI' in technologies:
            domains.add('Backend Development')
        
        if 'Database' in technologies or 'NoSQL Database' in technologies:
            domains.add('Database Design')
        
        if 'Docker' in technologies or 'Kubernetes' in technologies:
            domains.add('DevOps/Infrastructure')
        
        if 'AWS' in technologies or 'Cloud Platform' in technologies:
            domains.add('Cloud Computing')
        
        if 'Financial/Trading' in features:
            domains.add('Financial Technology')
        
        if 'Automation' in features:
            domains.add('Process Automation')
        
        return list(domains)
    
    def get_most_common(self, counter: Counter) -> str:
        """Get the most common item from a counter."""
        if counter:
            return counter.most_common(1)[0][0]
        return "Unknown"
    
    def generate_project_context_for_llm(self, repo_name: str) -> Dict[str, Any]:
        """Generate comprehensive context for a specific project."""
        if repo_name not in self.library_data:
            return {"error": f"Repository {repo_name} not found"}
        
        repo_data = self.library_data[repo_name]
        if 'files' not in repo_data:
            return {"error": f"No file data for {repo_name}"}
        
        # Analyze the specific project
        project_context = self.analyze_single_project_context(repo_name, repo_data['files'])
        
        # Generate LLM context
        llm_context = {
            'project_overview': {
                'name': repo_name,
                'description': self.generate_project_description(repo_name, project_context),
                'development_stage': project_context['development_stage'],
                'business_value': project_context['business_value'],
                'monetization_potential': project_context['monetization_potential']
            },
            'technical_context': {
                'languages': project_context['languages'],
                'technologies': project_context['technologies'],
                'architecture_patterns': project_context['architecture_patterns'],
                'key_features': list(set(project_context['key_features'])),
                'complexity_metrics': {
                    'avg_complexity': project_context.get('avg_complexity', 0),
                    'max_complexity': project_context.get('max_complexity', 0),
                    'file_count': project_context['file_count']
                }
            },
            'portfolio_context': {
                'category': self.categorize_project_for_context(repo_name, project_context),
                'skill_domains': project_context['skill_domains'],
                'similar_projects': self.find_similar_projects(repo_name, project_context),
                'portfolio_position': self.assess_portfolio_position(repo_name, project_context)
            },
            'business_context': {
                'market_opportunity': self.assess_market_opportunity(project_context),
                'competitive_advantages': self.identify_competitive_advantages(project_context),
                'development_priorities': self.suggest_development_priorities(project_context)
            }
        }
        
        return llm_context
    
    def generate_project_description(self, repo_name: str, context: Dict) -> str:
        """Generate a natural language description of the project."""
        name_lower = repo_name.lower()
        technologies = context.get('technologies', [])
        features = context.get('key_features', [])
        file_count = context.get('file_count', 0)
        
        description = f"{repo_name} is a "
        
        # Determine project type
        if 'Trading/Finance' in context.get('skill_domains', []):
            description += "financial trading application"
        elif 'AI/Machine Learning' in context.get('skill_domains', []):
            description += "AI/ML-powered application"
        elif 'Web Application' in context.get('skill_domains', []):
            description += "web application"
        elif 'Automation Tool' in context.get('skill_domains', []):
            description += "automation tool"
        else:
            description += "software project"
        
        # Add technology stack
        if technologies:
            tech_list = ', '.join(technologies[:3])  # Top 3 technologies
            description += f" built with {tech_list}"
        
        # Add scale information
        if file_count > 100:
            description += f". It's a substantial project with {file_count} files"
        elif file_count > 50:
            description += f". It's a medium-sized project with {file_count} files"
        else:
            description += f". It's a focused project with {file_count} files"
        
        # Add key features
        if features:
            feature_list = ', '.join(features[:3])  # Top 3 features
            description += f" featuring {feature_list}"
        
        description += "."
        
        return description
    
    def find_similar_projects(self, repo_name: str, context: Dict) -> List[str]:
        """Find similar projects in the portfolio."""
        similar = []
        current_technologies = set(context.get('technologies', []))
        current_domains = set(context.get('skill_domains', []))
        
        for other_repo, other_data in self.library_data.items():
            if other_repo == repo_name:
                continue
            
            if 'files' not in other_data:
                continue
            
            other_context = self.analyze_single_project_context(other_repo, other_data['files'])
            other_technologies = set(other_context.get('technologies', []))
            other_domains = set(other_context.get('skill_domains', []))
            
            # Calculate similarity score
            tech_overlap = len(current_technologies & other_technologies)
            domain_overlap = len(current_domains & other_domains)
            
            if tech_overlap > 0 or domain_overlap > 0:
                similar.append({
                    'name': other_repo,
                    'similarity_score': tech_overlap + domain_overlap,
                    'shared_technologies': list(current_technologies & other_technologies),
                    'shared_domains': list(current_domains & other_domains)
                })
        
        # Sort by similarity score and return top 5
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar[:5]
    
    def assess_portfolio_position(self, repo_name: str, context: Dict) -> Dict[str, Any]:
        """Assess the project's position within the portfolio."""
        category = self.categorize_project_for_context(repo_name, context)
        category_projects = self.portfolio_context['project_categories'].get(category, [])
        
        return {
            'category': category,
            'category_size': len(category_projects),
            'category_rank': category_projects.index(repo_name) + 1 if repo_name in category_projects else 0,
            'portfolio_percentage': len(category_projects) / len(self.library_data) * 100
        }
    
    def assess_market_opportunity(self, context: Dict) -> Dict[str, Any]:
        """Assess market opportunity for the project."""
        monetization = context.get('monetization_potential', 'Low')
        business_value = context.get('business_value', 'Low')
        technologies = context.get('technologies', [])
        
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
        
        if 'AI/LLM' in technologies or 'Machine Learning' in technologies:
            opportunity['factors'].append('AI/ML technology stack')
            opportunity['recommendations'].append('Leverage AI capabilities for competitive advantage')
        
        if 'Financial/Trading' in context.get('key_features', []):
            opportunity['factors'].append('Financial technology domain')
            opportunity['recommendations'].append('Target fintech market opportunities')
        
        return opportunity
    
    def identify_competitive_advantages(self, context: Dict) -> List[str]:
        """Identify competitive advantages of the project."""
        advantages = []
        technologies = context.get('technologies', [])
        features = context.get('key_features', [])
        
        if 'AI/LLM' in technologies:
            advantages.append('AI-powered functionality')
        
        if 'Financial/Trading' in features:
            advantages.append('Domain expertise in financial technology')
        
        if 'Automation' in features:
            advantages.append('Process automation capabilities')
        
        if 'API Endpoints' in features:
            advantages.append('API-first architecture')
        
        if 'User Authentication' in features:
            advantages.append('User management system')
        
        return advantages
    
    def suggest_development_priorities(self, context: Dict) -> List[str]:
        """Suggest development priorities for the project."""
        priorities = []
        development_stage = context.get('development_stage', 'Unknown')
        features = context.get('key_features', [])
        
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
        if 'User Authentication' not in features:
            priorities.append('Add user authentication system')
        
        if 'API Endpoints' not in features:
            priorities.append('Implement API endpoints')
        
        if 'Testing' not in features:
            priorities.append('Add comprehensive testing')
        
        return priorities
    
    def generate_portfolio_summary_for_llm(self) -> Dict[str, Any]:
        """Generate comprehensive portfolio summary for LLM context."""
        return {
            'portfolio_overview': self.portfolio_context['portfolio_overview'],
            'technology_ecosystem': dict(self.portfolio_context['technology_ecosystem']),
            'project_categories': dict(self.portfolio_context['project_categories']),
            'business_opportunities': dict(self.portfolio_context['business_opportunities']),
            'skill_domains': dict(self.portfolio_context['skill_domains']),
            'top_projects_by_category': self.get_top_projects_by_category(),
            'strategic_recommendations': self.generate_strategic_recommendations()
        }
    
    def get_top_projects_by_category(self) -> Dict[str, List[str]]:
        """Get top projects in each category."""
        top_projects = {}
        
        for category, projects in self.portfolio_context['project_categories'].items():
            # Sort projects by file count (complexity)
            sorted_projects = sorted(
                projects,
                key=lambda p: self.library_data.get(p, {}).get('files', {}).__len__() if isinstance(self.library_data.get(p, {}), dict) else 0,
                reverse=True
            )
            top_projects[category] = sorted_projects[:5]  # Top 5 per category
        
        return top_projects
    
    def generate_strategic_recommendations(self) -> List[Dict[str, Any]]:
        """Generate strategic recommendations for the portfolio."""
        recommendations = []
        
        # High-value opportunities
        high_value = self.portfolio_context['business_opportunities'].get('High', [])
        if high_value:
            recommendations.append({
                'type': 'Monetization',
                'priority': 'High',
                'action': f'Focus on commercializing {len(high_value)} high-value projects',
                'projects': high_value[:3]
            })
        
        # Technology gaps
        tech_ecosystem = self.portfolio_context['technology_ecosystem']['technologies']
        if 'Cloud Platform' not in tech_ecosystem:
            recommendations.append({
                'type': 'Technology',
                'priority': 'Medium',
                'action': 'Expand cloud deployment capabilities',
                'projects': []
            })
        
        # Skill development
        skill_domains = self.portfolio_context['skill_domains']
        if 'AI/Machine Learning' in skill_domains:
            recommendations.append({
                'type': 'Skill Development',
                'priority': 'High',
                'action': 'Leverage AI/ML expertise across portfolio',
                'projects': skill_domains['AI/Machine Learning'][:3]
            })
        
        return recommendations


def main():
    """Main function to demonstrate the enhanced LLM context analyzer."""
    analyzer = EnhancedLLMContextAnalyzer()
    
    # Generate portfolio summary
    portfolio_summary = analyzer.generate_portfolio_summary_for_llm()
    
    # Example: Get context for a specific project
    example_project = list(analyzer.library_data.keys())[0] if analyzer.library_data else "example-project"
    project_context = analyzer.generate_project_context_for_llm(example_project)
    
    print("🎯 Enhanced LLM Context Analyzer")
    print("=" * 60)
    print(f"Portfolio Summary: {len(analyzer.library_data)} repositories analyzed")
    print(f"Example Project Context: {example_project}")
    
    # Save results
    output_dir = Path("llm_context_analysis")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "portfolio_summary.json", 'w') as f:
        json.dump(portfolio_summary, f, indent=2)
    
    with open(output_dir / f"{example_project}_context.json", 'w') as f:
        json.dump(project_context, f, indent=2)
    
    print(f"✅ Analysis saved to {output_dir}/")


if __name__ == "__main__":
    main() 