#!/usr/bin/env python3
"""
Analyze which projects should be consolidated based on similarity and revenue potential.
"""

import json
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

def analyze_consolidation_candidates():
    """Analyze which projects should be consolidated."""
    
    # Load the duplicate analysis results
    duplicate_file = Path("duplicate_analysis_results.json")
    
    if not duplicate_file.exists():
        print("❌ Duplicate analysis file not found")
        return
    
    with open(duplicate_file, 'r', encoding='utf-8') as f:
        duplicate_data = json.load(f)
    
    # Load the GitHub API analysis for additional context
    api_file = Path("github_api_analysis/detailed_analysis_results.json")
    
    if not api_file.exists():
        print("❌ GitHub API analysis file not found")
        return
    
    with open(api_file, 'r', encoding='utf-8') as f:
        api_data = json.load(f)
    
    print("🔗 PROJECT CONSOLIDATION ANALYSIS")
    print("=" * 60)
    
    # Analyze duplicate groups
    if 'duplicate_groups' in duplicate_data:
        print(f"\n📊 FOUND {len(duplicate_data['duplicate_groups'])} DUPLICATE GROUPS:")
        print("-" * 50)
        
        for i, group in enumerate(duplicate_data['duplicate_groups'], 1):
            print(f"\n{i}. DUPLICATE GROUP {i}:")
            print(f"   Similarity Score: {group.get('similarity_score', 'N/A')}")
            print(f"   Projects ({len(group['projects'])}):")
            
            for project in group['projects']:
                project_name = project['name']
                api_info = api_data.get(project_name, {})
                
                print(f"     - {project_name}")
                print(f"       Category: {api_info.get('analysis', {}).get('project_category', 'Unknown')}")
                print(f"       Stage: {api_info.get('analysis', {}).get('development_stage', 'Unknown')}")
                print(f"       Size: {api_info.get('size', 0):,} bytes")
                print(f"       Monetization: {api_info.get('analysis', {}).get('monetization_potential', 'Unknown')}")
                print(f"       Business Value: {api_info.get('analysis', {}).get('business_value', 'Unknown')}")
            
            # Recommend consolidation strategy
            print(f"   💡 CONSOLIDATION STRATEGY:")
            
            # Find the best project to keep (highest business value, largest size, most developed)
            best_project = None
            best_score = 0
            
            for project in group['projects']:
                project_name = project['name']
                api_info = api_data.get(project_name, {})
                
                # Calculate a score based on multiple factors
                score = 0
                if api_info.get('analysis', {}).get('business_value') == 'High':
                    score += 10
                if api_info.get('analysis', {}).get('monetization_potential') == 'High':
                    score += 8
                if api_info.get('analysis', {}).get('development_stage') == 'Development':
                    score += 5
                if api_info.get('analysis', {}).get('development_stage') == 'Production':
                    score += 10
                score += min(api_info.get('size', 0) / 10000, 5)  # Size bonus (max 5 points)
                score += api_info.get('stargazers_count', 0)  # GitHub stars
                
                if score > best_score:
                    best_score = score
                    best_project = project_name
            
            if best_project:
                print(f"     🎯 KEEP: {best_project} (best business value/size/development)")
                print(f"     🔄 MERGE: All other projects into {best_project}")
                print(f"     📈 BENEFIT: Stronger product, reduced maintenance")
    
    # Analyze consolidation recommendations
    if 'consolidation_recommendations' in duplicate_data:
        print(f"\n🎯 CONSOLIDATION RECOMMENDATIONS:")
        print("-" * 50)
        
        for i, rec in enumerate(duplicate_data['consolidation_recommendations'], 1):
            print(f"\n{i}. {rec['action']}")
            print(f"   Projects: {', '.join(rec['projects'])}")
            print(f"   Reason: {rec['reason']}")
            print(f"   Priority: {rec.get('priority', 'Medium')}")
    
    # Find the most similar projects that should be consolidated
    print(f"\n🔍 TOP CONSOLIDATION CANDIDATES:")
    print("-" * 50)
    
    # Group projects by category and find similar ones
    category_projects = defaultdict(list)
    
    for repo_name, repo_data in api_data.items():
        category = repo_data.get('analysis', {}).get('project_category', 'Unknown')
        if category:
            category_projects[category].append({
                'name': repo_name,
                'data': repo_data
            })
    
    # Focus on Trading/Finance projects (highest revenue potential)
    trading_projects = category_projects.get('Trading/Finance', [])
    
    if trading_projects:
        print(f"\n📈 TRADING PROJECTS TO CONSOLIDATE:")
        print("-" * 50)
        
        # Find similar trading projects
        similar_groups = []
        
        for i, project1 in enumerate(trading_projects):
            for j, project2 in enumerate(trading_projects[i+1:], i+1):
                name1 = project1['name']
                name2 = project2['name']
                
                # Calculate similarity
                similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
                
                if similarity > 0.3:  # Significant similarity
                    similar_groups.append({
                        'project1': project1,
                        'project2': project2,
                        'similarity': similarity
                    })
        
        # Sort by similarity and business value
        similar_groups.sort(key=lambda x: (
            x['similarity'],
            x['project1']['data'].get('analysis', {}).get('business_value') == 'High',
            x['project2']['data'].get('analysis', {}).get('business_value') == 'High'
        ), reverse=True)
        
        for i, group in enumerate(similar_groups[:5], 1):
            p1 = group['project1']
            p2 = group['project2']
            
            print(f"\n{i}. SIMILAR PROJECTS ({group['similarity']:.1%} similarity):")
            print(f"   📊 {p1['name']}")
            print(f"      Size: {p1['data'].get('size', 0):,} bytes")
            print(f"      Business Value: {p1['data'].get('analysis', {}).get('business_value', 'Unknown')}")
            print(f"      Monetization: {p1['data'].get('analysis', {}).get('monetization_potential', 'Unknown')}")
            
            print(f"   📊 {p2['name']}")
            print(f"      Size: {p2['data'].get('size', 0):,} bytes")
            print(f"      Business Value: {p2['data'].get('analysis', {}).get('business_value', 'Unknown')}")
            print(f"      Monetization: {p2['data'].get('analysis', {}).get('monetization_potential', 'Unknown')}")
            
            # Recommend which to keep
            p1_score = 0
            p2_score = 0
            
            if p1['data'].get('analysis', {}).get('business_value') == 'High':
                p1_score += 10
            if p2['data'].get('analysis', {}).get('business_value') == 'High':
                p2_score += 10
            if p1['data'].get('analysis', {}).get('monetization_potential') == 'High':
                p1_score += 8
            if p2['data'].get('analysis', {}).get('monetization_potential') == 'High':
                p2_score += 8
            p1_score += min(p1['data'].get('size', 0) / 10000, 5)
            p2_score += min(p2['data'].get('size', 0) / 10000, 5)
            
            if p1_score >= p2_score:
                print(f"   🎯 RECOMMENDATION: Keep {p1['name']}, merge {p2['name']} into it")
            else:
                print(f"   🎯 RECOMMENDATION: Keep {p2['name']}, merge {p1['name']} into it")
    
    # Summary
    print(f"\n📋 CONSOLIDATION SUMMARY:")
    print("-" * 50)
    print("1. Focus on Trading/Finance projects (highest revenue potential)")
    print("2. Merge similar projects to reduce maintenance overhead")
    print("3. Keep the project with highest business value/size/development")
    print("4. Consolidate features from merged projects into the main project")
    print("5. Create stronger, more focused products")

if __name__ == "__main__":
    analyze_consolidation_candidates() 