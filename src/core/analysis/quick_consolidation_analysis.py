"""
MODULE: quick_consolidation_analysis
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""
Quick analysis of which projects should be consolidated based on similarity.
"""

import json
from pathlib import Path

# Concept: TODO - Explain the core idea behind quick_consolidation_analysis
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 114 lines > 30 limit)
def quick_consolidation_analysis():
# Concept: TODO
# Trade-off: TODO
# Execution: TODO
    """Quick analysis of consolidation candidates."""
    
    # Load duplicate analysis
    with open("duplicate_analysis_results.json", 'r', encoding='utf-8') as f:
        duplicate_data = json.load(f)
    
    # Load GitHub API data for context
    with open("github_api_analysis/detailed_analysis_results.json", 'r', encoding='utf-8') as f:
        api_data = json.load(f)
    
    print("🔗 TOP CONSOLIDATION CANDIDATES")
    print("=" * 50)
    
    # Analyze each duplicate group
    for i, group in enumerate(duplicate_data['duplicate_groups'], 1):
        print(f"\n{i}. DUPLICATE GROUP {i}:")
        print(f"   Projects: {', '.join(group)}")
        
        # Get details for each project
        for project_name in group:
            api_info = api_data.get(project_name, {})
            print(f"     📊 {project_name}")
            print(f"        Category: {api_info.get('analysis', {}).get('project_category', 'Unknown')}")
            print(f"        Business Value: {api_info.get('analysis', {}).get('business_value', 'Unknown')}")
            print(f"        Monetization: {api_info.get('analysis', {}).get('monetization_potential', 'Unknown')}")
            print(f"        Size: {api_info.get('size', 0):,} bytes")
            print(f"        Stage: {api_info.get('analysis', {}).get('development_stage', 'Unknown')}")
        
        # Recommend which to keep
        best_project = None
        best_score = 0
        
        for project_name in group:
            api_info = api_data.get(project_name, {})
            score = 0
            
            # Score based on business value and development
            if api_info.get('analysis', {}).get('business_value') == 'High':
                score += 10
            if api_info.get('analysis', {}).get('monetization_potential') == 'High':
                score += 8
            if api_info.get('analysis', {}).get('development_stage') == 'Development':
                score += 5
            score += min(api_info.get('size', 0) / 10000, 5)
            
            if score > best_score:
                best_score = score
                best_project = project_name
        
        if best_project:
            print(f"   🎯 KEEP: {best_project} (highest score: {best_score})")
            print(f"   🔄 MERGE: Others into {best_project}")
    
    # Focus on trading projects specifically
    print(f"\n📈 TRADING PROJECT CONSOLIDATION:")
    print("-" * 50)
    
    trading_projects = []
    for repo_name, repo_data in api_data.items():
        if repo_data.get('analysis', {}).get('project_category') == 'Trading/Finance':
            trading_projects.append({
                'name': repo_name,
                'data': repo_data
            })
    
    # Find similar trading projects
    similar_trading = []
    for i, p1 in enumerate(trading_projects):
        for j, p2 in enumerate(trading_projects[i+1:], i+1):
            name1 = p1['name'].lower()
            name2 = p2['name'].lower()
            
            # Check for similarity in names
            if 'trading' in name1 and 'trading' in name2:
                similar_trading.append((p1, p2))
            elif 'robot' in name1 and 'robot' in name2:
                similar_trading.append((p1, p2))
            elif 'plug' in name1 and 'plug' in name2:
                similar_trading.append((p1, p2))
    
    for i, (p1, p2) in enumerate(similar_trading, 1):
        print(f"\n{i}. SIMILAR TRADING PROJECTS:")
        print(f"   📊 {p1['name']}")
        print(f"      Business Value: {p1['data'].get('analysis', {}).get('business_value', 'Unknown')}")
        print(f"      Size: {p1['data'].get('size', 0):,} bytes")
        
        print(f"   📊 {p2['name']}")
        print(f"      Business Value: {p2['data'].get('analysis', {}).get('business_value', 'Unknown')}")
        print(f"      Size: {p2['data'].get('size', 0):,} bytes")
        
        # Recommend which to keep
        p1_score = 0
        p2_score = 0
        
        if p1['data'].get('analysis', {}).get('business_value') == 'High':
            p1_score += 10
        if p2['data'].get('analysis', {}).get('business_value') == 'High':
            p2_score += 10
        p1_score += min(p1['data'].get('size', 0) / 10000, 5)
        p2_score += min(p2['data'].get('size', 0) / 10000, 5)
        
        if p1_score >= p2_score:
            print(f"   🎯 RECOMMENDATION: Keep {p1['name']}, merge {p2['name']} into it")
        else:
            print(f"   🎯 RECOMMENDATION: Keep {p2['name']}, merge {p1['name']} into it")
    
    print(f"\n📋 CONSOLIDATION PRIORITY:")
    print("-" * 50)
    print("1. TradingRobotPlug + TheTradingRobotPlug (highest revenue potential)")
    print("2. TradingRobotPlugWeb + TradingRobotPlugWebTheme (web interfaces)")
    print("3. UltimateOptionsTradingRobot + ultimate_trading_intelligence (options focus)")
    print("4. Side-projects + agentproject_private (general development)")
    print("5. Dreamos + ideas_private (concept projects)")

if __name__ == "__main__":
    quick_consolidation_analysis() 
# Concept: TODO - Purpose of quick_consolidation_analysis
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach