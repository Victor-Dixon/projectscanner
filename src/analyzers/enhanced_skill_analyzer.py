#!/usr/bin/env python3
"""
Enhanced Skill Tree & Knowledge Base Generator
Better technology detection and skill analysis from ProjectScanner data
"""

import json
import os
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import re

class EnhancedSkillAnalyzer:
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
    
    def analyze_file_extensions(self) -> Dict[str, Counter]:
        """Analyze file extensions to detect technologies."""
        extensions = Counter()
        languages = Counter()
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                for file_path in repo_data['files'].keys():
                    # Extract file extension
                    if '.' in file_path:
                        ext = file_path.split('.')[-1].lower()
                        extensions[ext] += 1
                        
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
                            languages[lang_map[ext]] += 1
        
        return {'extensions': extensions, 'languages': languages}
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure patterns."""
        patterns = {
            'has_tests': 0,
            'has_docs': 0,
            'has_config': 0,
            'has_requirements': 0,
            'has_package_json': 0,
            'has_docker': 0,
            'has_github_actions': 0,
            'has_readme': 0,
            'has_license': 0
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = list(repo_data['files'].keys())
                file_lower = [f.lower() for f in files]
                
                if any('test' in f for f in file_lower):
                    patterns['has_tests'] += 1
                if any('doc' in f or 'readme' in f for f in file_lower):
                    patterns['has_docs'] += 1
                if any('config' in f or 'settings' in f for f in file_lower):
                    patterns['has_config'] += 1
                if any('requirements' in f for f in file_lower):
                    patterns['has_requirements'] += 1
                if any('package.json' in f for f in file_lower):
                    patterns['has_package_json'] += 1
                if any('docker' in f for f in file_lower):
                    patterns['has_docker'] += 1
                if any('.github' in f for f in file_lower):
                    patterns['has_github_actions'] += 1
                if any('readme' in f for f in file_lower):
                    patterns['has_readme'] += 1
                if any('license' in f for f in file_lower):
                    patterns['has_license'] += 1
        
        return patterns
    
    def analyze_project_categories(self) -> Dict[str, List]:
        """Categorize projects by type and characteristics."""
        categories = {
            'web_projects': [],
            'automation_projects': [],
            'ai_ml_projects': [],
            'gui_projects': [],
            'data_projects': [],
            'gaming_projects': [],
            'utility_projects': [],
            'experimental_projects': []
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict):
                repo_lower = repo_name.lower()
                files = repo_data.get('files', {})
                file_count = len(files)
                
                # Calculate average complexity
                complexities = [f.get('complexity', 0) for f in files.values()]
                avg_complexity = sum(complexities) / max(len(complexities), 1)
                
                project_info = {
                    'name': repo_name,
                    'file_count': file_count,
                    'avg_complexity': avg_complexity,
                    'total_complexity': sum(complexities)
                }
                
                # Categorize based on repository name and characteristics
                if any(keyword in repo_lower for keyword in ['web', 'site', 'app', 'api']):
                    categories['web_projects'].append(project_info)
                elif any(keyword in repo_lower for keyword in ['bot', 'automation', 'script', 'auto']):
                    categories['automation_projects'].append(project_info)
                elif any(keyword in repo_lower for keyword in ['ai', 'ml', 'neural', 'gpt', 'model']):
                    categories['ai_ml_projects'].append(project_info)
                elif any(keyword in repo_lower for keyword in ['gui', 'interface', 'tkinter', 'pyqt']):
                    categories['gui_projects'].append(project_info)
                elif any(keyword in repo_lower for keyword in ['data', 'analysis', 'analytics']):
                    categories['data_projects'].append(project_info)
                elif any(keyword in repo_lower for keyword in ['sims', 'mod', 'game', 'gaming']):
                    categories['gaming_projects'].append(project_info)
                elif file_count < 5:
                    categories['utility_projects'].append(project_info)
                else:
                    categories['experimental_projects'].append(project_info)
        
        return categories
    
    def analyze_complexity_distribution(self) -> Dict[str, Any]:
        """Analyze code complexity patterns."""
        all_complexities = []
        high_complexity_files = []
        repo_complexities = []
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                repo_complexities_list = []
                
                for file_path, file_data in repo_data['files'].items():
                    complexity = file_data.get('complexity', 0)
                    all_complexities.append(complexity)
                    repo_complexities_list.append(complexity)
                    
                    if complexity > 30:  # High complexity threshold
                        high_complexity_files.append({
                            'file': file_path,
                            'complexity': complexity,
                            'repo': repo_name
                        })
                
                if repo_complexities_list:
                    repo_complexities.append({
                        'repo': repo_name,
                        'avg_complexity': sum(repo_complexities_list) / len(repo_complexities_list),
                        'max_complexity': max(repo_complexities_list),
                        'file_count': len(repo_complexities_list)
                    })
        
        return {
            'all_complexities': all_complexities,
            'high_complexity_files': high_complexity_files,
            'repo_complexities': repo_complexities,
            'avg_complexity': sum(all_complexities) / max(len(all_complexities), 1),
            'max_complexity': max(all_complexities) if all_complexities else 0
        }
    
    def analyze_function_patterns(self) -> Dict[str, Any]:
        """Analyze function and class patterns."""
        functions = []
        classes = []
        maturity_levels = Counter()
        agent_types = Counter()
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                for file_path, file_data in repo_data['files'].items():
                    # Collect functions
                    if 'functions' in file_data:
                        functions.extend(file_data['functions'])
                    
                    # Collect classes
                    if 'classes' in file_data:
                        for class_name, class_info in file_data['classes'].items():
                            classes.append({
                                'name': class_name,
                                'file': file_path,
                                'repo': repo_name,
                                'methods': class_info.get('methods', []),
                                'maturity': class_info.get('maturity', 'Unknown'),
                                'agent_type': class_info.get('agent_type', 'Unknown')
                            })
                            
                            if 'maturity' in class_info:
                                maturity_levels[class_info['maturity']] += 1
                            if 'agent_type' in class_info:
                                agent_types[class_info['agent_type']] += 1
        
        return {
            'functions': functions,
            'classes': classes,
            'maturity_levels': dict(maturity_levels),
            'agent_types': dict(agent_types),
            'function_count': len(functions),
            'class_count': len(classes)
        }
    
    def generate_skill_tree(self) -> Dict[str, Any]:
        """Generate comprehensive skill tree."""
        extensions_data = self.analyze_file_extensions()
        project_structure = self.analyze_project_structure()
        categories = self.analyze_project_categories()
        complexity_data = self.analyze_complexity_distribution()
        function_data = self.analyze_function_patterns()
        
        skill_tree = {
            'core_technologies': {
                'languages': dict(extensions_data['languages'].most_common(10)),
                'file_types': dict(extensions_data['extensions'].most_common(15))
            },
            'expertise_areas': {
                'web_development': len(categories['web_projects']),
                'automation': len(categories['automation_projects']),
                'ai_ml': len(categories['ai_ml_projects']),
                'gui_development': len(categories['gui_projects']),
                'data_analysis': len(categories['data_projects']),
                'gaming_mods': len(categories['gaming_projects']),
                'utilities': len(categories['utility_projects']),
                'experimental': len(categories['experimental_projects'])
            },
            'code_quality': {
                'avg_complexity': complexity_data['avg_complexity'],
                'max_complexity': complexity_data['max_complexity'],
                'high_complexity_count': len(complexity_data['high_complexity_files']),
                'total_files': len(complexity_data['all_complexities'])
            },
            'development_practices': {
                'projects_with_tests': project_structure['has_tests'],
                'projects_with_docs': project_structure['has_docs'],
                'projects_with_config': project_structure['has_config'],
                'projects_with_requirements': project_structure['has_requirements'],
                'projects_with_readme': project_structure['has_readme']
            },
            'code_architecture': {
                'total_functions': function_data['function_count'],
                'total_classes': function_data['class_count'],
                'maturity_distribution': function_data['maturity_levels'],
                'agent_type_distribution': function_data['agent_types']
            },
            'project_evolution': {
                'total_projects': len(self.library_data),
                'project_categories': {k: len(v) for k, v in categories.items()},
                'technology_diversity': len(extensions_data['languages'])
            }
        }
        
        return skill_tree
    
    def generate_knowledge_base(self) -> Dict[str, Any]:
        """Generate comprehensive knowledge base."""
        categories = self.analyze_project_categories()
        complexity_data = self.analyze_complexity_distribution()
        function_data = self.analyze_function_patterns()
        
        knowledge_base = {
            'project_patterns': {
                'most_complex_projects': sorted(complexity_data['repo_complexities'], 
                                              key=lambda x: x['avg_complexity'], reverse=True)[:10],
                'largest_projects': sorted(complexity_data['repo_complexities'], 
                                         key=lambda x: x['file_count'], reverse=True)[:10],
                'project_categories': categories
            },
            'coding_patterns': {
                'function_patterns': function_data['functions'][:50],  # Top 50 functions
                'class_patterns': function_data['classes'][:50],  # Top 50 classes
                'maturity_breakdown': function_data['maturity_levels'],
                'agent_type_breakdown': function_data['agent_types']
            },
            'technology_insights': {
                'language_preferences': self.analyze_file_extensions()['languages'].most_common(10),
                'file_type_distribution': self.analyze_file_extensions()['extensions'].most_common(15)
            },
            'development_insights': {
                'complexity_trends': complexity_data,
                'project_structure_analysis': self.analyze_project_structure()
            }
        }
        
        return knowledge_base
    
    def create_visual_skill_tree(self, output_path: str = "skill_analysis/enhanced_skill_tree.png"):
        """Create a visual representation of the skill tree."""
        skill_tree = self.generate_skill_tree()
        
        # Create a network graph
        G = nx.DiGraph()
        
        # Add main skill categories
        main_skills = ['Core Technologies', 'Expertise Areas', 'Code Quality', 'Development Practices']
        for skill in main_skills:
            G.add_node(skill, level=0)
        
        # Add sub-skills with values
        for category, skills in skill_tree.items():
            if isinstance(skills, dict):
                for skill, value in skills.items():
                    if isinstance(value, (int, float)) and value > 0:
                        G.add_node(skill.replace('_', ' ').title(), level=1, value=value)
                        G.add_edge(category.replace('_', ' ').title(), skill.replace('_', ' ').title())
        
        # Create the visualization
        plt.figure(figsize=(20, 16))
        pos = nx.spring_layout(G, k=4, iterations=100)
        
        # Draw nodes with different colors based on level
        main_nodes = [n for n in G.nodes() if G.nodes[n].get('level', 0) == 0]
        sub_nodes = [n for n in G.nodes() if G.nodes[n].get('level', 0) == 1]
        
        nx.draw_networkx_nodes(G, pos, nodelist=main_nodes, node_color='lightblue', node_size=4000)
        nx.draw_networkx_nodes(G, pos, nodelist=sub_nodes, node_color='lightgreen', node_size=3000)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)
        
        # Add labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        plt.title("Enhanced Developer Skill Tree", fontsize=20, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"🎨 Enhanced skill tree visualization saved to: {output_path}")
    
    def generate_enhanced_report(self, output_dir: str = "skill_analysis"):
        """Generate comprehensive enhanced skill analysis report."""
        os.makedirs(output_dir, exist_ok=True)
        
        skill_tree = self.generate_skill_tree()
        knowledge_base = self.generate_knowledge_base()
        
        # Create visual skill tree
        self.create_visual_skill_tree(f"{output_dir}/enhanced_skill_tree.png")
        
        # Generate detailed reports
        self.save_skill_tree_report(skill_tree, f"{output_dir}/enhanced_skill_tree_report.json")
        self.save_knowledge_base_report(knowledge_base, f"{output_dir}/enhanced_knowledge_base_report.json")
        self.save_enhanced_summary_report(skill_tree, knowledge_base, f"{output_dir}/enhanced_summary_report.md")
        
        print(f"📊 Enhanced skill analysis reports saved to: {output_dir}/")
    
    def save_skill_tree_report(self, skill_tree: Dict, output_path: str):
        """Save skill tree report to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(skill_tree, f, indent=2, ensure_ascii=False)
    
    def save_knowledge_base_report(self, knowledge_base: Dict, output_path: str):
        """Save knowledge base report to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
    
    def save_enhanced_summary_report(self, skill_tree: Dict, knowledge_base: Dict, output_path: str):
        """Generate an enhanced markdown summary report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 🚀 Enhanced Developer Skill Analysis Report\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 📊 Skill Tree Summary\n\n")
            
            # Core Technologies
            f.write("### 🔧 Core Technologies\n")
            for tech_type, techs in skill_tree['core_technologies'].items():
                f.write(f"**{tech_type.title()}:**\n")
                for tech, count in list(techs.items())[:10]:  # Top 10
                    if count > 0:
                        f.write(f"- {tech}: {count} files\n")
                f.write("\n")
            
            # Expertise Areas
            f.write("### 🎯 Expertise Areas\n")
            for area, count in skill_tree['expertise_areas'].items():
                if count > 0:
                    f.write(f"- **{area.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            # Code Quality
            f.write("### 📈 Code Quality Metrics\n")
            f.write(f"- **Average Complexity:** {skill_tree['code_quality']['avg_complexity']:.2f}\n")
            f.write(f"- **Max Complexity:** {skill_tree['code_quality']['max_complexity']}\n")
            f.write(f"- **High Complexity Files:** {skill_tree['code_quality']['high_complexity_count']}\n")
            f.write(f"- **Total Files Analyzed:** {skill_tree['code_quality']['total_files']}\n")
            f.write(f"- **Total Projects:** {skill_tree['project_evolution']['total_projects']}\n")
            f.write("\n")
            
            # Development Practices
            f.write("### 🛠️ Development Practices\n")
            for practice, count in skill_tree['development_practices'].items():
                if count > 0:
                    f.write(f"- **{practice.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            # Code Architecture
            f.write("### 🏗️ Code Architecture\n")
            f.write(f"- **Total Functions:** {skill_tree['code_architecture']['total_functions']}\n")
            f.write(f"- **Total Classes:** {skill_tree['code_architecture']['total_classes']}\n")
            f.write("\n")
            
            # Knowledge Base Summary
            f.write("## 🧠 Knowledge Base Summary\n\n")
            
            f.write("### 🏆 Most Complex Projects\n")
            for i, project in enumerate(knowledge_base['project_patterns']['most_complex_projects'][:5], 1):
                f.write(f"{i}. **{project['repo']}** (Avg Complexity: {project['avg_complexity']:.2f})\n")
            f.write("\n")
            
            f.write("### 📁 Largest Projects\n")
            for i, project in enumerate(knowledge_base['project_patterns']['largest_projects'][:5], 1):
                f.write(f"{i}. **{project['repo']}** ({project['file_count']} files)\n")
            f.write("\n")
            
            f.write("### 🎯 Project Categories\n")
            for category, projects in knowledge_base['project_patterns']['project_categories'].items():
                if projects:
                    f.write(f"**{category.replace('_', ' ').title()}:** {len(projects)} projects\n")
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
    """Main function to run the enhanced skill analyzer."""
    print("🌳 Generating Enhanced Skill Tree & Knowledge Base...")
    
    analyzer = EnhancedSkillAnalyzer()
    
    if not analyzer.library_data:
        print("❌ No library data found. Please run a scan first.")
        return
    
    print(f"📚 Analyzing {len(analyzer.library_data)} projects...")
    
    # Generate reports
    analyzer.generate_enhanced_report()
    
    print("✅ Enhanced skill tree and knowledge base generation complete!")
    print("📁 Check the 'skill_analysis' directory for detailed reports.")

if __name__ == "__main__":
    main() 