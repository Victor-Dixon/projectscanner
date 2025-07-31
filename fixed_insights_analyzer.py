#!/usr/bin/env python3
"""
Fixed Insights Analyzer
Properly extracts function and class data from the nested analysis structure
"""

import json
import os
from collections import defaultdict, Counter
from typing import Dict, Any, List
from datetime import datetime

class FixedInsightsAnalyzer:
    def __init__(self, library_path: str = "github_library_enhanced/github_library_enhanced.json"):
        self.library_path = library_path
        self.library_data = self.load_library()
        
    def load_library(self) -> Dict[str, Any]:
        """Load the enhanced library data."""
        try:
            with open(self.library_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Library file not found: {self.library_path}")
            return {}
        except Exception as e:
            print(f"❌ Error loading library: {e}")
            return {}
    
    def analyze_project_details(self) -> Dict[str, Any]:
        """Analyze project details with proper data extraction."""
        print("🔍 Generating Fixed Project Insights...")
        print(f"📚 Analyzing {len(self.library_data)} projects with proper data extraction.")
        
        total_files = 0
        total_functions = 0
        total_classes = 0
        total_complexity = 0
        project_categories = Counter()
        largest_projects = []
        most_complex_projects = []
        
        # Track detailed file analysis
        file_analysis = defaultdict(list)
        technology_stack = Counter()
        languages = Counter()
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'analysis_data' in repo_data:
                analysis_data = repo_data['analysis_data']
                
                if analysis_data and isinstance(analysis_data, dict):
                    project_files = 0
                    project_functions = 0
                    project_classes = 0
                    project_complexity = 0
                    
                    # Analyze each file in the project
                    for file_path, file_data in analysis_data.items():
                        if isinstance(file_data, dict):
                            project_files += 1
                            
                            # Extract functions
                            functions = file_data.get('functions', [])
                            if functions:
                                project_functions += len(functions)
                                total_functions += len(functions)
                            
                            # Extract classes
                            classes = file_data.get('classes', {})
                            if classes:
                                project_classes += len(classes)
                                total_classes += len(classes)
                            
                            # Extract complexity
                            complexity = file_data.get('complexity', 0)
                            if isinstance(complexity, (int, float)):
                                project_complexity += complexity
                                total_complexity += complexity
                            
                            # Extract language
                            language = file_data.get('language', '')
                            if language:
                                languages[language] += 1
                            
                            # Track file analysis
                            file_analysis[repo_name].append({
                                'file': file_path,
                                'functions': len(functions),
                                'classes': len(classes),
                                'complexity': complexity,
                                'language': language
                            })
                    
                    total_files += project_files
                    
                    # Categorize project
                    category = self.categorize_project(repo_name, repo_data)
                    project_categories[category] += 1
                    
                    # Track largest projects
                    if project_files > 0:
                        largest_projects.append((repo_name, project_files))
                    
                    # Track most complex projects
                    if project_complexity > 0:
                        most_complex_projects.append((repo_name, project_complexity))
                    
                    # Extract technology stack from file paths
                    self.extract_technology_stack(repo_name, analysis_data, technology_stack)
        
        # Sort projects by size and complexity
        largest_projects.sort(key=lambda x: x[1], reverse=True)
        most_complex_projects.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'project_overview': {
                'total_projects': len(self.library_data),
                'total_files': total_files,
                'total_functions': total_functions,
                'total_classes': total_classes,
                'total_complexity': total_complexity,
                'private_projects': sum(1 for repo in self.library_data.values() if repo.get('is_private', False)),
                'public_projects': sum(1 for repo in self.library_data.values() if not repo.get('is_private', False)),
                'project_categories': dict(project_categories),
                'largest_projects': largest_projects[:10],
                'most_complex_projects': most_complex_projects[:10],
                'languages': dict(languages),
                'technology_stack': dict(technology_stack)
            },
            'detailed_analysis': dict(file_analysis),
            'technology_analysis': {
                'languages': dict(languages),
                'frameworks': dict(technology_stack),
                'most_used_languages': languages.most_common(10),
                'most_used_frameworks': technology_stack.most_common(10)
            }
        }
    
    def categorize_project(self, repo_name: str, repo_data: Dict) -> str:
        """Categorize project based on name and description."""
        repo_lower = repo_name.lower()
        description = (repo_data.get('description') or '').lower()
        
        # Check for specific categories
        if any(word in repo_lower for word in ['bot', 'automation', 'auto']):
            return 'automation_bot'
        elif any(word in repo_lower for word in ['ai', 'ml', 'machine', 'learning', 'neural']):
            return 'ai_ml'
        elif any(word in repo_lower for word in ['game', 'gaming', 'mod']):
            return 'gaming'
        elif any(word in repo_lower for word in ['web', 'site', 'app', 'frontend', 'backend']):
            return 'web_application'
        elif any(word in repo_lower for word in ['util', 'tool', 'helper']):
            return 'utility'
        elif repo_data.get('file_count', 0) < 10:
            return 'micro_project'
        else:
            return 'general_application'
    
    def extract_technology_stack(self, repo_name: str, analysis_data: Dict, technology_stack: Counter):
        """Extract technology stack from file paths and content."""
        for file_path in analysis_data.keys():
            file_lower = file_path.lower()
            
            # Framework detection
            if any(fw in file_lower for fw in ['django', 'flask', 'fastapi']):
                technology_stack['Django/Flask/FastAPI'] += 1
            elif any(fw in file_lower for fw in ['react', 'vue', 'angular']):
                technology_stack['React/Vue/Angular'] += 1
            elif any(fw in file_lower for fw in ['tensorflow', 'pytorch', 'keras']):
                technology_stack['TensorFlow/PyTorch'] += 1
            elif any(fw in file_lower for fw in ['selenium', 'beautifulsoup', 'requests']):
                technology_stack['Web Scraping'] += 1
            elif any(fw in file_lower for fw in ['sqlalchemy', 'sqlite', 'postgres']):
                technology_stack['Database'] += 1
            elif any(fw in file_lower for fw in ['git', 'github']):
                technology_stack['Version Control'] += 1
    
    def generate_summary_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a comprehensive summary report."""
        overview = analysis_results['project_overview']
        
        report = f"""# 🔍 Fixed Project Insights Analysis

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Project Overview

- **Total Projects:** {overview['total_projects']}
- **Total Files:** {overview['total_files']}
- **Total Functions:** {overview['total_functions']}
- **Total Classes:** {overview['total_classes']}
- **Total Complexity:** {overview['total_complexity']:.2f}
- **Private Projects:** {overview['private_projects']}
- **Public Projects:** {overview['public_projects']}

### 🎯 Project Categories
"""
        
        for category, count in overview['project_categories'].items():
            report += f"- **{category.replace('_', ' ').title()}:** {count} projects\n"
        
        report += "\n### 🏆 Largest Projects\n"
        for i, (project, file_count) in enumerate(overview['largest_projects'][:5], 1):
            report += f"{i}. **{project}** ({file_count} files)\n"
        
        report += "\n### 🧠 Most Complex Projects\n"
        for i, (project, complexity) in enumerate(overview['most_complex_projects'][:5], 1):
            report += f"{i}. **{project}** (Complexity: {complexity:.2f})\n"
        
        report += "\n### 💻 Programming Languages\n"
        for language, count in overview['languages'].items():
            if count > 0:
                report += f"- **{language}:** {count} files\n"
        
        report += "\n### 🛠️ Technology Stack\n"
        for tech, count in overview['technology_stack'].items():
            if count > 0:
                report += f"- **{tech}:** {count} files\n"
        
        report += "\n## 🎯 Key Insights\n"
        
        if overview['total_functions'] > 0:
            report += f"- **Function Development:** {overview['total_functions']} functions across all projects\n"
        if overview['total_classes'] > 0:
            report += f"- **Object-Oriented Development:** {overview['total_classes']} classes across all projects\n"
        if overview['total_complexity'] > 0:
            report += f"- **Code Complexity:** Average complexity of {overview['total_complexity']/overview['total_files']:.2f} per file\n"
        
        report += f"- **Project Diversity:** {len(overview['project_categories'])} different project categories\n"
        report += f"- **Technology Breadth:** {len(overview['technology_stack'])} different technologies used\n"
        
        return report
    
    def save_reports(self, analysis_results: Dict[str, Any]):
        """Save analysis reports to files."""
        # Create output directory
        os.makedirs('fixed_insights', exist_ok=True)
        
        # Save JSON report
        with open('fixed_insights/fixed_insights.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        # Save summary report
        summary = self.generate_summary_report(analysis_results)
        with open('fixed_insights/fixed_insights_summary.md', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print("✅ Fixed insights reports saved to: fixed_insights/")
    
    def run_analysis(self):
        """Run the complete fixed analysis."""
        if not self.library_data:
            print("❌ No library data available")
            return
        
        analysis_results = self.analyze_project_details()
        self.save_reports(analysis_results)
        
        # Print key findings
        overview = analysis_results['project_overview']
        print(f"\n🎯 **KEY FINDINGS:**")
        print(f"📊 Total Files: {overview['total_files']}")
        print(f"🔧 Total Functions: {overview['total_functions']}")
        print(f"🏗️ Total Classes: {overview['total_classes']}")
        print(f"🧠 Total Complexity: {overview['total_complexity']:.2f}")
        
        if overview['total_functions'] > 0:
            print("✅ SUCCESS: Function data extracted!")
        if overview['total_classes'] > 0:
            print("✅ SUCCESS: Class data extracted!")
        if overview['total_complexity'] > 0:
            print("✅ SUCCESS: Complexity data extracted!")
        
        print("\n✅ Fixed insights analysis complete!")

def main():
    analyzer = FixedInsightsAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 