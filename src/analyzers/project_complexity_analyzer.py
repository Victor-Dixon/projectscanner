#!/usr/bin/env python3
"""
Project Complexity & Architectural Analyzer
Analyzes project structure, complexity, and architectural patterns
"""

import json
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
from datetime import datetime
import ast

class ProjectComplexityAnalyzer:
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
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure and organization."""
        structure_analysis = {
            'project_types': defaultdict(int),
            'directory_depth': [],
            'file_organization': defaultdict(int),
            'module_organization': defaultdict(int),
            'naming_conventions': defaultdict(int),
            'separation_of_concerns': defaultdict(int)
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                
                # Analyze project type
                project_type = self.categorize_project_type(repo_name, files)
                structure_analysis['project_types'][project_type] += 1
                
                # Analyze directory structure
                for file_path in files.keys():
                    depth = len(file_path.split('/'))
                    structure_analysis['directory_depth'].append(depth)
                    
                    # File organization patterns
                    if 'src' in file_path:
                        structure_analysis['file_organization']['src_structure'] += 1
                    if 'tests' in file_path:
                        structure_analysis['file_organization']['test_structure'] += 1
                    if 'docs' in file_path:
                        structure_analysis['file_organization']['documentation'] += 1
                    if 'config' in file_path:
                        structure_analysis['file_organization']['configuration'] += 1
                    
                    # Module organization
                    if file_path.endswith('.py'):
                        if '__init__.py' in file_path:
                            structure_analysis['module_organization']['python_packages'] += 1
                        if 'utils' in file_path or 'helpers' in file_path:
                            structure_analysis['module_organization']['utility_modules'] += 1
                        if 'models' in file_path or 'entities' in file_path:
                            structure_analysis['module_organization']['data_models'] += 1
                        if 'views' in file_path or 'controllers' in file_path:
                            structure_analysis['module_organization']['mvc_pattern'] += 1
                    
                    # Naming conventions
                    self.analyze_naming_conventions(file_path, structure_analysis)
                    
                    # Separation of concerns
                    self.analyze_separation_of_concerns(file_path, structure_analysis)
        
        return structure_analysis
    
    def categorize_project_type(self, repo_name: str, files: Dict) -> str:
        """Categorize the type of project."""
        file_paths = list(files.keys())
        file_lower = [f.lower() for f in file_paths]
        
        # Web applications
        if any('html' in f for f in file_lower) or any('css' in f for f in file_lower):
            return 'Web Application'
        
        # API projects
        if any('api' in f for f in file_lower) or any('endpoint' in f for f in file_lower):
            return 'API Project'
        
        # Data science
        if any('jupyter' in f for f in file_lower) or any('notebook' in f for f in file_lower):
            return 'Data Science'
        
        # Mobile apps
        if any('android' in f for f in file_lower) or any('ios' in f for f in file_lower):
            return 'Mobile Application'
        
        # Desktop apps
        if any('gui' in f for f in file_lower) or any('tkinter' in f for f in file_lower):
            return 'Desktop Application'
        
        # Libraries
        if any('setup.py' in f for f in file_lower) or any('package.json' in f for f in file_lower):
            return 'Library'
        
        # Scripts
        if len(files) < 10:
            return 'Scripts'
        
        return 'General Application'
    
    def analyze_naming_conventions(self, file_path: str, analysis: Dict):
        """Analyze naming conventions used in the project."""
        # File naming
        if '_' in file_path:
            analysis['naming_conventions']['snake_case'] += 1
        elif any(c.isupper() for c in file_path):
            analysis['naming_conventions']['pascal_case'] += 1
        else:
            analysis['naming_conventions']['lowercase'] += 1
    
    def analyze_separation_of_concerns(self, file_path: str, analysis: Dict):
        """Analyze separation of concerns in the project."""
        if 'model' in file_path.lower():
            analysis['separation_of_concerns']['data_layer'] += 1
        if 'view' in file_path.lower() or 'template' in file_path.lower():
            analysis['separation_of_concerns']['presentation_layer'] += 1
        if 'controller' in file_path.lower() or 'service' in file_path.lower():
            analysis['separation_of_concerns']['business_logic'] += 1
        if 'dao' in file_path.lower() or 'repository' in file_path.lower():
            analysis['separation_of_concerns']['data_access'] += 1
    
    def analyze_code_complexity(self) -> Dict[str, Any]:
        """Analyze code complexity patterns."""
        complexity_analysis = {
            'cyclomatic_complexity': [],
            'function_complexity': defaultdict(list),
            'class_complexity': defaultdict(list),
            'nesting_depth': [],
            'code_duplication': defaultdict(int),
            'maintainability_index': []
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                
                for file_path, file_data in files.items():
                    complexity = file_data.get('complexity', 0)
                    complexity_analysis['cyclomatic_complexity'].append(complexity)
                    
                    # Function complexity
                    functions = file_data.get('functions', [])
                    for func in functions:
                        if isinstance(func, dict):
                            func_complexity = func.get('complexity', 0)
                            complexity_analysis['function_complexity'][file_path].append(func_complexity)
                    
                    # Class complexity
                    classes = file_data.get('classes', {})
                    for class_name, class_data in classes.items():
                        if isinstance(class_data, dict):
                            class_complexity = len(class_data.get('methods', []))
                            complexity_analysis['class_complexity'][file_path].append(class_complexity)
                    
                    # Nesting depth (simplified)
                    if complexity > 10:
                        complexity_analysis['nesting_depth'].append('High')
                    elif complexity > 5:
                        complexity_analysis['nesting_depth'].append('Medium')
                    else:
                        complexity_analysis['nesting_depth'].append('Low')
                    
                    # Maintainability index (simplified)
                    if complexity < 5:
                        complexity_analysis['maintainability_index'].append('High')
                    elif complexity < 10:
                        complexity_analysis['maintainability_index'].append('Medium')
                    else:
                        complexity_analysis['maintainability_index'].append('Low')
        
        return complexity_analysis
    
    def analyze_architectural_patterns(self) -> Dict[str, Any]:
        """Analyze architectural patterns used in projects."""
        architectural_analysis = {
            'design_patterns': defaultdict(int),
            'architectural_styles': defaultdict(int),
            'framework_patterns': defaultdict(int),
            'database_patterns': defaultdict(int),
            'api_patterns': defaultdict(int)
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                
                for file_path, file_data in files.items():
                    file_content = str(file_data)
                    
                    # Design patterns
                    if 'class' in file_content and 'def __init__' in file_content:
                        architectural_analysis['design_patterns']['object_oriented'] += 1
                    
                    if 'singleton' in file_content.lower():
                        architectural_analysis['design_patterns']['singleton'] += 1
                    
                    if 'factory' in file_content.lower():
                        architectural_analysis['design_patterns']['factory'] += 1
                    
                    if 'observer' in file_content.lower() or 'event' in file_content.lower():
                        architectural_analysis['design_patterns']['observer'] += 1
                    
                    # Architectural styles
                    if 'microservice' in file_content.lower():
                        architectural_analysis['architectural_styles']['microservices'] += 1
                    
                    if 'monolith' in file_content.lower():
                        architectural_analysis['architectural_styles']['monolithic'] += 1
                    
                    if 'layered' in file_content.lower():
                        architectural_analysis['architectural_styles']['layered'] += 1
                    
                    # Framework patterns
                    if 'django' in file_content.lower():
                        architectural_analysis['framework_patterns']['django_mvc'] += 1
                    
                    if 'flask' in file_content.lower():
                        architectural_analysis['framework_patterns']['flask_minimal'] += 1
                    
                    if 'fastapi' in file_content.lower():
                        architectural_analysis['framework_patterns']['fastapi_modern'] += 1
                    
                    # Database patterns
                    if 'orm' in file_content.lower():
                        architectural_analysis['database_patterns']['orm'] += 1
                    
                    if 'repository' in file_content.lower():
                        architectural_analysis['database_patterns']['repository'] += 1
                    
                    if 'dao' in file_content.lower():
                        architectural_analysis['database_patterns']['dao'] += 1
                    
                    # API patterns
                    if 'rest' in file_content.lower():
                        architectural_analysis['api_patterns']['rest'] += 1
                    
                    if 'graphql' in file_content.lower():
                        architectural_analysis['api_patterns']['graphql'] += 1
                    
                    if 'grpc' in file_content.lower():
                        architectural_analysis['api_patterns']['grpc'] += 1
    
        return architectural_analysis
    
    def analyze_code_organization(self) -> Dict[str, Any]:
        """Analyze code organization and structure."""
        organization_analysis = {
            'file_sizes': [],
            'function_sizes': [],
            'class_sizes': [],
            'import_patterns': defaultdict(int),
            'dependency_management': defaultdict(int),
            'configuration_management': defaultdict(int)
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                
                for file_path, file_data in files.items():
                    # File size analysis
                    functions = file_data.get('functions', [])
                    classes = file_data.get('classes', {})
                    
                    organization_analysis['file_sizes'].append(len(functions) + len(classes))
                    organization_analysis['function_sizes'].extend([len(str(f)) for f in functions])
                    organization_analysis['class_sizes'].extend([len(str(c)) for c in classes.values()])
                    
                    # Import patterns
                    file_content = str(file_data)
                    if 'import' in file_content:
                        organization_analysis['import_patterns']['standard_imports'] += 1
                    if 'from' in file_content and 'import' in file_content:
                        organization_analysis['import_patterns']['specific_imports'] += 1
                    
                    # Dependency management
                    if 'requirements' in file_path.lower():
                        organization_analysis['dependency_management']['python_requirements'] += 1
                    if 'package.json' in file_path.lower():
                        organization_analysis['dependency_management']['npm_package'] += 1
                    if 'pom.xml' in file_path.lower():
                        organization_analysis['dependency_management']['maven_package'] += 1
                    
                    # Configuration management
                    if 'config' in file_path.lower():
                        organization_analysis['configuration_management']['config_files'] += 1
                    if 'settings' in file_path.lower():
                        organization_analysis['configuration_management']['settings_files'] += 1
                    if 'env' in file_path.lower():
                        organization_analysis['configuration_management']['environment_files'] += 1
        
        return organization_analysis
    
    def generate_complexity_report(self) -> Dict[str, Any]:
        """Generate comprehensive complexity and architectural report."""
        report = {
            'project_structure': self.analyze_project_structure(),
            'code_complexity': self.analyze_code_complexity(),
            'architectural_patterns': self.analyze_architectural_patterns(),
            'code_organization': self.analyze_code_organization(),
            'summary': {}
        }
        
        # Generate summary
        report['summary'] = self.generate_complexity_summary(report)
        
        return report
    
    def generate_complexity_summary(self, report: Dict) -> Dict[str, Any]:
        """Generate a summary of complexity and architectural analysis."""
        summary = {
            'project_count': len(self.library_data),
            'average_complexity': 0,
            'complexity_distribution': {},
            'architectural_maturity': 'Intermediate',
            'code_organization_score': 0,
            'architectural_patterns_used': [],
            'strengths': [],
            'improvement_areas': []
        }
        
        # Calculate average complexity
        complexities = report['code_complexity']['cyclomatic_complexity']
        if complexities:
            summary['average_complexity'] = sum(complexities) / len(complexities)
        
        # Complexity distribution
        complexity_counter = Counter(complexities)
        summary['complexity_distribution'] = dict(complexity_counter)
        
        # Architectural maturity assessment
        patterns = report['architectural_patterns']['design_patterns']
        if len(patterns) > 5:
            summary['architectural_maturity'] = 'Advanced'
        elif len(patterns) > 2:
            summary['architectural_maturity'] = 'Intermediate'
        else:
            summary['architectural_maturity'] = 'Basic'
        
        # Code organization score
        organization = report['code_organization']
        if organization['import_patterns']:
            summary['code_organization_score'] += 25
        if organization['dependency_management']:
            summary['code_organization_score'] += 25
        if organization['configuration_management']:
            summary['code_organization_score'] += 25
        if organization['file_sizes'] and max(organization['file_sizes']) < 100:
            summary['code_organization_score'] += 25
        
        # Architectural patterns used
        for pattern_type, patterns in report['architectural_patterns'].items():
            for pattern, count in patterns.items():
                if count > 0:
                    summary['architectural_patterns_used'].append(f"{pattern_type}: {pattern}")
        
        # Identify strengths and improvement areas
        if summary['average_complexity'] < 5:
            summary['strengths'].append('Low Code Complexity')
        if summary['code_organization_score'] > 70:
            summary['strengths'].append('Good Code Organization')
        if len(summary['architectural_patterns_used']) > 3:
            summary['strengths'].append('Diverse Architectural Patterns')
        
        if summary['average_complexity'] > 10:
            summary['improvement_areas'].append('High Code Complexity')
        if summary['code_organization_score'] < 50:
            summary['improvement_areas'].append('Code Organization')
        if len(summary['architectural_patterns_used']) < 2:
            summary['improvement_areas'].append('Architectural Patterns')
        
        return summary
    
    def save_complexity_report(self, report: Dict, output_path: str = "complexity_report.json"):
        """Save the complexity report to a JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4)
            print(f"✅ Complexity report saved to: {output_path}")
        except Exception as e:
            print(f"❌ Error saving complexity report: {e}")

def generate_complexity_analysis(github_data: Dict) -> str:
    """Generate a comprehensive complexity and architectural analysis from GitHub data."""
    analyzer = ProjectComplexityAnalyzer()
    
    # Create a temporary library file for analysis
    temp_library = {"temp_repo": {"files": {}}}
    
    # Convert GitHub data to the expected format
    for repo_name, repo_data in github_data.items():
        if isinstance(repo_data, dict) and 'analysis_data' in repo_data:
            temp_library[repo_name] = {"files": repo_data['analysis_data']}
    
    analyzer.library_data = temp_library
    report = analyzer.generate_complexity_report()
    
    # Format as markdown
    markdown = f"""# Project Complexity & Architectural Analysis

## Summary
- **Total Projects:** {report['summary']['project_count']}
- **Average Complexity:** {report['summary']['average_complexity']:.1f}
- **Architectural Maturity:** {report['summary']['architectural_maturity']}
- **Code Organization Score:** {report['summary']['code_organization_score']}/100

## Strengths
"""
    
    for strength in report['summary']['strengths']:
        markdown += f"- {strength}\n"
    
    markdown += "\n## Areas for Improvement\n"
    for area in report['summary']['improvement_areas']:
        markdown += f"- {area}\n"
    
    markdown += "\n## Project Structure Analysis\n"
    structure = report['project_structure']
    for category, data in structure.items():
        if data:
            markdown += f"\n### {category.replace('_', ' ').title()}\n"
            if isinstance(data, dict):
                for item, count in data.items():
                    if count > 0:
                        markdown += f"- {item}: {count}\n"
            elif isinstance(data, list) and data:
                markdown += f"- Average: {sum(data) / len(data):.1f}\n"
    
    markdown += "\n## Architectural Patterns\n"
    patterns = report['architectural_patterns']
    for category, pattern_data in patterns.items():
        if pattern_data:
            markdown += f"\n### {category.replace('_', ' ').title()}\n"
            for pattern, count in pattern_data.items():
                if count > 0:
                    markdown += f"- {pattern}: {count} instances\n"
    
    markdown += "\n## Code Organization\n"
    organization = report['code_organization']
    for category, data in organization.items():
        if data:
            markdown += f"\n### {category.replace('_', ' ').title()}\n"
            if isinstance(data, dict):
                for item, count in data.items():
                    if count > 0:
                        markdown += f"- {item}: {count}\n"
            elif isinstance(data, list) and data:
                markdown += f"- Average: {sum(data) / len(data):.1f}\n"
    
    return markdown

if __name__ == "__main__":
    analyzer = ProjectComplexityAnalyzer()
    report = analyzer.generate_complexity_report()
    analyzer.save_complexity_report(report)
    print("✅ Project complexity analysis completed!") 