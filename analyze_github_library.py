#!/usr/bin/env python3
"""
Analyze GitHub library and extract insights about projects.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def analyze_github_library():
    """Analyze the GitHub library and extract insights."""
    library_file = Path("github_library/github_library.json")
    
    if not library_file.exists():
        print("❌ GitHub library file not found. Run the scanner first.")
        return
    
    print("🔍 Analyzing GitHub Library...")
    print("=" * 50)
    
    # Load the library data
    with library_file.open('r', encoding='utf-8') as f:
        library_data = json.load(f)
    
    # Extract insights
    insights = extract_insights(library_data)
    
    # Display insights
    display_insights(insights)
    
    return insights


def extract_insights(library_data):
    """Extract insights from the library data."""
    insights = {
        'total_repos': len(library_data),
        'total_files': 0,
        'languages': Counter(),
        'file_counts': [],
        'largest_repos': [],
        'tech_stack': defaultdict(int),
        'project_categories': defaultdict(int),
        'complexity_scores': [],
        'recent_projects': [],
        'ai_ml_projects': [],
        'automation_projects': [],
        'gaming_projects': [],
        'financial_projects': [],
        'social_media_projects': []
    }
    
    # Keywords for categorization
    ai_ml_keywords = ['ai', 'ml', 'machine', 'learning', 'neural', 'lstm', 'gpt', 'automation', 'agent']
    automation_keywords = ['automation', 'bot', 'script', 'auto', 'workflow']
    gaming_keywords = ['game', 'rpg', 'ttrpg', 'tactics', 'swarm', 'troop']
    financial_keywords = ['stock', 'trading', 'portfolio', 'financial', 'market']
    social_keywords = ['social', 'media', 'twitter', 'youtube', 'stream']
    
    for repo_id, repo_info in library_data.items():
        repo_name = repo_info.get('repo_name', '').lower()
        description = (repo_info.get('description') or '').lower()
        language = repo_info.get('language', 'Unknown')
        file_count = repo_info.get('file_count', 0)
        stars = repo_info.get('stars', 0)
        created_at = repo_info.get('created_at', '')
        
        # Count files
        insights['total_files'] += file_count
        insights['file_counts'].append(file_count)
        
        # Count languages
        insights['languages'][language] += 1
        
        # Track largest repos
        insights['largest_repos'].append({
            'name': repo_info.get('repo_name', repo_id),
            'files': file_count,
            'stars': stars,
            'language': language
        })
        
        # Categorize projects
        combined_text = f"{repo_name} {description}"
        
        if any(keyword in combined_text for keyword in ai_ml_keywords):
            insights['ai_ml_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['AI/ML'] += 1
            
        if any(keyword in combined_text for keyword in automation_keywords):
            insights['automation_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Automation'] += 1
            
        if any(keyword in combined_text for keyword in gaming_keywords):
            insights['gaming_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Gaming'] += 1
            
        if any(keyword in combined_text for keyword in financial_keywords):
            insights['financial_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Financial'] += 1
            
        if any(keyword in combined_text for keyword in social_keywords):
            insights['social_media_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Social Media'] += 1
        
        # Analyze tech stack from analysis data
        analysis_data = repo_info.get('analysis_data', {})
        for file_path, file_info in analysis_data.items():
            if 'classes' in file_info and file_info['classes']:
                for class_name, class_info in file_info['classes'].items():
                    if 'maturity' in class_info:
                        insights['tech_stack'][class_info['maturity']] += 1
                    if 'agent_type' in class_info:
                        insights['tech_stack'][class_info['agent_type']] += 1
    
    # Sort largest repos by file count
    insights['largest_repos'].sort(key=lambda x: x['files'], reverse=True)
    
    return insights


def display_insights(insights):
    """Display the extracted insights."""
    print(f"📊 **GitHub Portfolio Analysis**")
    print(f"Total Repositories: {insights['total_repos']}")
    print(f"Total Files Analyzed: {insights['total_files']:,}")
    print(f"Average Files per Repo: {insights['total_files'] / insights['total_repos']:.1f}")
    
    print(f"\n🎯 **Technology Stack**")
    print(f"Primary Languages:")
    for lang, count in insights['languages'].most_common(5):
        print(f"  • {lang}: {count} repos")
    
    print(f"\n🏗️ **Project Categories**")
    for category, count in insights['project_categories'].items():
        print(f"  • {category}: {count} projects")
    
    print(f"\n📈 **Largest Projects**")
    for i, repo in enumerate(insights['largest_repos'][:5], 1):
        print(f"  {i}. {repo['name']} ({repo['files']} files, {repo['stars']} stars)")
    
    print(f"\n🤖 **AI/ML Projects** ({len(insights['ai_ml_projects'])})")
    for project in insights['ai_ml_projects']:
        print(f"  • {project}")
    
    print(f"\n⚙️ **Automation Projects** ({len(insights['automation_projects'])})")
    for project in insights['automation_projects']:
        print(f"  • {project}")
    
    print(f"\n🎮 **Gaming Projects** ({len(insights['gaming_projects'])})")
    for project in insights['gaming_projects']:
        print(f"  • {project}")
    
    print(f"\n💰 **Financial Projects** ({len(insights['financial_projects'])})")
    for project in insights['financial_projects']:
        print(f"  • {project}")
    
    print(f"\n📱 **Social Media Projects** ({len(insights['social_media_projects'])})")
    for project in insights['social_media_projects']:
        print(f"  • {project}")
    
    print(f"\n💡 **Key Insights**")
    
    # Calculate complexity
    if insights['file_counts']:
        avg_files = sum(insights['file_counts']) / len(insights['file_counts'])
        print(f"  • Average project size: {avg_files:.1f} files")
        
        large_projects = sum(1 for count in insights['file_counts'] if count > 100)
        print(f"  • Large projects (>100 files): {large_projects}")
        
        small_projects = sum(1 for count in insights['file_counts'] if count < 20)
        print(f"  • Small projects (<20 files): {small_projects}")
    
    # Most common language
    if insights['languages']:
        most_common_lang = insights['languages'].most_common(1)[0]
        print(f"  • Primary language: {most_common_lang[0]} ({most_common_lang[1]} repos)")
    
    # Project diversity
    category_count = len(insights['project_categories'])
    print(f"  • Project diversity: {category_count} different categories")
    
    # AI/ML focus
    ai_ml_percentage = (len(insights['ai_ml_projects']) / insights['total_repos']) * 100
    print(f"  • AI/ML focus: {ai_ml_percentage:.1f}% of projects")


def generate_summary_report():
    """Generate a summary report."""
    insights = analyze_github_library()
    
    # Save insights to file
    report_file = Path("github_insights_report.json")
    with report_file.open('w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2)
    
    print(f"\n📄 **Report saved to: {report_file}**")


if __name__ == "__main__":
    generate_summary_report() 