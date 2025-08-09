#!/usr/bin/env python3
"""
Analyze which projects are closest to generating real revenue.
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_revenue_potential():
    """Analyze projects by revenue potential and readiness."""
    
    # Load the GitHub API analysis data
    api_file = Path("github_api_analysis/detailed_analysis_results.json")
    
    if not api_file.exists():
        print("❌ GitHub API analysis file not found")
        return
    
    with open(api_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Categorize projects by revenue potential
    high_potential = []
    medium_potential = []
    low_potential = []
    
    for repo_name, repo_data in data.items():
        monetization = repo_data.get('analysis', {}).get('monetization_potential', 'Low')
        business_value = repo_data.get('analysis', {}).get('business_value', 'Low')
        category = repo_data.get('analysis', {}).get('project_category', 'Unknown')
        stage = repo_data.get('analysis', {}).get('development_stage', 'Unknown')
        
        project_info = {
            'name': repo_name,
            'description': repo_data.get('description', ''),
            'category': category,
            'stage': stage,
            'business_value': business_value,
            'size': repo_data.get('size', 0),
            'stars': repo_data.get('stargazers_count', 0),
            'forks': repo_data.get('forks_count', 0),
            'language': repo_data.get('language', 'Unknown'),
            'readme': repo_data.get('analysis', {}).get('readme_content', '')[:200] + '...' if repo_data.get('analysis', {}).get('readme_content') else 'No README'
        }
        
        if monetization == 'High':
            high_potential.append(project_info)
        elif monetization == 'Medium':
            medium_potential.append(project_info)
        else:
            low_potential.append(project_info)
    
    # Display results
    print("💰 REVENUE POTENTIAL ANALYSIS")
    print("=" * 60)
    
    print(f"\n🎯 HIGH REVENUE POTENTIAL ({len(high_potential)} projects):")
    print("-" * 50)
    
    for i, project in enumerate(high_potential, 1):
        print(f"\n{i}. {project['name']}")
        print(f"   Category: {project['category']}")
        print(f"   Stage: {project['stage']}")
        print(f"   Language: {project['language']}")
        print(f"   Size: {project['size']:,} bytes")
        print(f"   Stars: {project['stars']}, Forks: {project['forks']}")
        print(f"   Business Value: {project['business_value']}")
        print(f"   Description: {project['description'] or 'No description'}")
        print(f"   README Preview: {project['readme'][:100]}...")
    
    print(f"\n📊 MEDIUM REVENUE POTENTIAL ({len(medium_potential)} projects):")
    print("-" * 50)
    
    for i, project in enumerate(medium_potential, 1):
        print(f"\n{i}. {project['name']}")
        print(f"   Category: {project['category']}")
        print(f"   Stage: {project['stage']}")
        print(f"   Language: {project['language']}")
    
    # Analyze by category
    category_analysis = defaultdict(list)
    for project in high_potential:
        category_analysis[project['category']].append(project)
    
    print(f"\n📈 REVENUE BY CATEGORY:")
    print("-" * 50)
    
    for category, projects in category_analysis.items():
        print(f"\n{category} ({len(projects)} high-potential projects):")
        for project in projects:
            print(f"  - {project['name']} ({project['stage']})")
    
    # Identify the most promising projects
    print(f"\n🚀 TOP 5 MOST PROMISING PROJECTS:")
    print("-" * 50)
    
    # Sort by business value and development stage
    promising_projects = sorted(high_potential, 
                              key=lambda x: (
                                  x['business_value'] == 'High',
                                  x['stage'] in ['Production', 'Development'],
                                  x['size'],
                                  x['stars']
                              ), reverse=True)
    
    for i, project in enumerate(promising_projects[:5], 1):
        print(f"\n{i}. {project['name']}")
        print(f"   🎯 Revenue Potential: HIGH")
        print(f"   💼 Business Value: {project['business_value']}")
        print(f"   🏗️  Development Stage: {project['stage']}")
        print(f"   📊 Category: {project['category']}")
        print(f"   💻 Language: {project['language']}")
        print(f"   📏 Size: {project['size']:,} bytes")
        
        # Add specific recommendations
        if 'Trading' in project['category']:
            print(f"   💡 Action: Deploy as SaaS trading platform")
        elif 'AI/ML' in project['category']:
            print(f"   💡 Action: Create API service for ML predictions")
        elif 'Web' in project['category']:
            print(f"   💡 Action: Launch as web application")
        else:
            print(f"   💡 Action: Package as commercial product")
    
    # Summary
    print(f"\n📋 SUMMARY:")
    print("-" * 50)
    print(f"Total projects analyzed: {len(data)}")
    print(f"High revenue potential: {len(high_potential)}")
    print(f"Medium revenue potential: {len(medium_potential)}")
    print(f"Low revenue potential: {len(low_potential)}")
    
    if high_potential:
        print(f"\n🎯 IMMEDIATE ACTION ITEMS:")
        print("-" * 50)
        print("1. Focus on the top 5 high-potential projects")
        print("2. Complete development and testing")
        print("3. Create landing pages and documentation")
        print("4. Set up payment processing")
        print("5. Launch MVP versions")
    
    return high_potential, medium_potential, low_potential

if __name__ == "__main__":
    analyze_revenue_potential() 