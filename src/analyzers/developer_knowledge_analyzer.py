#!/usr/bin/env python3
"""
Developer Knowledge & Capability Analyzer
Deep analysis of developer skills, code quality, and architectural understanding
"""

import json
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
from datetime import datetime
import ast

class DeveloperKnowledgeAnalyzer:
    def __init__(self, library_path: str = "github_library_enhanced/github_library_enhanced.json"):
        self.library_path = library_path
        self.library_data = self.load_library()
        
    def load_library(self) -> Dict:
        """Load the scanned library data."""
        try:
            with open(self.library_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Library file not found: {self.library_path}")
            return {}
    
    def analyze_code_quality_metrics(self) -> Dict[str, Any]:
        """Analyze code quality indicators across all projects."""
        quality_metrics = {
            'complexity_distribution': Counter(),
            'function_lengths': [],
            'class_sizes': [],
            'documentation_coverage': 0,
            'test_coverage': 0,
            'lint_suggestions': [],
            'code_style_indicators': defaultdict(int),
            'architectural_patterns': defaultdict(int)
        }
        
        total_files = 0
        documented_files = 0
        test_files = 0
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                total_files += len(files)
                
                for file_path, file_data in files.items():
                    # Complexity analysis
                    complexity = file_data.get('complexity', 0)
                    quality_metrics['complexity_distribution'][complexity] += 1
                    
                    # Function analysis
                    functions = file_data.get('functions', [])
                    for func in functions:
                        if isinstance(func, dict) and 'end_lineno' in func and 'lineno' in func:
                            length = func['end_lineno'] - func['lineno']
                            quality_metrics['function_lengths'].append(length)
                    
                    # Class analysis
                    classes = file_data.get('classes', {})
                    for class_name, class_data in classes.items():
                        if isinstance(class_data, dict) and 'methods' in class_data:
                            quality_metrics['class_sizes'].append(len(class_data['methods']))
                    
                    # Documentation analysis
                    if self.has_documentation(file_path, file_data):
                        documented_files += 1
                    
                    # Test file detection
                    if self.is_test_file(file_path):
                        test_files += 1
                    
                    # Lint suggestions
                    lint_suggestions = file_data.get('lint', [])
                    quality_metrics['lint_suggestions'].extend(lint_suggestions)
                    
                    # Code style indicators
                    self.analyze_code_style(file_path, file_data, quality_metrics)
                    
                    # Architectural patterns
                    self.detect_architectural_patterns(file_path, file_data, quality_metrics)
        
        # Calculate coverage percentages
        if total_files > 0:
            quality_metrics['documentation_coverage'] = (documented_files / total_files) * 100
            quality_metrics['test_coverage'] = (test_files / total_files) * 100
        
        return quality_metrics
    
    def has_documentation(self, file_path: str, file_data: Dict) -> bool:
        """Check if file has documentation."""
        # Check for docstrings in Python files
        if file_path.endswith('.py'):
            functions = file_data.get('functions', [])
            classes = file_data.get('classes', {})
            
            # Check if functions have docstrings
            for func in functions:
                if isinstance(func, dict) and func.get('docstring'):
                    return True
            
            # Check if classes have docstrings
            for class_data in classes.values():
                if isinstance(class_data, dict) and class_data.get('docstring'):
                    return True
        
        # Check for README, docs, etc.
        if any(keyword in file_path.lower() for keyword in ['readme', 'doc', 'docs']):
            return True
        
        return False
    
    def is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file."""
        test_indicators = [
            'test_', '_test', 'tests/', 'spec_', '_spec',
            'test.py', 'tests.py', 'spec.py', 'tests.js',
            'test.js', 'spec.js', 'test.ts', 'spec.ts'
        ]
        
        file_lower = file_path.lower()
        return any(indicator in file_lower for indicator in test_indicators)
    
    def analyze_code_style(self, file_path: str, file_data: Dict, metrics: Dict):
        """Analyze code style indicators."""
        if file_path.endswith('.py'):
            # Check for type hints
            if 'typing' in str(file_data):
                metrics['code_style_indicators']['type_hints'] += 1
            
            # Check for async/await usage
            if 'async' in str(file_data):
                metrics['code_style_indicators']['async_usage'] += 1
            
            # Check for list comprehensions
            if '[' in str(file_data) and 'for' in str(file_data):
                metrics['code_style_indicators']['list_comprehensions'] += 1
        
        # Check for consistent naming
        functions = file_data.get('functions', [])
        for func in functions:
            if isinstance(func, str) and func:
                if func.islower() and '_' in func:
                    metrics['code_style_indicators']['snake_case'] += 1
                elif func[0].isupper():
                    metrics['code_style_indicators']['pascal_case'] += 1
    
    def detect_architectural_patterns(self, file_path: str, file_data: Dict, metrics: Dict):
        """Detect architectural patterns in code."""
        file_content = str(file_data)
        
        # Design patterns
        if 'class' in file_content and 'def __init__' in file_content:
            metrics['architectural_patterns']['classes'] += 1
        
        if 'def __init__' in file_content and 'self.' in file_content:
            metrics['architectural_patterns']['object_oriented'] += 1
        
        if 'import' in file_content and 'from' in file_content:
            metrics['architectural_patterns']['modular_code'] += 1
        
        # Framework patterns
        if 'flask' in file_content or 'django' in file_content:
            metrics['architectural_patterns']['web_framework'] += 1
        
        if 'requests' in file_content:
            metrics['architectural_patterns']['http_requests'] += 1
        
        if 'sqlite' in file_content or 'postgresql' in file_content or 'mysql' in file_content:
            metrics['architectural_patterns']['database_usage'] += 1
    
    def analyze_development_practices(self) -> Dict[str, Any]:
        """Analyze development practices and workflow."""
        practices = {
            'version_control': defaultdict(int),
            'ci_cd': defaultdict(int),
            'documentation_practices': defaultdict(int),
            'testing_practices': defaultdict(int),
            'deployment_practices': defaultdict(int),
            'project_structure': defaultdict(int)
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = list(repo_data['files'].keys())
                
                # Version control
                if any('.git' in f for f in files):
                    practices['version_control']['git'] += 1
                
                # CI/CD
                if any('.github' in f for f in files):
                    practices['ci_cd']['github_actions'] += 1
                if any('travis' in f for f in files):
                    practices['ci_cd']['travis_ci'] += 1
                if any('jenkins' in f for f in files):
                    practices['ci_cd']['jenkins'] += 1
                
                # Documentation
                if any('readme' in f.lower() for f in files):
                    practices['documentation_practices']['readme'] += 1
                if any('docs' in f.lower() for f in files):
                    practices['documentation_practices']['documentation'] += 1
                if any('license' in f.lower() for f in files):
                    practices['documentation_practices']['license'] += 1
                
                # Testing
                if any('test' in f.lower() for f in files):
                    practices['testing_practices']['unit_tests'] += 1
                if any('pytest' in f.lower() for f in files):
                    practices['testing_practices']['pytest'] += 1
                if any('unittest' in f.lower() for f in files):
                    practices['testing_practices']['unittest'] += 1
                
                # Deployment
                if any('docker' in f.lower() for f in files):
                    practices['deployment_practices']['docker'] += 1
                if any('kubernetes' in f.lower() for f in files):
                    practices['deployment_practices']['kubernetes'] += 1
                if any('requirements' in f.lower() for f in files):
                    practices['deployment_practices']['dependency_management'] += 1
                
                # Project structure
                if any('src' in f.lower() for f in files):
                    practices['project_structure']['src_structure'] += 1
                if any('config' in f.lower() for f in files):
                    practices['project_structure']['configuration'] += 1
                if any('utils' in f.lower() for f in files):
                    practices['project_structure']['utilities'] += 1
        
        return practices
    
    def analyze_technology_expertise(self) -> Dict[str, Any]:
        """Analyze technology expertise and proficiency levels."""
        expertise = {
            'languages': defaultdict(lambda: {'files': 0, 'complexity': 0, 'projects': 0}),
            'frameworks': defaultdict(lambda: {'files': 0, 'projects': 0}),
            'databases': defaultdict(lambda: {'files': 0, 'projects': 0}),
            'cloud_services': defaultdict(lambda: {'files': 0, 'projects': 0}),
            'tools': defaultdict(lambda: {'files': 0, 'projects': 0})
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                
                for file_path, file_data in files.items():
                    # Language analysis
                    language = file_data.get('language', '')
                    if language:
                        expertise['languages'][language]['files'] += 1
                        expertise['languages'][language]['complexity'] += file_data.get('complexity', 0)
                        expertise['languages'][language]['projects'] += 1
                    
                    # Framework detection
                    self.detect_frameworks(file_path, file_data, expertise)
                    
                    # Database detection
                    self.detect_databases(file_path, file_data, expertise)
                    
                    # Cloud services detection
                    self.detect_cloud_services(file_path, file_data, expertise)
                    
                    # Tools detection
                    self.detect_tools(file_path, file_data, expertise)
        
        return expertise
    
    def detect_frameworks(self, file_path: str, file_data: Dict, expertise: Dict):
        """Detect frameworks used in the code."""
        file_content = str(file_data)
        
        frameworks = {
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'express': 'Express.js',
            'spring': 'Spring',
            'laravel': 'Laravel',
            'rails': 'Ruby on Rails'
        }
        
        for keyword, framework in frameworks.items():
            if keyword in file_content.lower():
                expertise['frameworks'][framework]['files'] += 1
                expertise['frameworks'][framework]['projects'] += 1
    
    def detect_databases(self, file_path: str, file_data: Dict, expertise: Dict):
        """Detect databases used in the code."""
        file_content = str(file_data)
        
        databases = {
            'sqlite': 'SQLite',
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongodb': 'MongoDB',
            'redis': 'Redis',
            'elasticsearch': 'Elasticsearch'
        }
        
        for keyword, database in databases.items():
            if keyword in file_content.lower():
                expertise['databases'][database]['files'] += 1
                expertise['databases'][database]['projects'] += 1
    
    def detect_cloud_services(self, file_path: str, file_data: Dict, expertise: Dict):
        """Detect cloud services used in the code."""
        file_content = str(file_data)
        
        cloud_services = {
            'aws': 'AWS',
            'azure': 'Azure',
            'gcp': 'Google Cloud',
            'heroku': 'Heroku',
            'digitalocean': 'DigitalOcean',
            'vercel': 'Vercel',
            'netlify': 'Netlify'
        }
        
        for keyword, service in cloud_services.items():
            if keyword in file_content.lower():
                expertise['cloud_services'][service]['files'] += 1
                expertise['cloud_services'][service]['projects'] += 1
    
    def detect_tools(self, file_path: str, file_data: Dict, expertise: Dict):
        """Detect development tools used in the code."""
        file_content = str(file_data)
        
        tools = {
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'jenkins': 'Jenkins',
            'gitlab': 'GitLab CI',
            'travis': 'Travis CI',
            'pytest': 'pytest',
            'junit': 'JUnit',
            'maven': 'Maven',
            'gradle': 'Gradle',
            'npm': 'npm',
            'yarn': 'Yarn'
        }
        
        for keyword, tool in tools.items():
            if keyword in file_content.lower():
                expertise['tools'][tool]['files'] += 1
                expertise['tools'][tool]['projects'] += 1
    
    def generate_developer_profile(self) -> Dict[str, Any]:
        """Generate comprehensive developer profile."""
        profile = {
            'code_quality': self.analyze_code_quality_metrics(),
            'development_practices': self.analyze_development_practices(),
            'technology_expertise': self.analyze_technology_expertise(),
            'summary': {}
        }
        
        # Generate summary
        profile['summary'] = self.generate_profile_summary(profile)
        
        return profile
    
    def generate_profile_summary(self, profile: Dict) -> Dict[str, Any]:
        """Generate a summary of the developer's profile."""
        summary = {
            'total_projects': len(self.library_data),
            'primary_languages': [],
            'expertise_level': 'Intermediate',
            'code_quality_score': 0,
            'best_practices_score': 0,
            'technology_breadth': 0,
            'strengths': [],
            'areas_for_improvement': []
        }
        
        # Calculate scores
        quality = profile['code_quality']
        practices = profile['development_practices']
        expertise = profile['technology_expertise']
        
        # Code quality score
        if quality['documentation_coverage'] > 50:
            summary['code_quality_score'] += 25
        if quality['test_coverage'] > 30:
            summary['code_quality_score'] += 25
        if len(quality['lint_suggestions']) < 10:
            summary['code_quality_score'] += 25
        if quality['complexity_distribution'][0] > quality['complexity_distribution'][10]:
            summary['code_quality_score'] += 25
        
        # Best practices score
        if practices['version_control']['git'] > 0:
            summary['best_practices_score'] += 20
        if practices['ci_cd']:
            summary['best_practices_score'] += 20
        if practices['testing_practices']['unit_tests'] > 0:
            summary['best_practices_score'] += 20
        if practices['documentation_practices']['readme'] > 0:
            summary['best_practices_score'] += 20
        if practices['deployment_practices']['docker'] > 0:
            summary['best_practices_score'] += 20
        
        # Technology breadth
        summary['technology_breadth'] = (
            len(expertise['languages']) + 
            len(expertise['frameworks']) + 
            len(expertise['databases']) + 
            len(expertise['cloud_services'])
        )
        
        # Determine expertise level
        total_score = summary['code_quality_score'] + summary['best_practices_score']
        if total_score >= 80:
            summary['expertise_level'] = 'Expert'
        elif total_score >= 60:
            summary['expertise_level'] = 'Advanced'
        elif total_score >= 40:
            summary['expertise_level'] = 'Intermediate'
        else:
            summary['expertise_level'] = 'Beginner'
        
        # Identify strengths and areas for improvement
        if summary['code_quality_score'] > 70:
            summary['strengths'].append('Code Quality')
        if summary['best_practices_score'] > 70:
            summary['strengths'].append('Development Practices')
        if summary['technology_breadth'] > 10:
            summary['strengths'].append('Technology Breadth')
        
        if summary['code_quality_score'] < 50:
            summary['areas_for_improvement'].append('Code Quality')
        if summary['best_practices_score'] < 50:
            summary['areas_for_improvement'].append('Development Practices')
        if summary['technology_breadth'] < 5:
            summary['areas_for_improvement'].append('Technology Diversity')
        
        return summary
    
    def save_developer_profile(self, profile: Dict, output_path: str = "developer_profile.json"):
        """Save the developer profile to a JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=4)
            print(f"✅ Developer profile saved to: {output_path}")
        except Exception as e:
            print(f"❌ Error saving developer profile: {e}")

def generate_developer_profile(github_data: Dict) -> str:
    """Generate a comprehensive developer profile from GitHub data."""
    analyzer = DeveloperKnowledgeAnalyzer()
    
    # Create a temporary library file for analysis
    temp_library = {"temp_repo": {"files": {}}}
    
    # Convert GitHub data to the expected format
    for repo_name, repo_data in github_data.items():
        if isinstance(repo_data, dict) and 'analysis_data' in repo_data:
            temp_library[repo_name] = {"files": repo_data['analysis_data']}
    
    analyzer.library_data = temp_library
    profile = analyzer.generate_developer_profile()
    
    # Format as markdown
    markdown = f"""# Developer Knowledge Profile

## Summary
- **Expertise Level:** {profile['summary']['expertise_level']}
- **Total Projects:** {profile['summary']['total_projects']}
- **Code Quality Score:** {profile['summary']['code_quality_score']}/100
- **Best Practices Score:** {profile['summary']['best_practices_score']}/100
- **Technology Breadth:** {profile['summary']['technology_breadth']} technologies

## Strengths
"""
    
    for strength in profile['summary']['strengths']:
        markdown += f"- {strength}\n"
    
    markdown += "\n## Areas for Improvement\n"
    for area in profile['summary']['areas_for_improvement']:
        markdown += f"- {area}\n"
    
    markdown += "\n## Code Quality Metrics\n"
    quality = profile['code_quality']
    markdown += f"- Documentation Coverage: {quality['documentation_coverage']:.1f}%\n"
    markdown += f"- Test Coverage: {quality['test_coverage']:.1f}%\n"
    markdown += f"- Average Complexity: {sum(quality['complexity_distribution'].keys()) / len(quality['complexity_distribution']) if quality['complexity_distribution'] else 0:.1f}\n"
    
    markdown += "\n## Development Practices\n"
    practices = profile['development_practices']
    for category, items in practices.items():
        if items:
            markdown += f"\n### {category.replace('_', ' ').title()}\n"
            for practice, count in items.items():
                if count > 0:
                    markdown += f"- {practice}: {count} projects\n"
    
    markdown += "\n## Technology Expertise\n"
    expertise = profile['technology_expertise']
    for category, technologies in expertise.items():
        if technologies:
            markdown += f"\n### {category.replace('_', ' ').title()}\n"
            for tech, data in technologies.items():
                if data['files'] > 0:
                    markdown += f"- {tech}: {data['files']} files, {data['projects']} projects\n"
    
    return markdown

if __name__ == "__main__":
    analyzer = DeveloperKnowledgeAnalyzer()
    profile = analyzer.generate_developer_profile()
    analyzer.save_developer_profile(profile)
    print("✅ Developer profile analysis completed!") 