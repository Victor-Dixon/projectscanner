#!/usr/bin/env python3
"""
Analyze language distribution across GitHub projects to determine optimal main language.
"""

import json
from collections import Counter
from pathlib import Path

def analyze_language_distribution():
    """Analyze the language distribution across all projects."""
    
    # Load the GitHub API analysis data
    api_file = Path("github_api_analysis/detailed_analysis_results.json")
    
    if not api_file.exists():
        print("❌ GitHub API analysis file not found")
        return
    
    with open(api_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Count languages
    language_counter = Counter()
    project_languages = {}
    
    for repo_name, repo_data in data.items():
        language = repo_data.get('language')
        if language:
            language_counter[language] += 1
            project_languages[repo_name] = language
    
    # Display results
    print("🎯 LANGUAGE DISTRIBUTION ANALYSIS")
    print("=" * 50)
    
    total_projects = len(project_languages)
    print(f"Total projects analyzed: {total_projects}")
    print()
    
    print("📊 Language Distribution:")
    for language, count in language_counter.most_common():
        percentage = (count / total_projects) * 100
        print(f"  {language}: {count} projects ({percentage:.1f}%)")
    
    print()
    
    # Determine optimal main language
    most_common_language = language_counter.most_common(1)[0][0]
    most_common_count = language_counter.most_common(1)[0][1]
    most_common_percentage = (most_common_count / total_projects) * 100
    
    print("🎯 RECOMMENDATION:")
    print(f"Your main language should have been: {most_common_language}")
    print(f"Reason: {most_common_count} out of {total_projects} projects ({most_common_percentage:.1f}%)")
    
    print()
    
    # Show project breakdown by language
    print("📋 Project Breakdown by Language:")
    for language in language_counter.keys():
        projects = [name for name, lang in project_languages.items() if lang == language]
        print(f"\n{language} Projects ({len(projects)}):")
        for project in projects[:5]:  # Show first 5
            print(f"  - {project}")
        if len(projects) > 5:
            print(f"  ... and {len(projects) - 5} more")
    
    print()
    
    # Analysis insights
    print("💡 INSIGHTS:")
    if most_common_percentage > 50:
        print(f"✅ {most_common_language} is clearly your dominant language ({most_common_percentage:.1f}%)")
    elif most_common_percentage > 30:
        print(f"✅ {most_common_language} is your primary language ({most_common_percentage:.1f}%)")
    else:
        print(f"⚠️  Your language usage is quite diverse. {most_common_language} is most common ({most_common_percentage:.1f}%)")
    
    # Check if Python is actually the best choice
    python_count = language_counter.get('Python', 0)
    python_percentage = (python_count / total_projects) * 100
    
    print(f"\n🐍 Python Analysis:")
    print(f"  Python projects: {python_count} ({python_percentage:.1f}%)")
    
    if python_count == most_common_count:
        print("  ✅ Python is indeed your main language - good choice!")
    else:
        print(f"  ⚠️  {most_common_language} is more common than Python")
        print(f"  Consider if {most_common_language} would have been a better choice")

if __name__ == "__main__":
    analyze_language_distribution() 