#!/usr/bin/env python3
"""
Deep Project Insights Analyzer
Extracts comprehensive insights from scanned projects
"""

import json
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class DeepProjectInsights:
    def __init__(self, library_path: str = "github_library_enhanced/github_library_enhanced.json"):
        self.library_path = library_path
        self.library_data = self.load_library()
        self.insights = {}
        
    def load_library(self) -> Dict:
        """Load the scanned library data."""
        try:
            with open(self.library_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Library file not found: {self.library_path}")
            return {}
    
    def analyze_project_structures(self) -> Dict[str, Any]:
        """Analyze project structure patterns in detail."""
        structures = {
            'project_types': Counter(),
            'file_organizations': Counter(),
            'naming_patterns': Counter(),
            'architecture_patterns': Counter(),
            'dependency_patterns': Counter()
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = list(repo_data['files'].keys())
                
                # Analyze project structure
                self.analyze_single_project_structure(repo_name, files, structures)
                
                # Analyze file organization
                self.analyze_file_organization(files, structures)
                
                # Analyze naming patterns
                self.analyze_naming_patterns(files, structures)
        
        return structures
    
    def analyze_single_project_structure(self, repo_name: str, files: List[str], structures: Dict):
        """Analyze structure of a single project."""
        repo_lower = repo_name.lower()
        
        # Determine project type based on name and files
        if any(keyword in repo_lower for keyword in ['bot', 'automation', 'script']):
            structures['project_types']['automation'] += 1
        elif any(keyword in repo_lower for keyword in ['web', 'site', 'app', 'api']):
            structures['project_types']['web_application'] += 1
        elif any(keyword in repo_lower for keyword in ['ai', 'ml', 'gpt', 'neural']):
            structures['project_types']['ai_ml'] += 1
        elif any(keyword in repo_lower for keyword in ['gui', 'interface', 'tkinter']):
            structures['project_types']['gui_application'] += 1
        elif any(keyword in repo_lower for keyword in ['data', 'analysis', 'analytics']):
            structures['project_types']['data_analysis'] += 1
        elif any(keyword in repo_lower for keyword in ['sims', 'mod', 'game']):
            structures['project_types']['gaming'] += 1
        elif any(keyword in repo_lower for keyword in ['tool', 'utility', 'helper']):
            structures['project_types']['utility'] += 1
        else:
            structures['project_types']['experimental'] += 1
        
        # Analyze architecture patterns
        if any('__init__.py' in f for f in files):
            structures['architecture_patterns']['python_package'] += 1
        if any('main.py' in f or 'app.py' in f for f in files):
            structures['architecture_patterns']['main_entry_point'] += 1
        if any('config' in f or 'settings' in f for f in files):
            structures['architecture_patterns']['configuration_management'] += 1
        if any('test' in f for f in files):
            structures['architecture_patterns']['testing_framework'] += 1
        if any('requirements' in f for f in files):
            structures['dependency_patterns']['python_dependencies'] += 1
        if any('package.json' in f for f in files):
            structures['dependency_patterns']['node_dependencies'] += 1
    
    def analyze_file_organization(self, files: List[str], structures: Dict):
        """Analyze how files are organized."""
        # Check for common directory patterns
        directories = set()
        for file_path in files:
            if '/' in file_path or '\\' in file_path:
                dir_parts = file_path.replace('\\', '/').split('/')[:-1]
                if dir_parts:
                    directories.add('/'.join(dir_parts))
        
        if len(directories) > 5:
            structures['file_organizations']['complex_hierarchy'] += 1
        elif len(directories) > 2:
            structures['file_organizations']['moderate_hierarchy'] += 1
        else:
            structures['file_organizations']['flat_structure'] += 1
    
    def analyze_naming_patterns(self, files: List[str], structures: Dict):
        """Analyze file naming patterns."""
        for file_path in files:
            filename = file_path.split('/')[-1].split('\\')[-1]
            
            # Analyze naming conventions
            if filename.startswith('test_'):
                structures['naming_patterns']['test_files'] += 1
            elif filename.startswith('config_') or filename.startswith('settings_'):
                structures['naming_patterns']['config_files'] += 1
            elif filename.startswith('utils_') or filename.startswith('helper_'):
                structures['naming_patterns']['utility_files'] += 1
            elif filename.endswith('_manager.py'):
                structures['naming_patterns']['manager_classes'] += 1
            elif filename.endswith('_handler.py'):
                structures['naming_patterns']['handler_classes'] += 1
    
    def analyze_technology_stack(self) -> Dict[str, Any]:
        """Analyze technology stack in detail."""
        tech_stack = {
            'languages': Counter(),
            'frameworks': Counter(),
            'libraries': Counter(),
            'tools': Counter(),
            'databases': Counter(),
            'cloud_services': Counter(),
            'file_extensions': Counter()
        }
        
        # Technology patterns to detect
        tech_patterns = {
            'web_frameworks': ['flask', 'django', 'fastapi', 'express', 'react', 'vue', 'angular', 'bootstrap'],
            'databases': ['sqlite', 'postgresql', 'mysql', 'mongodb', 'redis', 'sql'],
            'cloud': ['aws', 'azure', 'gcp', 'heroku', 'vercel', 'netlify'],
            'ai_ml': ['tensorflow', 'pytorch', 'scikit-learn', 'opencv', 'numpy', 'pandas', 'matplotlib'],
            'automation': ['selenium', 'beautifulsoup', 'requests', 'pyautogui', 'schedule'],
            'gui': ['tkinter', 'pyqt', 'kivy', 'wxpython', 'electron', 'gtk'],
            'testing': ['pytest', 'unittest', 'nose', 'junit', 'mocha'],
            'build_tools': ['docker', 'dockerfile', 'makefile', 'gradle', 'maven']
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                for file_path in repo_data['files'].keys():
                    # Analyze file extensions
                    if '.' in file_path:
                        ext = file_path.split('.')[-1].lower()
                        tech_stack['file_extensions'][ext] += 1
                        
                        # Map extensions to languages
                        lang_map = {
                            'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript',
                            'rs': 'Rust', 'cpp': 'C++', 'c': 'C', 'java': 'Java',
                            'html': 'HTML', 'css': 'CSS', 'php': 'PHP',
                            'go': 'Go', 'rb': 'Ruby', 'swift': 'Swift',
                            'kt': 'Kotlin', 'scala': 'Scala', 'r': 'R',
                            'sql': 'SQL', 'sh': 'Shell', 'bat': 'Batch',
                            'ps1': 'PowerShell', 'json': 'JSON', 'xml': 'XML',
                            'yaml': 'YAML', 'yml': 'YAML', 'toml': 'TOML',
                            'md': 'Markdown', 'txt': 'Text'
                        }
                        
                        if ext in lang_map:
                            tech_stack['languages'][lang_map[ext]] += 1
                    
                    # Detect technologies from file paths and names
                    file_lower = file_path.lower()
                    for category, patterns in tech_patterns.items():
                        for pattern in patterns:
                            if pattern in file_lower:
                                tech_stack[category.replace('_', 's')][pattern] += 1
        
        return tech_stack
    
    def analyze_code_patterns(self) -> Dict[str, Any]:
        """Analyze code patterns and complexity."""
        patterns = {
            'function_patterns': Counter(),
            'class_patterns': Counter(),
            'complexity_levels': Counter(),
            'maturity_distribution': Counter(),
            'agent_types': Counter(),
            'code_quality': {
                'high_complexity_files': [],
                'well_structured_files': [],
                'simple_files': []
            }
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                for file_path, file_data in repo_data['files'].items():
                    # Analyze complexity
                    complexity = file_data.get('complexity', 0)
                    patterns['complexity_levels'][self.categorize_complexity(complexity)] += 1
                    
                    if complexity > 50:
                        patterns['code_quality']['high_complexity_files'].append({
                            'file': file_path,
                            'repo': repo_name,
                            'complexity': complexity
                        })
                    elif complexity < 10:
                        patterns['code_quality']['simple_files'].append({
                            'file': file_path,
                            'repo': repo_name,
                            'complexity': complexity
                        })
                    else:
                        patterns['code_quality']['well_structured_files'].append({
                            'file': file_path,
                            'repo': repo_name,
                            'complexity': complexity
                        })
                    
                    # Analyze functions
                    if 'functions' in file_data:
                        for func_name in file_data['functions']:
                            patterns['function_patterns'][self.categorize_function(func_name)] += 1
                    
                    # Analyze classes
                    if 'classes' in file_data:
                        for class_name, class_info in file_data['classes'].items():
                            patterns['class_patterns'][self.categorize_class(class_name)] += 1
                            
                            if 'maturity' in class_info:
                                patterns['maturity_distribution'][class_info['maturity']] += 1
                            if 'agent_type' in class_info:
                                patterns['agent_types'][class_info['agent_type']] += 1
        
        return patterns
    
    def categorize_complexity(self, complexity: int) -> str:
        """Categorize complexity levels."""
        if complexity > 50:
            return 'very_high'
        elif complexity > 30:
            return 'high'
        elif complexity > 15:
            return 'medium'
        elif complexity > 5:
            return 'low'
        else:
            return 'very_low'
    
    def categorize_function(self, func_name: str) -> str:
        """Categorize function types."""
        func_lower = func_name.lower()
        
        if any(keyword in func_lower for keyword in ['get_', 'fetch_', 'retrieve_']):
            return 'data_retrieval'
        elif any(keyword in func_lower for keyword in ['set_', 'update_', 'modify_']):
            return 'data_modification'
        elif any(keyword in func_lower for keyword in ['process_', 'handle_', 'manage_']):
            return 'processing'
        elif any(keyword in func_lower for keyword in ['validate_', 'check_', 'verify_']):
            return 'validation'
        elif any(keyword in func_lower for keyword in ['init_', 'setup_', 'configure_']):
            return 'initialization'
        elif any(keyword in func_lower for keyword in ['clean_', 'destroy_', 'close_']):
            return 'cleanup'
        else:
            return 'general'
    
    def categorize_class(self, class_name: str) -> str:
        """Categorize class types."""
        class_lower = class_name.lower()
        
        if any(keyword in class_lower for keyword in ['manager', 'controller']):
            return 'manager'
        elif any(keyword in class_lower for keyword in ['handler', 'processor']):
            return 'handler'
        elif any(keyword in class_lower for keyword in ['model', 'entity']):
            return 'model'
        elif any(keyword in class_lower for keyword in ['service', 'api']):
            return 'service'
        elif any(keyword in class_lower for keyword in ['util', 'helper']):
            return 'utility'
        elif any(keyword in class_lower for keyword in ['config', 'settings']):
            return 'configuration'
        else:
            return 'general'
    
    def analyze_development_practices(self) -> Dict[str, Any]:
        """Analyze development practices and patterns."""
        practices = {
            'testing_practices': Counter(),
            'documentation_practices': Counter(),
            'configuration_management': Counter(),
            'deployment_practices': Counter(),
            'version_control': Counter(),
            'code_organization': Counter()
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = list(repo_data['files'].keys())
                file_lower = [f.lower() for f in files]
                
                # Testing practices
                if any('test' in f for f in file_lower):
                    practices['testing_practices']['has_tests'] += 1
                if any('pytest' in f for f in file_lower):
                    practices['testing_practices']['pytest_framework'] += 1
                if any('unittest' in f for f in file_lower):
                    practices['testing_practices']['unittest_framework'] += 1
                
                # Documentation practices
                if any('readme' in f for f in file_lower):
                    practices['documentation_practices']['has_readme'] += 1
                if any('doc' in f for f in file_lower):
                    practices['documentation_practices']['has_documentation'] += 1
                if any('license' in f for f in file_lower):
                    practices['documentation_practices']['has_license'] += 1
                
                # Configuration management
                if any('config' in f for f in file_lower):
                    practices['configuration_management']['has_config'] += 1
                if any('settings' in f for f in file_lower):
                    practices['configuration_management']['has_settings'] += 1
                if any('env' in f for f in file_lower):
                    practices['configuration_management']['environment_variables'] += 1
                
                # Deployment practices
                if any('docker' in f for f in file_lower):
                    practices['deployment_practices']['docker_containerization'] += 1
                if any('requirements' in f for f in file_lower):
                    practices['deployment_practices']['python_dependencies'] += 1
                if any('package.json' in f for f in file_lower):
                    practices['deployment_practices']['node_dependencies'] += 1
                
                # Code organization
                if any('__init__.py' in f for f in file_lower):
                    practices['code_organization']['python_packages'] += 1
                if any('main.py' in f for f in file_lower):
                    practices['code_organization']['main_entry_points'] += 1
                if len(files) > 20:
                    practices['code_organization']['large_projects'] += 1
                elif len(files) > 5:
                    practices['code_organization']['medium_projects'] += 1
                else:
                    practices['code_organization']['small_projects'] += 1
        
        return practices
    
    def analyze_project_evolution(self) -> Dict[str, Any]:
        """Analyze project evolution and patterns."""
        evolution = {
            'project_sizes': [],
            'complexity_trends': [],
            'technology_adoption': Counter(),
            'project_categories': Counter(),
            'development_stages': Counter()
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                file_count = len(files)
                
                # Calculate project metrics
                complexities = [f.get('complexity', 0) for f in files.values()]
                avg_complexity = sum(complexities) / max(len(complexities), 1)
                max_complexity = max(complexities) if complexities else 0
                
                project_info = {
                    'name': repo_name,
                    'file_count': file_count,
                    'avg_complexity': avg_complexity,
                    'max_complexity': max_complexity,
                    'total_complexity': sum(complexities)
                }
                
                evolution['project_sizes'].append(project_info)
                
                # Categorize project size
                if file_count > 50:
                    evolution['development_stages']['large_project'] += 1
                elif file_count > 20:
                    evolution['development_stages']['medium_project'] += 1
                elif file_count > 5:
                    evolution['development_stages']['small_project'] += 1
                else:
                    evolution['development_stages']['micro_project'] += 1
                
                # Analyze complexity trends
                if avg_complexity > 30:
                    evolution['complexity_trends'].append({
                        'repo': repo_name,
                        'complexity': avg_complexity,
                        'category': 'high_complexity'
                    })
                elif avg_complexity > 15:
                    evolution['complexity_trends'].append({
                        'repo': repo_name,
                        'complexity': avg_complexity,
                        'category': 'medium_complexity'
                    })
                else:
                    evolution['complexity_trends'].append({
                        'repo': repo_name,
                        'complexity': avg_complexity,
                        'category': 'low_complexity'
                    })
        
        return evolution
    
    def generate_deep_insights(self) -> Dict[str, Any]:
        """Generate comprehensive deep insights."""
        insights = {
            'project_structures': self.analyze_project_structures(),
            'technology_stack': self.analyze_technology_stack(),
            'code_patterns': self.analyze_code_patterns(),
            'development_practices': self.analyze_development_practices(),
            'project_evolution': self.analyze_project_evolution()
        }
        
        return insights
    
    def create_insights_visualizations(self, insights: Dict[str, Any], output_dir: str = "deep_insights"):
        """Create visualizations for the insights."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Project Types Distribution
        plt.figure(figsize=(12, 8))
        project_types = insights['project_structures']['project_types']
        if project_types:
            plt.subplot(2, 2, 1)
            plt.pie(project_types.values(), labels=project_types.keys(), autopct='%1.1f%%')
            plt.title('Project Types Distribution')
        
        # Technology Stack
        tech_stack = insights['technology_stack']['languages']
        if tech_stack:
            plt.subplot(2, 2, 2)
            languages = list(tech_stack.keys())[:10]
            counts = [tech_stack[lang] for lang in languages]
            plt.barh(languages, counts)
            plt.title('Programming Languages Used')
            plt.xlabel('Number of Files')
        
        # Complexity Distribution
        complexity_levels = insights['code_patterns']['complexity_levels']
        if complexity_levels:
            plt.subplot(2, 2, 3)
            plt.bar(complexity_levels.keys(), complexity_levels.values())
            plt.title('Code Complexity Distribution')
            plt.xlabel('Complexity Level')
            plt.ylabel('Number of Files')
        
        # Development Practices
        practices = insights['development_practices']['testing_practices']
        if practices:
            plt.subplot(2, 2, 4)
            plt.bar(practices.keys(), practices.values())
            plt.title('Testing Practices')
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/insights_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Insights visualizations saved to: {output_dir}/")
    
    def generate_comprehensive_report(self, output_dir: str = "deep_insights"):
        """Generate comprehensive deep insights report."""
        os.makedirs(output_dir, exist_ok=True)
        
        insights = self.generate_deep_insights()
        
        # Create visualizations
        self.create_insights_visualizations(insights, output_dir)
        
        # Save detailed reports
        self.save_insights_report(insights, f"{output_dir}/deep_insights_report.json")
        self.save_summary_report(insights, f"{output_dir}/deep_insights_summary.md")
        
        print(f"📊 Deep insights reports saved to: {output_dir}/")
    
    def save_insights_report(self, insights: Dict, output_path: str):
        """Save insights report to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
    
    def save_summary_report(self, insights: Dict, output_path: str):
        """Generate a comprehensive markdown summary report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 🔍 Deep Project Insights Analysis\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 📊 Project Structure Analysis\n\n")
            
            # Project Types
            project_types = insights['project_structures']['project_types']
            f.write("### 🎯 Project Types\n")
            for project_type, count in project_types.most_common():
                f.write(f"- **{project_type.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            # Architecture Patterns
            arch_patterns = insights['project_structures']['architecture_patterns']
            f.write("### 🏗️ Architecture Patterns\n")
            for pattern, count in arch_patterns.most_common():
                f.write(f"- **{pattern.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            f.write("## 🔧 Technology Stack Analysis\n\n")
            
            # Languages
            languages = insights['technology_stack']['languages']
            f.write("### 💻 Programming Languages\n")
            for lang, count in languages.most_common(10):
                f.write(f"- **{lang}:** {count} files\n")
            f.write("\n")
            
            # Frameworks
            frameworks = insights['technology_stack']['frameworks']
            f.write("### 🛠️ Frameworks & Libraries\n")
            for framework, count in frameworks.most_common(10):
                f.write(f"- **{framework}:** {count} occurrences\n")
            f.write("\n")
            
            f.write("## 📈 Code Quality Analysis\n\n")
            
            # Complexity Distribution
            complexity = insights['code_patterns']['complexity_levels']
            f.write("### 🎯 Code Complexity Distribution\n")
            for level, count in complexity.most_common():
                f.write(f"- **{level.replace('_', ' ').title()}:** {count} files\n")
            f.write("\n")
            
            # Function Patterns
            func_patterns = insights['code_patterns']['function_patterns']
            f.write("### 🔧 Function Patterns\n")
            for pattern, count in func_patterns.most_common():
                f.write(f"- **{pattern.replace('_', ' ').title()}:** {count} functions\n")
            f.write("\n")
            
            f.write("## 🛠️ Development Practices\n\n")
            
            # Testing Practices
            testing = insights['development_practices']['testing_practices']
            f.write("### 🧪 Testing Practices\n")
            for practice, count in testing.most_common():
                f.write(f"- **{practice.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            # Documentation
            docs = insights['development_practices']['documentation_practices']
            f.write("### 📚 Documentation Practices\n")
            for practice, count in docs.most_common():
                f.write(f"- **{practice.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            f.write("## 🚀 Project Evolution\n\n")
            
            # Project Sizes
            sizes = insights['project_evolution']['development_stages']
            f.write("### 📦 Project Size Distribution\n")
            for size, count in sizes.most_common():
                f.write(f"- **{size.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            f.write("## 💡 Key Insights & Recommendations\n\n")
            
            f.write("### 🎯 Strengths\n")
            # Identify strengths based on analysis
            if project_types.get('automation', 0) > 5:
                f.write("- **Automation Expertise:** Strong focus on automated solutions\n")
            if project_types.get('utility', 0) > 10:
                f.write("- **Utility Development:** Excellent at creating practical tools\n")
            if frameworks:
                f.write("- **Technology Diversity:** Using multiple frameworks and libraries\n")
            f.write("\n")
            
            f.write("### 🌱 Growth Opportunities\n")
            # Identify areas for improvement
            if not testing.get('has_tests', 0):
                f.write("- **Testing:** Consider adding more test coverage\n")
            if not docs.get('has_documentation', 0):
                f.write("- **Documentation:** Improve project documentation\n")
            f.write("\n")
            
            f.write("### 🎯 Recommendations\n")
            f.write("- Focus on your strongest areas (automation, utilities)\n")
            f.write("- Expand into new technology areas\n")
            f.write("- Improve testing and documentation practices\n")
            f.write("- Consider larger, more complex projects\n")

def main():
    """Main function to run the deep insights analyzer."""
    print("🔍 Generating Deep Project Insights...")
    
    analyzer = DeepProjectInsights()
    
    if not analyzer.library_data:
        print("❌ No library data found. Please run a scan first.")
        return
    
    print(f"📚 Analyzing {len(analyzer.library_data)} projects for deep insights...")
    
    # Generate comprehensive insights
    analyzer.generate_comprehensive_report()
    
    print("✅ Deep project insights generation complete!")
    print("📁 Check the 'deep_insights' directory for detailed analysis.")

if __name__ == "__main__":
    main() 