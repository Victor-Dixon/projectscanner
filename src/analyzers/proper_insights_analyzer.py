#!/usr/bin/env python3
"""
Proper Insights Analyzer
Extracts insights from the actual structure of scanned library data
"""

import json
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
from datetime import datetime

class ProperInsightsAnalyzer:
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
    
    def analyze_project_insights(self) -> Dict[str, Any]:
        """Analyze projects using the correct data structure."""
        analysis = {
            'project_summary': {},
            'technology_usage': defaultdict(Counter),
            'development_patterns': defaultdict(Counter),
            'project_categories': defaultdict(list),
            'overall_stats': {
                'total_projects': len(self.library_data),
                'total_files': 0,
                'total_functions': 0,
                'total_classes': 0,
                'private_projects': 0,
                'public_projects': 0
            }
        }
        
        for repo_name, repo_data in self.library_data.items():
            if isinstance(repo_data, dict):
                # Extract project information
                project_info = self.extract_project_info(repo_name, repo_data)
                analysis['project_summary'][repo_name] = project_info
                
                # Categorize project
                category = self.categorize_project(repo_name, repo_data)
                analysis['project_categories'][category].append(repo_name)
                
                # Update overall stats
                analysis['overall_stats']['total_files'] += project_info['file_count']
                analysis['overall_stats']['total_functions'] += project_info['function_count']
                analysis['overall_stats']['total_classes'] += project_info['class_count']
                
                if repo_data.get('is_private', False):
                    analysis['overall_stats']['private_projects'] += 1
                else:
                    analysis['overall_stats']['public_projects'] += 1
                
                # Analyze technologies
                self.analyze_technologies(repo_name, repo_data, analysis)
                
                # Analyze development patterns
                self.analyze_development_patterns(repo_name, repo_data, analysis)
        
        return analysis
    
    def extract_project_info(self, repo_name: str, repo_data: Dict) -> Dict[str, Any]:
        """Extract project information from repository data."""
        project_info = {
            'name': repo_name,
            'description': repo_data.get('description', ''),
            'language': repo_data.get('language', ''),
            'is_private': repo_data.get('is_private', False),
            'stars': repo_data.get('stars', 0),
            'forks': repo_data.get('forks', 0),
            'file_count': repo_data.get('file_count', 0),
            'function_count': 0,
            'class_count': 0,
            'avg_complexity': 0,
            'max_complexity': 0,
            'technologies': set(),
            'frameworks': set()
        }
        
        # Analyze analysis_data if available
        if 'analysis_data' in repo_data and repo_data['analysis_data']:
            try:
                analysis_data = json.loads(repo_data['analysis_data'])
                project_info.update(self.analyze_analysis_data(analysis_data))
            except (json.JSONDecodeError, TypeError):
                pass
        
        return project_info
    
    def analyze_analysis_data(self, analysis_data: Dict) -> Dict[str, Any]:
        """Analyze the analysis_data structure."""
        result = {
            'function_count': 0,
            'class_count': 0,
            'avg_complexity': 0,
            'max_complexity': 0,
            'technologies': set(),
            'frameworks': set()
        }
        
        complexities = []
        
        for file_path, file_data in analysis_data.items():
            # Count functions and classes
            if 'functions' in file_data:
                result['function_count'] += len(file_data['functions'])
            
            if 'classes' in file_data:
                result['class_count'] += len(file_data['classes'])
            
            # Complexity analysis
            complexity = file_data.get('complexity', 0)
            complexities.append(complexity)
            
            # Technology detection from file path
            self.detect_technologies_from_path(file_path, result)
        
        # Calculate complexity metrics
        if complexities:
            result['avg_complexity'] = sum(complexities) / len(complexities)
            result['max_complexity'] = max(complexities)
        
        return result
    
    def detect_technologies_from_path(self, file_path: str, result: Dict):
        """Detect technologies from file path."""
        file_lower = file_path.lower()
        
        # Language detection from extension
        if file_path.endswith('.py'):
            result['technologies'].add('Python')
        elif file_path.endswith('.js'):
            result['technologies'].add('JavaScript')
        elif file_path.endswith('.ts'):
            result['technologies'].add('TypeScript')
        elif file_path.endswith('.html'):
            result['technologies'].add('HTML')
        elif file_path.endswith('.css'):
            result['technologies'].add('CSS')
        elif file_path.endswith('.rs'):
            result['technologies'].add('Rust')
        
        # Framework detection
        frameworks = {
            'flask': 'Flask', 'django': 'Django', 'fastapi': 'FastAPI',
            'react': 'React', 'vue': 'Vue', 'angular': 'Angular',
            'selenium': 'Selenium', 'beautifulsoup': 'BeautifulSoup',
            'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
            'opencv': 'OpenCV', 'numpy': 'NumPy', 'pandas': 'Pandas',
            'tkinter': 'Tkinter', 'pyqt': 'PyQt'
        }
        
        for pattern, framework in frameworks.items():
            if pattern in file_lower:
                result['frameworks'].add(framework)
    
    def categorize_project(self, repo_name: str, repo_data: Dict) -> str:
        """Categorize project based on name and metadata."""
        repo_lower = repo_name.lower()
        description = (repo_data.get('description') or '').lower()
        
        # Check for specific patterns
        if any(keyword in repo_lower for keyword in ['bot', 'automation']):
            return 'automation_bot'
        elif any(keyword in repo_lower for keyword in ['web', 'site', 'app']):
            return 'web_application'
        elif any(keyword in repo_lower for keyword in ['ai', 'ml', 'gpt', 'neural']):
            return 'ai_ml'
        elif any(keyword in repo_lower for keyword in ['gui', 'interface']):
            return 'gui_application'
        elif any(keyword in repo_lower for keyword in ['data', 'analysis']):
            return 'data_analysis'
        elif any(keyword in repo_lower for keyword in ['sims', 'mod', 'game']):
            return 'gaming'
        elif any(keyword in repo_lower for keyword in ['tool', 'util']):
            return 'utility'
        elif repo_data.get('file_count', 0) < 5:
            return 'micro_project'
        else:
            return 'general_application'
    
    def analyze_technologies(self, repo_name: str, repo_data: Dict, analysis: Dict):
        """Analyze technology usage."""
        project_info = analysis['project_summary'][repo_name]
        
        # Count technologies
        for tech in project_info['technologies']:
            analysis['technology_usage']['languages'][tech] += 1
        
        for framework in project_info['frameworks']:
            analysis['technology_usage']['frameworks'][framework] += 1
    
    def analyze_development_patterns(self, repo_name: str, repo_data: Dict, analysis: Dict):
        """Analyze development patterns."""
        project_info = analysis['project_summary'][repo_name]
        
        # Project size patterns
        file_count = project_info['file_count']
        if file_count > 50:
            analysis['development_patterns']['size']['large_project'] += 1
        elif file_count > 20:
            analysis['development_patterns']['size']['medium_project'] += 1
        elif file_count > 5:
            analysis['development_patterns']['size']['small_project'] += 1
        else:
            analysis['development_patterns']['size']['micro_project'] += 1
        
        # Complexity patterns
        avg_complexity = project_info['avg_complexity']
        if avg_complexity > 30:
            analysis['development_patterns']['complexity']['high_complexity'] += 1
        elif avg_complexity > 15:
            analysis['development_patterns']['complexity']['medium_complexity'] += 1
        else:
            analysis['development_patterns']['complexity']['low_complexity'] += 1
        
        # Visibility patterns
        if project_info['is_private']:
            analysis['development_patterns']['visibility']['private'] += 1
        else:
            analysis['development_patterns']['visibility']['public'] += 1
    
    def generate_insights_report(self) -> Dict[str, Any]:
        """Generate comprehensive insights report."""
        analysis = self.analyze_project_insights()
        
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
            'private_projects': overall_stats['private_projects'],
            'public_projects': overall_stats['public_projects'],
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
            'project_sizes': dict(dev_patterns['size']),
            'complexity_levels': dict(dev_patterns['complexity']),
            'visibility': dict(dev_patterns['visibility'])
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
        if dev_insights['complexity_levels'].get('high_complexity', 0) < 5:
            recommendations['growth_areas'].append("Build more complex projects to challenge yourself")
        
        if dev_insights['project_sizes'].get('large_project', 0) < 3:
            recommendations['growth_areas'].append("Work on larger, more comprehensive projects")
        
        # Next steps
        recommendations['next_steps'].append("Focus on your strongest areas")
        recommendations['next_steps'].append("Explore new technologies")
        recommendations['next_steps'].append("Build larger, more complex projects")
        
        return recommendations
    
    def generate_comprehensive_report(self, output_dir: str = "proper_insights"):
        """Generate comprehensive analysis report."""
        os.makedirs(output_dir, exist_ok=True)
        
        insights = self.generate_insights_report()
        
        # Save detailed reports
        self.save_insights_report(insights, f"{output_dir}/proper_insights.json")
        self.save_summary_report(insights, f"{output_dir}/proper_insights_summary.md")
        
        print(f"📊 Proper insights reports saved to: {output_dir}/")
    
    def save_insights_report(self, insights: Dict, output_path: str):
        """Save insights report to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
    
    def save_summary_report(self, insights: Dict, output_path: str):
        """Generate a comprehensive markdown summary report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 🔍 Proper Project Insights Analysis\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Project Overview
            overview = insights['project_overview']
            f.write("## 📊 Project Overview\n\n")
            f.write(f"- **Total Projects:** {overview['total_projects']}\n")
            f.write(f"- **Total Files:** {overview['total_files']}\n")
            f.write(f"- **Total Functions:** {overview['total_functions']}\n")
            f.write(f"- **Total Classes:** {overview['total_classes']}\n")
            f.write(f"- **Private Projects:** {overview['private_projects']}\n")
            f.write(f"- **Public Projects:** {overview['public_projects']}\n\n")
            
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
            f.write("## 🛠️ Development Patterns\n\n")
            
            f.write("### 📦 Project Sizes\n")
            for size, count in dev_insights['project_sizes'].items():
                f.write(f"- **{size.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            f.write("### 🧠 Complexity Levels\n")
            for level, count in dev_insights['complexity_levels'].items():
                f.write(f"- **{level.replace('_', ' ').title()}:** {count} projects\n")
            f.write("\n")
            
            f.write("### 👁️ Project Visibility\n")
            for visibility, count in dev_insights['visibility'].items():
                f.write(f"- **{visibility.title()}:** {count} projects\n")
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
            f.write("This analysis reveals your actual development patterns, strengths, and areas for growth. ")
            f.write("Use these insights to guide your learning journey and project planning!")

def main():
    """Main function to run the proper insights analyzer."""
    print("🔍 Generating Proper Project Insights...")
    
    analyzer = ProperInsightsAnalyzer()
    
    if not analyzer.library_data:
        print("❌ No library data found. Please run a scan first.")
        return
    
    print(f"📚 Analyzing {len(analyzer.library_data)} projects with proper data structure...")
    
    # Generate comprehensive analysis
    analyzer.generate_comprehensive_report()
    
    print("✅ Proper insights analysis complete!")
    print("📁 Check the 'proper_insights' directory for detailed insights.")

if __name__ == "__main__":
    main() 