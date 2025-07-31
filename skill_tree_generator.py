#!/usr/bin/env python3
"""
Skill Tree & Knowledge Base Generator
Creates visual skill trees and knowledge bases from ProjectScanner analysis
"""

import json
import os
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import pandas as pd

class SkillTreeGenerator:
    def __init__(self, library_path: str = "github_library_enhanced/github_library_enhanced.json"):
        self.library_path = library_path
        self.library_data = self.load_library()
        self.skill_tree = {}
        self.knowledge_base = {}
        
    def load_library(self) -> Dict:
        """Load the scanned library data."""
        try:
            with open(self.library_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Library file not found: {self.library_path}")
            return {}
    
    def analyze_technology_stack(self) -> Dict[str, Any]:
        """Analyze technology stack from scanned projects."""
        tech_stack = {
            'languages': Counter(),
            'frameworks': Counter(),
            'libraries': Counter(),
            'tools': Counter(),
            'databases': Counter(),
            'cloud_services': Counter()
        }
        
        # Common technology patterns
        tech_patterns = {
            'web_frameworks': ['flask', 'django', 'fastapi', 'express', 'react', 'vue', 'angular'],
            'databases': ['sqlite', 'postgresql', 'mysql', 'mongodb', 'redis'],
            'cloud': ['aws', 'azure', 'gcp', 'heroku', 'vercel'],
            'ai_ml': ['tensorflow', 'pytorch', 'scikit-learn', 'opencv', 'numpy', 'pandas'],
            'automation': ['selenium', 'beautifulsoup', 'requests', 'pyautogui'],
            'gui': ['tkinter', 'pyqt', 'kivy', 'wxpython', 'electron']
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                for file_path, file_data in repo_data['files'].items():
                    # Language detection
                    if 'language' in file_data:
                        lang = file_data['language']
                        if lang:
                            tech_stack['languages'][lang] += 1
                    
                    # Framework and library detection from file paths and content
                    file_lower = file_path.lower()
                    for category, patterns in tech_patterns.items():
                        for pattern in patterns:
                            if pattern in file_lower:
                                tech_stack[category.replace('_', 's')][pattern] += 1
        
        return tech_stack
    
    def analyze_complexity_patterns(self) -> Dict[str, Any]:
        """Analyze code complexity patterns."""
        complexity_data = {
            'high_complexity_files': [],
            'complexity_distribution': [],
            'maturity_levels': Counter(),
            'agent_types': Counter()
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                for file_path, file_data in repo_data['files'].items():
                    if 'complexity' in file_data:
                        complexity = file_data['complexity']
                        complexity_data['complexity_distribution'].append(complexity)
                        
                        if complexity > 50:  # High complexity threshold
                            complexity_data['high_complexity_files'].append({
                                'file': file_path,
                                'complexity': complexity,
                                'repo': repo_name
                            })
                    
                    # Analyze classes for maturity and agent types
                    if 'classes' in file_data:
                        for class_name, class_info in file_data['classes'].items():
                            if 'maturity' in class_info:
                                complexity_data['maturity_levels'][class_info['maturity']] += 1
                            if 'agent_type' in class_info:
                                complexity_data['agent_types'][class_info['agent_type']] += 1
        
        return complexity_data
    
    def analyze_project_categories(self) -> Dict[str, Any]:
        """Categorize projects by type and domain."""
        categories = {
            'web_applications': [],
            'automation_scripts': [],
            'ai_ml_projects': [],
            'gui_applications': [],
            'data_analysis': [],
            'gaming_mods': [],
            'utilities': [],
            'experimental': []
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict):
                # Analyze project characteristics
                has_gui = any('gui' in file.lower() or 'ui' in file.lower() 
                            for file in repo_data.get('files', {}).keys())
                has_web = any('html' in file.lower() or 'css' in file.lower() or 'js' in file.lower()
                             for file in repo_data.get('files', {}).keys())
                has_ai = any('ai' in file.lower() or 'ml' in file.lower() or 'neural' in file.lower()
                            for file in repo_data.get('files', {}).keys())
                has_automation = any('automation' in file.lower() or 'script' in file.lower()
                                   for file in repo_data.get('files', {}).keys())
                
                project_info = {
                    'name': repo_name,
                    'file_count': len(repo_data.get('files', {})),
                    'avg_complexity': sum(f.get('complexity', 0) for f in repo_data.get('files', {}).values()) / max(len(repo_data.get('files', {})), 1)
                }
                
                # Categorize based on characteristics
                if has_gui:
                    categories['gui_applications'].append(project_info)
                elif has_web:
                    categories['web_applications'].append(project_info)
                elif has_ai:
                    categories['ai_ml_projects'].append(project_info)
                elif has_automation:
                    categories['automation_scripts'].append(project_info)
                elif 'sims' in repo_name.lower() or 'mod' in repo_name.lower():
                    categories['gaming_mods'].append(project_info)
                elif 'data' in repo_name.lower() or 'analysis' in repo_name.lower():
                    categories['data_analysis'].append(project_info)
                elif project_info['file_count'] < 10:
                    categories['utilities'].append(project_info)
                else:
                    categories['experimental'].append(project_info)
        
        return categories
    
    def generate_skill_tree(self) -> Dict[str, Any]:
        """Generate a comprehensive skill tree."""
        tech_stack = self.analyze_technology_stack()
        complexity_data = self.analyze_complexity_patterns()
        categories = self.analyze_project_categories()
        
        skill_tree = {
            'core_technologies': {
                'languages': dict(tech_stack['languages'].most_common(10)),
                'frameworks': dict(tech_stack['frameworks'].most_common(10)),
                'libraries': dict(tech_stack['libraries'].most_common(10))
            },
            'expertise_areas': {
                'web_development': len(categories['web_applications']),
                'automation': len(categories['automation_scripts']),
                'ai_ml': len(categories['ai_ml_projects']),
                'gui_development': len(categories['gui_applications']),
                'data_analysis': len(categories['data_analysis']),
                'gaming_mods': len(categories['gaming_mods'])
            },
            'code_quality': {
                'avg_complexity': sum(complexity_data['complexity_distribution']) / max(len(complexity_data['complexity_distribution']), 1),
                'high_complexity_count': len(complexity_data['high_complexity_files']),
                'maturity_distribution': dict(complexity_data['maturity_levels']),
                'agent_type_distribution': dict(complexity_data['agent_types'])
            },
            'project_evolution': {
                'total_projects': len(self.library_data),
                'project_categories': {k: len(v) for k, v in categories.items()},
                'technology_diversity': len(tech_stack['languages'])
            }
        }
        
        return skill_tree
    
    def generate_knowledge_base(self) -> Dict[str, Any]:
        """Generate a comprehensive knowledge base."""
        knowledge_base = {
            'coding_patterns': self.extract_coding_patterns(),
            'architectural_patterns': self.extract_architectural_patterns(),
            'problem_solving_patterns': self.extract_problem_solving_patterns(),
            'best_practices': self.extract_best_practices(),
            'learning_progression': self.analyze_learning_progression()
        }
        
        return knowledge_base
    
    def extract_coding_patterns(self) -> Dict[str, List]:
        """Extract common coding patterns from the codebase."""
        patterns = {
            'function_patterns': [],
            'class_patterns': [],
            'error_handling': [],
            'naming_conventions': []
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                for file_path, file_data in repo_data['files'].items():
                    if 'functions' in file_data:
                        patterns['function_patterns'].extend(file_data['functions'])
                    
                    if 'classes' in file_data:
                        for class_name, class_info in file_data['classes'].items():
                            patterns['class_patterns'].append({
                                'name': class_name,
                                'methods': class_info.get('methods', []),
                                'maturity': class_info.get('maturity', 'Unknown'),
                                'type': class_info.get('agent_type', 'Unknown')
                            })
        
        return patterns
    
    def extract_architectural_patterns(self) -> Dict[str, Any]:
        """Extract architectural patterns from projects."""
        patterns = {
            'design_patterns': Counter(),
            'project_structure': Counter(),
            'dependency_management': Counter()
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict):
                # Analyze project structure
                files = repo_data.get('files', {})
                file_paths = list(files.keys())
                
                # Detect common patterns
                has_tests = any('test' in path.lower() for path in file_paths)
                has_docs = any('doc' in path.lower() or 'readme' in path.lower() for path in file_paths)
                has_config = any('config' in path.lower() or 'settings' in path.lower() for path in file_paths)
                
                if has_tests:
                    patterns['project_structure']['testing'] += 1
                if has_docs:
                    patterns['project_structure']['documentation'] += 1
                if has_config:
                    patterns['project_structure']['configuration'] += 1
        
        return patterns
    
    def extract_problem_solving_patterns(self) -> Dict[str, Any]:
        """Extract problem-solving patterns from the codebase."""
        patterns = {
            'automation_solutions': [],
            'data_processing': [],
            'user_interface': [],
            'integration_patterns': []
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict):
                repo_name_lower = repo_name.lower()
                
                # Categorize by project name and characteristics
                if 'automation' in repo_name_lower or 'bot' in repo_name_lower:
                    patterns['automation_solutions'].append(repo_name)
                elif 'data' in repo_name_lower or 'analysis' in repo_name_lower:
                    patterns['data_processing'].append(repo_name)
                elif 'gui' in repo_name_lower or 'interface' in repo_name_lower:
                    patterns['user_interface'].append(repo_name)
                elif 'api' in repo_name_lower or 'integration' in repo_name_lower:
                    patterns['integration_patterns'].append(repo_name)
        
        return patterns
    
    def extract_best_practices(self) -> Dict[str, Any]:
        """Extract best practices from the codebase."""
        practices = {
            'code_organization': [],
            'error_handling': [],
            'documentation': [],
            'testing': []
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict):
                files = repo_data.get('files', {})
                
                # Analyze code organization
                has_init_files = any('__init__.py' in path for path in files.keys())
                has_main_files = any('main' in path.lower() for path in files.keys())
                
                if has_init_files:
                    practices['code_organization'].append('Proper package structure')
                if has_main_files:
                    practices['code_organization'].append('Entry point organization')
        
        return practices
    
    def analyze_learning_progression(self) -> Dict[str, Any]:
        """Analyze learning progression over time."""
        progression = {
            'skill_evolution': {},
            'complexity_trends': {},
            'technology_adoption': {}
        }
        
        # This would require timestamp data from repositories
        # For now, we'll analyze based on project characteristics
        projects_by_complexity = []
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                avg_complexity = sum(f.get('complexity', 0) for f in repo_data['files'].values()) / max(len(repo_data['files']), 1)
                projects_by_complexity.append({
                    'name': repo_name,
                    'complexity': avg_complexity,
                    'file_count': len(repo_data['files'])
                })
        
        # Sort by complexity to see progression
        projects_by_complexity.sort(key=lambda x: x['complexity'])
        progression['complexity_trends'] = projects_by_complexity
        
        return progression
    
    def create_visual_skill_tree(self, output_path: str = "skill_tree_visualization.png"):
        """Create a visual representation of the skill tree."""
        skill_tree = self.generate_skill_tree()
        
        # Create a network graph
        G = nx.DiGraph()
        
        # Add main skill categories
        main_skills = ['Core Technologies', 'Expertise Areas', 'Code Quality', 'Project Evolution']
        for skill in main_skills:
            G.add_node(skill, level=0)
        
        # Add sub-skills
        for category, skills in skill_tree.items():
            if isinstance(skills, dict):
                for skill, value in skills.items():
                    if isinstance(value, (int, float)):
                        G.add_node(skill, level=1, value=value)
                        G.add_edge(category.replace('_', ' ').title(), skill)
        
        # Create the visualization
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, 
                              nodelist=[n for n in G.nodes() if G.nodes[n].get('level', 0) == 0],
                              node_color='lightblue', 
                              node_size=3000)
        nx.draw_networkx_nodes(G, pos,
                              nodelist=[n for n in G.nodes() if G.nodes[n].get('level', 0) == 1],
                              node_color='lightgreen',
                              node_size=2000)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True)
        
        # Add labels
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        plt.title("Developer Skill Tree", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"🎨 Skill tree visualization saved to: {output_path}")
    
    def generate_report(self, output_dir: str = "skill_analysis"):
        """Generate comprehensive skill analysis report."""
        os.makedirs(output_dir, exist_ok=True)
        
        skill_tree = self.generate_skill_tree()
        knowledge_base = self.generate_knowledge_base()
        
        # Create visual skill tree
        self.create_visual_skill_tree(f"{output_dir}/skill_tree.png")
        
        # Generate detailed reports
        self.save_skill_tree_report(skill_tree, f"{output_dir}/skill_tree_report.json")
        self.save_knowledge_base_report(knowledge_base, f"{output_dir}/knowledge_base_report.json")
        self.save_summary_report(skill_tree, knowledge_base, f"{output_dir}/summary_report.md")
        
        print(f"📊 Skill analysis reports saved to: {output_dir}/")
    
    def save_skill_tree_report(self, skill_tree: Dict, output_path: str):
        """Save skill tree report to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(skill_tree, f, indent=2, ensure_ascii=False)
    
    def save_knowledge_base_report(self, knowledge_base: Dict, output_path: str):
        """Save knowledge base report to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
    
    def save_summary_report(self, skill_tree: Dict, knowledge_base: Dict, output_path: str):
        """Generate a markdown summary report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 🚀 Developer Skill Analysis Report\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 📊 Skill Tree Summary\n\n")
            
            # Core Technologies
            f.write("### 🔧 Core Technologies\n")
            for tech_type, techs in skill_tree['core_technologies'].items():
                f.write(f"**{tech_type.title()}:**\n")
                for tech, count in list(techs.items())[:5]:  # Top 5
                    f.write(f"- {tech}: {count} occurrences\n")
                f.write("\n")
            
            # Expertise Areas
            f.write("### 🎯 Expertise Areas\n")
            for area, count in skill_tree['expertise_areas'].items():
                f.write(f"- **{area.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            # Code Quality
            f.write("### 📈 Code Quality Metrics\n")
            f.write(f"- **Average Complexity:** {skill_tree['code_quality']['avg_complexity']:.2f}\n")
            f.write(f"- **High Complexity Files:** {skill_tree['code_quality']['high_complexity_count']}\n")
            f.write(f"- **Total Projects:** {skill_tree['project_evolution']['total_projects']}\n")
            f.write("\n")
            
            # Knowledge Base Summary
            f.write("## 🧠 Knowledge Base Summary\n\n")
            
            f.write("### 🏗️ Architectural Patterns\n")
            for pattern_type, patterns in knowledge_base['architectural_patterns'].items():
                f.write(f"**{pattern_type.replace('_', ' ').title()}:**\n")
                for pattern, count in patterns.most_common(5):
                    f.write(f"- {pattern}: {count} projects\n")
                f.write("\n")
            
            f.write("### 💡 Problem-Solving Approaches\n")
            for approach_type, approaches in knowledge_base['problem_solving_patterns'].items():
                f.write(f"**{approach_type.replace('_', ' ').title()}:**\n")
                for approach in approaches[:5]:  # Top 5
                    f.write(f"- {approach}\n")
                f.write("\n")
            
            f.write("## 🎯 Recommendations\n\n")
            f.write("### Strengths to Leverage\n")
            # Add recommendations based on analysis
            f.write("- Focus on your strongest technology areas\n")
            f.write("- Build on successful project patterns\n")
            f.write("- Leverage your unique problem-solving approaches\n\n")
            
            f.write("### Areas for Growth\n")
            f.write("- Explore new technologies outside your comfort zone\n")
            f.write("- Increase code quality and testing practices\n")
            f.write("- Document your knowledge for future reference\n\n")

def main():
    """Main function to run the skill tree generator."""
    print("🌳 Generating Skill Tree & Knowledge Base...")
    
    generator = SkillTreeGenerator()
    
    if not generator.library_data:
        print("❌ No library data found. Please run a scan first.")
        return
    
    print(f"📚 Analyzing {len(generator.library_data)} projects...")
    
    # Generate reports
    generator.generate_report()
    
    print("✅ Skill tree and knowledge base generation complete!")
    print("📁 Check the 'skill_analysis' directory for detailed reports.")

if __name__ == "__main__":
    main() 