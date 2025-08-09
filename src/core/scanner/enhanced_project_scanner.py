#!/usr/bin/env python3
"""
Enhanced Project Scanner - Comprehensive Analysis Engine
Provides deep, meaningful analysis of projects to capture their true essence.
"""

import json
import ast
import re
import os
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict, Counter
import logging
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedProjectScanner:
    """Comprehensive project analysis engine that captures project essence."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.analysis = {}
        self.project_essence = {}
        
    def scan_project(self) -> Dict:
        """Perform comprehensive project analysis."""
        logger.info(f"🔍 Starting comprehensive analysis of {self.project_path}")
        
        # Basic project info
        self.analysis['project_info'] = self.analyze_project_info()
        
        # Code structure analysis
        self.analysis['code_structure'] = self.analyze_code_structure()
        
        # Dependencies and technology stack
        self.analysis['dependencies'] = self.analyze_dependencies()
        
        # Project purpose and functionality
        self.analysis['purpose_analysis'] = self.analyze_project_purpose()
        
        # Architecture patterns
        self.analysis['architecture'] = self.analyze_architecture_patterns()
        
        # Business logic and features
        self.analysis['business_logic'] = self.analyze_business_logic()
        
        # Integration points
        self.analysis['integrations'] = self.analyze_integrations()
        
        # Data flow and storage
        self.analysis['data_flow'] = self.analyze_data_flow()
        
        # Security and configuration
        self.analysis['security'] = self.analyze_security_config()
        
        # Development patterns
        self.analysis['development_patterns'] = self.analyze_development_patterns()
        
        # Project maturity and quality
        self.analysis['maturity'] = self.analyze_project_maturity()
        
        # Generate project essence summary
        self.analysis['project_essence'] = self.generate_project_essence()
        
        return self.analysis
    
    def analyze_project_info(self) -> Dict:
        """Analyze basic project information."""
        info = {
            'name': self.project_path.name,
            'path': str(self.project_path),
            'scan_timestamp': datetime.now().isoformat(),
            'total_files': 0,
            'total_lines': 0,
            'languages': Counter(),
            'file_types': Counter(),
            'readme_content': '',
            'license': '',
            'git_info': {}
        }
        
        # Count files and lines
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and not self._should_skip_file(file_path):
                info['total_files'] += 1
                info['file_types'][file_path.suffix] += 1
                
                # Count lines
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        info['total_lines'] += len(lines)
                except Exception as e:
                    logger.debug(f"Could not read {file_path}: {e}")
        
        # Detect languages
        for ext, count in info['file_types'].items():
            if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.rs', '.go', '.php', '.rb']:
                lang_map = {
                    '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                    '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.rs': 'Rust',
                    '.go': 'Go', '.php': 'PHP', '.rb': 'Ruby'
                }
                info['languages'][lang_map.get(ext, ext)] += count
        
        # Read README
        readme_files = ['README.md', 'README.txt', 'readme.md', 'readme.txt']
        for readme in readme_files:
            readme_path = self.project_path / readme
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        info['readme_content'] = f.read()
                    break
                except Exception as e:
                    logger.debug(f"Could not read README: {e}")
        
        # Check for license
        license_files = ['LICENSE', 'LICENSE.txt', 'license.txt']
        for license_file in license_files:
            license_path = self.project_path / license_file
            if license_path.exists():
                try:
                    with open(license_path, 'r', encoding='utf-8') as f:
                        info['license'] = f.read()[:200] + "..." if len(f.read()) > 200 else f.read()
                    break
                except Exception as e:
                    logger.debug(f"Could not read license: {e}")
        
        # Git information
        try:
            result = subprocess.run(['git', 'log', '--oneline'], 
                                  cwd=self.project_path, capture_output=True, text=True)
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                info['git_info'] = {
                    'total_commits': len(commits),
                    'last_commit': commits[0] if commits else '',
                    'has_git': True
                }
        except Exception as e:
            info['git_info'] = {'has_git': False, 'error': str(e)}
        
        return info
    
    def analyze_code_structure(self) -> Dict:
        """Analyze code structure and organization."""
        structure = {
            'main_files': [],
            'entry_points': [],
            'modules': [],
            'classes': [],
            'functions': [],
            'imports': Counter(),
            'file_organization': {},
            'complexity_metrics': {}
        }
        
        python_files = list(self.project_path.rglob('*.py'))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                tree = ast.parse(source)
                file_analysis = self._analyze_python_file(py_file, tree, source)
                
                # Collect imports
                for import_name in file_analysis.get('imports', []):
                    structure['imports'][import_name] += 1
                
                # Collect functions and classes
                structure['functions'].extend(file_analysis.get('functions', []))
                structure['classes'].extend(file_analysis.get('classes', []))
                
                # Identify entry points
                if self._is_entry_point(py_file, file_analysis):
                    structure['entry_points'].append(str(py_file))
                
                # Identify main files
                if self._is_main_file(py_file):
                    structure['main_files'].append(str(py_file))
                
            except Exception as e:
                logger.debug(f"Could not analyze {py_file}: {e}")
        
        return structure
    
    def _analyze_python_file(self, file_path: Path, tree: ast.AST, source: str) -> Dict:
        """Analyze a single Python file."""
        analysis = {
            'file_path': str(file_path),
            'imports': [],
            'functions': [],
            'classes': [],
            'complexity': 0,
            'docstrings': [],
            'comments': []
        }
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis['imports'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    analysis['imports'].append(f"{module}.{alias.name}")
        
        # Extract functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis['functions'].append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
                })
            elif isinstance(node, ast.ClassDef):
                analysis['classes'].append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    'bases': [self._get_base_name(base) for base in node.bases]
                })
        
        # Extract docstrings and comments
        analysis['docstrings'] = self._extract_docstrings(tree)
        analysis['comments'] = self._extract_comments(source)
        
        return analysis
    
    def _extract_docstrings(self, tree: ast.AST) -> List[str]:
        """Extract all docstrings from AST."""
        docstrings = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings.append(docstring)
        return docstrings
    
    def _extract_comments(self, source: str) -> List[str]:
        """Extract comments from source code."""
        comments = []
        lines = source.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#') and len(line) > 1:
                comments.append(line[1:].strip())
        return comments
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Get decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        return "unknown"
    
    def _get_base_name(self, base: ast.expr) -> str:
        """Get base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return "unknown"
    
    def _is_entry_point(self, file_path: Path, analysis: Dict) -> bool:
        """Determine if file is an entry point."""
        filename = file_path.name.lower()
        return (filename in ['main.py', '__main__.py', 'app.py', 'run.py', 'start.py'] or
                'if __name__ == "__main__"' in str(analysis))
    
    def _is_main_file(self, file_path: Path) -> bool:
        """Determine if file is a main application file."""
        filename = file_path.name.lower()
        return filename in ['main.py', 'app.py', 'run.py', 'start.py', 'server.py', 'bot.py']
    
    def analyze_dependencies(self) -> Dict:
        """Analyze project dependencies and technology stack."""
        dependencies = {
            'python_packages': [],
            'external_apis': [],
            'databases': [],
            'frameworks': [],
            'tools': [],
            'requirements_files': []
        }
        
        # Check for requirements files
        req_files = ['requirements.txt', 'requirements-dev.txt', 'setup.py', 'pyproject.toml']
        for req_file in req_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                dependencies['requirements_files'].append(str(req_path))
                if req_file == 'requirements.txt':
                    dependencies['python_packages'] = self._parse_requirements(req_path)
        
        # Analyze imports to detect frameworks and libraries
        framework_patterns = {
            'web_frameworks': ['flask', 'django', 'fastapi', 'tornado', 'bottle'],
            'data_science': ['pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn'],
            'ai_ml': ['tensorflow', 'pytorch', 'keras', 'transformers', 'openai'],
            'databases': ['sqlite', 'postgresql', 'mysql', 'mongodb', 'redis'],
            'cloud': ['boto3', 'google.cloud', 'azure', 'aws'],
            'trading': ['yfinance', 'pandas-ta', 'ccxt', 'alpaca', 'ibapi']
        }
        
        # Extract from code structure
        if 'code_structure' in self.analysis:
            imports = self.analysis['code_structure']['imports']
            for import_name, count in imports.items():
                for category, patterns in framework_patterns.items():
                    if any(pattern in import_name.lower() for pattern in patterns):
                        if category not in dependencies:
                            dependencies[category] = []
                        dependencies[category].append(import_name)
        
        return dependencies
    
    def _parse_requirements(self, req_path: Path) -> List[str]:
        """Parse requirements.txt file."""
        packages = []
        try:
            with open(req_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (remove version constraints)
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0]
                        packages.append(package)
        except Exception as e:
            logger.debug(f"Could not parse requirements: {e}")
        return packages
    
    def analyze_project_purpose(self) -> Dict:
        """Analyze project purpose and functionality."""
        purpose = {
            'primary_function': '',
            'target_audience': '',
            'use_cases': [],
            'key_features': [],
            'business_domain': '',
            'problem_solved': '',
            'value_proposition': ''
        }
        
        # Analyze README content
        if 'project_info' in self.analysis:
            readme = self.analysis['project_info']['readme_content']
            if readme:
                purpose.update(self._extract_purpose_from_readme(readme))
        
        # Analyze code patterns
        code_patterns = self._analyze_code_patterns()
        purpose.update(code_patterns)
        
        # Analyze file names and structure
        file_analysis = self._analyze_file_patterns()
        purpose.update(file_analysis)
        
        return purpose
    
    def _extract_purpose_from_readme(self, readme: str) -> Dict:
        """Extract project purpose from README content."""
        purpose = {}
        
        # Look for common patterns in README
        lines = readme.lower().split('\n')
        
        # Find description sections
        for i, line in enumerate(lines):
            if 'description' in line or 'about' in line:
                # Get next few lines as description
                desc_lines = lines[i+1:i+4]
                purpose['primary_function'] = ' '.join(desc_lines)
                break
        
        # Look for features
        features = []
        for line in lines:
            if line.strip().startswith('-') or line.strip().startswith('*'):
                feature = line.strip()[1:].strip()
                if feature and len(feature) > 10:
                    features.append(feature)
        purpose['key_features'] = features[:5]  # Top 5 features
        
        # Detect business domain
        domain_keywords = {
            'trading': ['trading', 'stock', 'portfolio', 'investment', 'finance'],
            'web_app': ['web', 'website', 'app', 'api', 'server'],
            'automation': ['automation', 'bot', 'script', 'workflow'],
            'data_analysis': ['data', 'analysis', 'analytics', 'reporting'],
            'ai_ml': ['ai', 'machine learning', 'neural', 'model', 'prediction']
        }
        
        readme_lower = readme.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in readme_lower for keyword in keywords):
                purpose['business_domain'] = domain
                break
        
        return purpose
    
    def _analyze_code_patterns(self) -> Dict:
        """Analyze code patterns to understand functionality."""
        patterns = {}
        
        if 'code_structure' in self.analysis:
            functions = self.analysis['code_structure']['functions']
            classes = self.analysis['code_structure']['classes']
            
            # Analyze function names for patterns
            function_names = [f['name'] for f in functions]
            
            # Detect patterns
            if any('scrape' in name.lower() for name in function_names):
                patterns['primary_function'] = 'Web scraping/data extraction'
            elif any('trade' in name.lower() or 'stock' in name.lower() for name in function_names):
                patterns['primary_function'] = 'Trading/financial analysis'
            elif any('bot' in name.lower() or 'automate' in name.lower() for name in function_names):
                patterns['primary_function'] = 'Automation/bot'
            elif any('api' in name.lower() or 'server' in name.lower() for name in function_names):
                patterns['primary_function'] = 'Web API/server'
            elif any('ml' in name.lower() or 'model' in name.lower() for name in function_names):
                patterns['primary_function'] = 'Machine learning/AI'
        
        return patterns
    
    def _analyze_file_patterns(self) -> Dict:
        """Analyze file patterns to understand project structure."""
        patterns = {}
        
        # Look for configuration files
        config_files = ['config.py', 'settings.py', '.env', 'config.json']
        if any((self.project_path / f).exists() for f in config_files):
            patterns['has_configuration'] = True
        
        # Look for test files
        test_dirs = ['tests', 'test', '__tests__']
        if any((self.project_path / d).exists() for d in test_dirs):
            patterns['has_tests'] = True
        
        # Look for documentation
        doc_files = ['docs', 'documentation', 'README.md']
        if any((self.project_path / f).exists() for f in doc_files):
            patterns['has_documentation'] = True
        
        return patterns
    
    def analyze_architecture_patterns(self) -> Dict:
        """Analyze software architecture patterns."""
        architecture = {
            'pattern': 'unknown',
            'layers': [],
            'components': [],
            'design_principles': []
        }
        
        # Analyze file structure for architectural patterns
        if 'code_structure' in self.analysis:
            main_files = self.analysis['code_structure']['main_files']
            entry_points = self.analysis['code_structure']['entry_points']
            
            if len(main_files) == 1 and 'app.py' in main_files[0]:
                architecture['pattern'] = 'Web Application'
            elif len(entry_points) > 0:
                architecture['pattern'] = 'Command Line Tool'
            elif any('bot' in f.lower() for f in main_files):
                architecture['pattern'] = 'Bot/Automation'
        
        return architecture
    
    def analyze_business_logic(self) -> Dict:
        """Analyze business logic and core functionality."""
        business_logic = {
            'core_functions': [],
            'data_processing': [],
            'external_interactions': [],
            'business_rules': [],
            'workflows': []
        }
        
        # Extract from function names and docstrings
        if 'code_structure' in self.analysis:
            functions = self.analysis['code_structure']['functions']
            
            for func in functions:
                func_name = func['name'].lower()
                docstring = func.get('docstring', '').lower()
                
                # Categorize functions
                if any(keyword in func_name for keyword in ['process', 'analyze', 'calculate']):
                    business_logic['data_processing'].append(func['name'])
                elif any(keyword in func_name for keyword in ['api', 'request', 'fetch', 'scrape']):
                    business_logic['external_interactions'].append(func['name'])
                elif any(keyword in func_name for keyword in ['validate', 'check', 'verify']):
                    business_logic['business_rules'].append(func['name'])
                elif any(keyword in func_name for keyword in ['run', 'execute', 'start']):
                    business_logic['workflows'].append(func['name'])
                else:
                    business_logic['core_functions'].append(func['name'])
        
        return business_logic
    
    def analyze_integrations(self) -> Dict:
        """Analyze external integrations and APIs."""
        integrations = {
            'apis': [],
            'databases': [],
            'services': [],
            'external_tools': []
        }
        
        # Extract from imports and dependencies
        if 'dependencies' in self.analysis:
            deps = self.analysis['dependencies']
            
            # Map dependencies to integration types
            api_libs = ['requests', 'httpx', 'aiohttp', 'urllib']
            db_libs = ['sqlite', 'psycopg2', 'pymongo', 'redis']
            service_libs = ['boto3', 'google.cloud', 'azure', 'stripe']
            
            for category, libs in [('apis', api_libs), ('databases', db_libs), ('services', service_libs)]:
                for lib in libs:
                    if lib in str(deps):
                        integrations[category].append(lib)
        
        return integrations
    
    def analyze_data_flow(self) -> Dict:
        """Analyze data flow and storage patterns."""
        data_flow = {
            'data_sources': [],
            'data_storage': [],
            'data_transformations': [],
            'data_outputs': []
        }
        
        # Analyze based on file patterns and imports
        if 'code_structure' in self.analysis:
            imports = self.analysis['code_structure']['imports']
            
            # Detect data sources
            if any('pandas' in imp for imp in imports):
                data_flow['data_sources'].append('CSV/Excel files')
            if any('sqlite' in imp for imp in imports):
                data_flow['data_storage'].append('SQLite database')
            if any('json' in imp for imp in imports):
                data_flow['data_sources'].append('JSON files')
        
        return data_flow
    
    def analyze_security_config(self) -> Dict:
        """Analyze security and configuration patterns."""
        security = {
            'authentication': False,
            'authorization': False,
            'encryption': False,
            'environment_vars': False,
            'secrets_management': False
        }
        
        # Check for security patterns
        if 'code_structure' in self.analysis:
            functions = self.analysis['code_structure']['functions']
            
            for func in functions:
                func_name = func['name'].lower()
                if any(keyword in func_name for keyword in ['auth', 'login', 'password']):
                    security['authentication'] = True
                elif any(keyword in func_name for keyword in ['encrypt', 'hash', 'secure']):
                    security['encryption'] = True
        
        # Check for environment variables
        env_files = ['.env', '.env.example', 'config.py']
        if any((self.project_path / f).exists() for f in env_files):
            security['environment_vars'] = True
        
        return security
    
    def analyze_development_patterns(self) -> Dict:
        """Analyze development patterns and practices."""
        patterns = {
            'testing': False,
            'documentation': False,
            'logging': False,
            'error_handling': False,
            'code_quality': False
        }
        
        # Check for testing
        test_dirs = ['tests', 'test', '__tests__']
        if any((self.project_path / d).exists() for d in test_dirs):
            patterns['testing'] = True
        
        # Check for documentation
        doc_files = ['README.md', 'docs', 'documentation']
        if any((self.project_path / f).exists() for f in doc_files):
            patterns['documentation'] = True
        
        # Check for logging
        if 'code_structure' in self.analysis:
            imports = self.analysis['code_structure']['imports']
            if any('logging' in imp for imp in imports):
                patterns['logging'] = True
        
        return patterns
    
    def analyze_project_maturity(self) -> Dict:
        """Analyze project maturity and quality indicators."""
        maturity = {
            'maturity_level': 'unknown',
            'quality_score': 0,
            'maintenance_indicators': [],
            'complexity_metrics': {}
        }
        
        # Calculate quality score based on various factors
        score = 0
        
        # Documentation
        if 'project_info' in self.analysis:
            if self.analysis['project_info']['readme_content']:
                score += 20
        
        # Testing
        if 'development_patterns' in self.analysis:
            if self.analysis['development_patterns']['testing']:
                score += 20
        
        # Git history
        if 'project_info' in self.analysis:
            git_info = self.analysis['project_info']['git_info']
            if git_info.get('total_commits', 0) > 10:
                score += 15
        
        # Code structure
        if 'code_structure' in self.analysis:
            structure = self.analysis['code_structure']
            if structure['entry_points']:
                score += 10
            if structure['main_files']:
                score += 10
        
        maturity['quality_score'] = score
        
        # Determine maturity level
        if score >= 70:
            maturity['maturity_level'] = 'mature'
        elif score >= 40:
            maturity['maturity_level'] = 'developing'
        else:
            maturity['maturity_level'] = 'prototype'
        
        return maturity
    
    def generate_project_essence(self) -> Dict:
        """Generate a comprehensive project essence summary."""
        essence = {
            'summary': '',
            'primary_purpose': '',
            'key_technologies': [],
            'target_users': '',
            'business_value': '',
            'technical_complexity': '',
            'deployment_type': '',
            'integration_points': [],
            'data_handling': '',
            'security_considerations': '',
            'maintenance_status': '',
            'recommendations': []
        }
        
        # Generate summary from all analysis components
        if 'purpose_analysis' in self.analysis:
            purpose = self.analysis['purpose_analysis']
            essence['primary_purpose'] = purpose.get('primary_function', 'Unknown')
            essence['business_value'] = purpose.get('value_proposition', 'Not specified')
        
        if 'dependencies' in self.analysis:
            deps = self.analysis['dependencies']
            essence['key_technologies'] = deps.get('python_packages', [])[:10]
        
        if 'maturity' in self.analysis:
            maturity = self.analysis['maturity']
            essence['maintenance_status'] = maturity.get('maturity_level', 'unknown')
            essence['technical_complexity'] = f"Quality Score: {maturity.get('quality_score', 0)}/100"
        
        # Generate comprehensive summary
        summary_parts = []
        if essence['primary_purpose']:
            summary_parts.append(f"This is a {essence['primary_purpose']} project")
        
        if essence['key_technologies']:
            summary_parts.append(f"using {', '.join(essence['key_technologies'][:3])}")
        
        if essence['maintenance_status']:
            summary_parts.append(f"({essence['maintenance_status']} maturity)")
        
        essence['summary'] = ' '.join(summary_parts) if summary_parts else 'Project analysis incomplete'
        
        return essence
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if file should be skipped in analysis."""
        skip_patterns = [
            '__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules',
            '.pytest_cache', '.mypy_cache', '.coverage', '.tox',
            '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.pyd'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def save_analysis(self, output_file: str = None) -> str:
        """Save analysis results to file."""
        if not output_file:
            output_file = self.project_path / f"enhanced_analysis_{self.project_path.name}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Analysis saved to {output_file}")
        return str(output_file)


def main():
    """Main entry point for enhanced project scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Project Scanner")
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    scanner = EnhancedProjectScanner(args.project_path)
    analysis = scanner.scan_project()
    
    output_file = scanner.save_analysis(args.output)
    
    print(f"\n🎯 PROJECT ESSENCE SUMMARY")
    print("=" * 60)
    if 'project_essence' in analysis:
        essence = analysis['project_essence']
        print(f"Summary: {essence['summary']}")
        print(f"Primary Purpose: {essence['primary_purpose']}")
        print(f"Key Technologies: {', '.join(essence['key_technologies'][:5])}")
        print(f"Maturity: {essence['maintenance_status']}")
        print(f"Quality Score: {essence['technical_complexity']}")
    
    print(f"\n✅ Enhanced analysis complete! Results saved to {output_file}")


if __name__ == "__main__":
    main() 