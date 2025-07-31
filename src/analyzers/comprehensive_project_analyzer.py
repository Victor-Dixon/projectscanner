#!/usr/bin/env python3
"""
Comprehensive Project Analyzer
Extracts detailed insights from scanned project data
"""

import json
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
from datetime import datetime

class ComprehensiveProjectAnalyzer:
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
    
    def analyze_project_details(self) -> Dict[str, Any]:
        """Analyze detailed project information."""
        analysis = {
            'project_summary': {},
            'technology_usage': defaultdict(Counter),
            'code_metrics': defaultdict(list),
            'development_patterns': defaultdict(Counter),
            'project_categories': defaultdict(list),
            'complexity_analysis': defaultdict(list)
        }
        
        total_files = 0
        total_functions = 0
        total_classes = 0
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                file_count = len(files)
                total_files += file_count
                
                # Project summary
                project_info = {
                    'name': repo_name,
                    'file_count': file_count,
                    'total_complexity': 0,
                    'avg_complexity': 0,
                    'max_complexity': 0,
                    'function_count': 0,
                    'class_count': 0,
                    'languages': set(),
                    'frameworks': set(),
                    'project_type': self.categorize_project(repo_name, files)
                }
                
                # Analyze each file
                complexities = []
                for file_path, file_data in files.items():
                    # Complexity analysis
                    complexity = file_data.get('complexity', 0)
                    complexities.append(complexity)
                    project_info['total_complexity'] += complexity
                    
                    # Language detection
                    if 'language' in file_data and file_data['language']:
                        project_info['languages'].add(file_data['language'])
                    
                    # Function and class counting
                    if 'functions' in file_data:
                        project_info['function_count'] += len(file_data['functions'])
                        total_functions += len(file_data['functions'])
                    
                    if 'classes' in file_data:
                        project_info['class_count'] += len(file_data['classes'])
                        total_classes += len(file_data['classes'])
                    
                    # Technology detection from file path
                    self.detect_technologies(file_path, project_info)
                
                # Calculate averages
                if complexities:
                    project_info['avg_complexity'] = sum(complexities) / len(complexities)
                    project_info['max_complexity'] = max(complexities)
                
                # Store project info
                analysis['project_summary'][repo_name] = project_info
                analysis['project_categories'][project_info['project_type']].append(repo_name)
                
                # Technology usage
                for lang in project_info['languages']:
                    analysis['technology_usage']['languages'][lang] += 1
                for framework in project_info['frameworks']:
                    analysis['technology_usage']['frameworks'][framework] += 1
                
                # Code metrics
                analysis['code_metrics']['complexities'].append(project_info['avg_complexity'])
                analysis['code_metrics']['file_counts'].append(file_count)
                analysis['code_metrics']['function_counts'].append(project_info['function_count'])
                analysis['code_metrics']['class_counts'].append(project_info['class_count'])
                
                # Development patterns
                self.analyze_development_patterns(repo_name, files, analysis)
        
        # Overall statistics
        analysis['overall_stats'] = {
            'total_projects': len(self.library_data),
            'total_files': total_files,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'avg_files_per_project': total_files / max(len(self.library_data), 1),
            'avg_functions_per_project': total_functions / max(len(self.library_data), 1),
            'avg_classes_per_project': total_classes / max(len(self.library_data), 1)
        }
        
        return analysis
    
    def categorize_project(self, repo_name: str, files: Dict) -> str:
        """Categorize project based on name and file patterns."""
        repo_lower = repo_name.lower()
        file_paths = list(files.keys())
        
        # Check for specific patterns
        if any('bot' in repo_lower for _ in [repo_lower]):
            return 'automation_bot'
        elif any('web' in repo_lower or 'site' in repo_lower or 'app' in repo_lower):
            return 'web_application'
        elif any('ai' in repo_lower or 'ml' in repo_lower or 'gpt' in repo_lower):
            return 'ai_ml'
        elif any('gui' in repo_lower or 'interface' in repo_lower):
            return 'gui_application'
        elif any('data' in repo_lower or 'analysis' in repo_lower):
            return 'data_analysis'
        elif any('sims' in repo_lower or 'mod' in repo_lower or 'game' in repo_lower):
            return 'gaming'
        elif any('tool' in repo_lower or 'util' in repo_lower):
            return 'utility'
        elif len(files) < 5:
            return 'micro_project'
        else:
            return 'general_application'
    
    def detect_technologies(self, file_path: str, project_info: Dict):
        """Detect technologies from file path."""
        file_lower = file_path.lower()
        
        # Framework detection
        frameworks = {
            'flask': 'Flask', 'django': 'Django', 'fastapi': 'FastAPI',
            'react': 'React', 'vue': 'Vue', 'angular': 'Angular',
            'express': 'Express', 'bootstrap': 'Bootstrap',
            'selenium': 'Selenium', 'beautifulsoup': 'BeautifulSoup',
            'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
            'opencv': 'OpenCV', 'numpy': 'NumPy', 'pandas': 'Pandas',
            'tkinter': 'Tkinter', 'pyqt': 'PyQt', 'kivy': 'Kivy'
        }
        
        for pattern, framework in frameworks.items():
            if pattern in file_lower:
                project_info['frameworks'].add(framework)
    
    def analyze_development_patterns(self, repo_name: str, files: Dict, analysis: Dict):
        """Analyze development patterns in the project."""
        file_paths = list(files.keys())
        
        # Testing patterns
        if any('test' in path.lower() for path in file_paths):
            analysis['development_patterns']['testing']['has_tests'] += 1
        if any('pytest' in path.lower() for path in file_paths):
            analysis['development_patterns']['testing']['pytest'] += 1
        
        # Documentation patterns
        if any('readme' in path.lower() for path in file_paths):
            analysis['development_patterns']['documentation']['has_readme'] += 1
        if any('doc' in path.lower() for path in file_paths):
            analysis['development_patterns']['documentation']['has_docs'] += 1
        
        # Configuration patterns
        if any('config' in path.lower() for path in file_paths):
            analysis['development_patterns']['configuration']['has_config'] += 1
        if any('requirements' in path.lower() for path in file_paths):
            analysis['development_patterns']['configuration']['has_requirements'] += 1
        
        # Project structure patterns
        if any('__init__.py' in path for path in file_paths):
            analysis['development_patterns']['structure']['python_package'] += 1
        if any('main.py' in path for path in file_paths):
            analysis['development_patterns']['structure']['has_main'] += 1
        
        # Project size patterns
        if len(files) > 50:
            analysis['development_patterns']['size']['large_project'] += 1
        elif len(files) > 20:
            analysis['development_patterns']['size']['medium_project'] += 1
        elif len(files) > 5:
            analysis['development_patterns']['size']['small_project'] += 1
        else:
            analysis['development_patterns']['size']['micro_project'] += 1
    
    def generate_detailed_insights(self) -> Dict[str, Any]:
        """Generate detailed insights from the analysis."""
        analysis = self.analyze_project_details()
        
        insights = {
            'project_overview': self.create_project_overview(analysis),
            'technology_insights': self.create_technology_insights(analysis),
            'development_insights': self.create_development_insights(analysis),
            'skill_insights': self.create_skill_insights(analysis),
            'recommendations': self.create_recommendations(analysis)
        }
        
        return insights
    
    def create_project_overview(self, analysis: Dict) -> Dict[str, Any]:
        """Create project overview insights."""
        overall_stats = analysis['overall_stats']
        project_categories = analysis['project_categories']
        
        # Find most common project types
        category_counts = {cat: len(projects) for cat, projects in project_categories.items()}
        most_common_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Find largest projects
        project_summaries = analysis['project_summary']
        largest_projects = sorted(
            [(name, info['file_count']) for name, info in project_summaries.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        # Find most complex projects
        most_complex_projects = sorted(
            [(name, info['avg_complexity']) for name, info in project_summaries.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        return {
            'total_projects': overall_stats['total_projects'],
            'total_files': overall_stats['total_files'],
            'total_functions': overall_stats['total_functions'],
            'total_classes': overall_stats['total_classes'],
            'project_categories': category_counts,
            'most_common_categories': most_common_categories,
            'largest_projects': largest_projects,
            'most_complex_projects': most_complex_projects
        }
    
    def create_technology_insights(self, analysis: Dict) -> Dict[str, Any]:
        """Create technology insights."""
        tech_usage = analysis['technology_usage']
        
        return {
            'languages': dict(tech_usage['languages'].most_common(10)),
            'frameworks': dict(tech_usage['frameworks'].most_common(10)),
            'language_diversity': len(tech_usage['languages']),
            'framework_diversity': len(tech_usage['frameworks'])
        }
    
    def create_development_insights(self, analysis: Dict) -> Dict[str, Any]:
        """Create development practice insights."""
        dev_patterns = analysis['development_patterns']
        
        return {
            'testing_practices': dict(dev_patterns['testing']),
            'documentation_practices': dict(dev_patterns['documentation']),
            'configuration_practices': dict(dev_patterns['configuration']),
            'project_structure': dict(dev_patterns['structure']),
            'project_sizes': dict(dev_patterns['size'])
        }
    
    def create_skill_insights(self, analysis: Dict) -> Dict[str, Any]:
        """Create skill-based insights."""
        project_categories = analysis['project_categories']
        project_summaries = analysis['project_summary']
        
        # Calculate skill strengths
        skill_areas = {}
        for category, projects in project_categories.items():
            if projects:
                avg_complexity = sum(project_summaries[proj]['avg_complexity'] for proj in projects) / len(projects)
                avg_files = sum(project_summaries[proj]['file_count'] for proj in projects) / len(projects)
                skill_areas[category] = {
                    'project_count': len(projects),
                    'avg_complexity': avg_complexity,
                    'avg_files': avg_files
                }
        
        return {
            'skill_areas': skill_areas,
            'strongest_areas': sorted(skill_areas.items(), key=lambda x: x[1]['project_count'], reverse=True),
            'most_complex_areas': sorted(skill_areas.items(), key=lambda x: x[1]['avg_complexity'], reverse=True)
        }
    
    def create_recommendations(self, analysis: Dict) -> Dict[str, Any]:
        """Create personalized recommendations."""
        skill_insights = self.create_skill_insights(analysis)
        dev_insights = self.create_development_insights(analysis)
        
        recommendations = {
            'strengths': [],
            'growth_areas': [],
            'next_steps': []
        }
        
        # Identify strengths
        strongest_areas = skill_insights['strongest_areas']
        if strongest_areas:
            top_area = strongest_areas[0]
            recommendations['strengths'].append(f"Strong expertise in {top_area[0].replace('_', ' ')} ({top_area[1]['project_count']} projects)")
        
        # Identify growth areas
        if not dev_insights['testing_practices'].get('has_tests', 0):
            recommendations['growth_areas'].append("Add more testing to your projects")
        if not dev_insights['documentation_practices'].get('has_readme', 0):
            recommendations['growth_areas'].append("Improve project documentation")
        
        # Next steps
        recommendations['next_steps'].append("Focus on your strongest areas")
        recommendations['next_steps'].append("Explore new technologies")
        recommendations['next_steps'].append("Build larger, more complex projects")
        
        return recommendations
    
    def generate_comprehensive_report(self, output_dir: str = "comprehensive_analysis"):
        """Generate comprehensive analysis report."""
        os.makedirs(output_dir, exist_ok=True)
        
        insights = self.generate_detailed_insights()
        
        # Save detailed reports
        self.save_insights_report(insights, f"{output_dir}/comprehensive_insights.json")
        self.save_summary_report(insights, f"{output_dir}/comprehensive_summary.md")
        
        print(f"📊 Comprehensive analysis reports saved to: {output_dir}/")
    
    def save_insights_report(self, insights: Dict, output_path: str):
        """Save insights report to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
    
    def save_summary_report(self, insights: Dict, output_path: str):
        """Generate a comprehensive markdown summary report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 🔍 Comprehensive Project Analysis\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Project Overview
            overview = insights['project_overview']
            f.write("## 📊 Project Overview\n\n")
            f.write(f"- **Total Projects:** {overview['total_projects']}\n")
            f.write(f"- **Total Files:** {overview['total_files']}\n")
            f.write(f"- **Total Functions:** {overview['total_functions']}\n")
            f.write(f"- **Total Classes:** {overview['total_classes']}\n\n")
            
            f.write("### 🎯 Project Categories\n")
            for category, count in overview['project_categories'].items():
                f.write(f"- **{category.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            f.write("### 🏆 Largest Projects\n")
            for i, (project, file_count) in enumerate(overview['largest_projects'][:5], 1):
                f.write(f"{i}. **{project}** ({file_count} files)\n")
            f.write("\n")
            
            f.write("### 🧠 Most Complex Projects\n")
            for i, (project, complexity) in enumerate(overview['most_complex_projects'][:5], 1):
                f.write(f"{i}. **{project}** (Complexity: {complexity:.2f})\n")
            f.write("\n")
            
            # Technology Insights
            tech_insights = insights['technology_insights']
            f.write("## 🔧 Technology Stack\n\n")
            
            f.write("### 💻 Programming Languages\n")
            for lang, count in tech_insights['languages'].items():
                f.write(f"- **{lang}:** {count} projects\n")
            f.write("\n")
            
            f.write("### 🛠️ Frameworks & Libraries\n")
            for framework, count in tech_insights['frameworks'].items():
                f.write(f"- **{framework}:** {count} occurrences\n")
            f.write("\n")
            
            # Development Insights
            dev_insights = insights['development_insights']
            f.write("## 🛠️ Development Practices\n\n")
            
            f.write("### 🧪 Testing Practices\n")
            for practice, count in dev_insights['testing_practices'].items():
                f.write(f"- **{practice.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            f.write("### 📚 Documentation Practices\n")
            for practice, count in dev_insights['documentation_practices'].items():
                f.write(f"- **{practice.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            f.write("### 📦 Project Sizes\n")
            for size, count in dev_insights['project_sizes'].items():
                f.write(f"- **{size.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            # Skill Insights
            skill_insights = insights['skill_insights']
            f.write("## 🎯 Skill Analysis\n\n")
            
            f.write("### 💪 Strongest Areas\n")
            for area, stats in skill_insights['strongest_areas'][:5]:
                f.write(f"- **{area.replace('_', ' ').title()}:** {stats['project_count']} projects (Avg Complexity: {stats['avg_complexity']:.2f})\n")
            f.write("\n")
            
            f.write("### 🧠 Most Complex Areas\n")
            for area, stats in skill_insights['most_complex_areas'][:5]:
                f.write(f"- **{area.replace('_', ' ').title()}:** Avg Complexity {stats['avg_complexity']:.2f} ({stats['project_count']} projects)\n")
            f.write("\n")
            
            # Recommendations
            recommendations = insights['recommendations']
            f.write("## 💡 Recommendations\n\n")
            
            f.write("### 🎯 Strengths\n")
            for strength in recommendations['strengths']:
                f.write(f"- {strength}\n")
            f.write("\n")
            
            f.write("### 🌱 Growth Areas\n")
            for area in recommendations['growth_areas']:
                f.write(f"- {area}\n")
            f.write("\n")
            
            f.write("### 🚀 Next Steps\n")
            for step in recommendations['next_steps']:
                f.write(f"- {step}\n")
            f.write("\n")
            
            f.write("## 🎉 Summary\n\n")
            f.write("This analysis reveals your development patterns, strengths, and areas for growth. ")
            f.write("Use these insights to guide your learning journey and project planning!")

def main():
    """Main function to run the comprehensive analyzer."""
    print("🔍 Generating Comprehensive Project Analysis...")
    
    analyzer = ComprehensiveProjectAnalyzer()
    
    if not analyzer.library_data:
        print("❌ No library data found. Please run a scan first.")
        return
    
    print(f"📚 Analyzing {len(analyzer.library_data)} projects comprehensively...")
    
    # Generate comprehensive analysis
    analyzer.generate_comprehensive_report()
    
    print("✅ Comprehensive analysis complete!")
    print("📁 Check the 'comprehensive_analysis' directory for detailed insights.")

if __name__ == "__main__":
    main() 