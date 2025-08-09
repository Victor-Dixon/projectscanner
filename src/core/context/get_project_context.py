#!/usr/bin/env python3
"""
Get Project Context for LLMs
Simple interface to get comprehensive context for any project in the portfolio
"""

import json
import sys
from pathlib import Path
from src.analyzers.enhanced_llm_context_analyzer import EnhancedLLMContextAnalyzer

def get_project_context(project_name: str) -> dict:
    """Get comprehensive context for a specific project."""
    analyzer = EnhancedLLMContextAnalyzer()
    return analyzer.generate_project_context_for_llm(project_name)

def get_portfolio_summary() -> dict:
    """Get comprehensive portfolio summary."""
    analyzer = EnhancedLLMContextAnalyzer()
    return analyzer.generate_portfolio_summary_for_llm()

def list_all_projects() -> list:
    """List all projects in the portfolio."""
    analyzer = EnhancedLLMContextAnalyzer()
    return list(analyzer.library_data.keys())

def main():
    """Main interface for getting project context."""
    if len(sys.argv) < 2:
        print("Usage: python get_project_context.py <project_name>")
        print("       python get_project_context.py --list")
        print("       python get_project_context.py --portfolio")
        return
    
    command = sys.argv[1]
    
    if command == "--list":
        projects = list_all_projects()
        print("📁 Available Projects:")
        for i, project in enumerate(projects, 1):
            print(f"   {i:2d}. {project}")
        return
    
    elif command == "--portfolio":
        summary = get_portfolio_summary()
        print("🎯 Portfolio Summary:")
        print(f"   Total Repositories: {summary['portfolio_overview']['total_repositories']}")
        print(f"   Total Files: {summary['portfolio_overview']['total_files']}")
        print(f"   Primary Language: {summary['portfolio_overview']['primary_language']}")
        print(f"   Primary Technology: {summary['portfolio_overview']['primary_technology']}")
        
        print("\n📊 Project Categories:")
        for category, projects in summary['project_categories'].items():
            print(f"   {category}: {len(projects)} projects")
        
        print("\n💎 Business Opportunities:")
        for level, projects in summary['business_opportunities'].items():
            print(f"   {level}: {len(projects)} projects")
        
        return
    
    else:
        project_name = command
        context = get_project_context(project_name)
        
        if "error" in context:
            print(f"❌ {context['error']}")
            return
        
        # Print formatted context
        print(f"🎯 Project Context: {project_name}")
        print("=" * 60)
        
        # Project Overview
        overview = context['project_overview']
        print(f"📋 Description: {overview['description']}")
        print(f"🏗️  Development Stage: {overview['development_stage']}")
        print(f"💰 Business Value: {overview['business_value']}")
        print(f"💎 Monetization Potential: {overview['monetization_potential']}")
        
        # Technical Context
        tech = context['technical_context']
        print(f"\n🛠️  Technologies: {', '.join(tech['languages'])}")
        print(f"🔧 Frameworks: {', '.join(tech['technologies'])}")
        print(f"🏛️  Architecture: {', '.join(tech['architecture_patterns'])}")
        print(f"✨ Key Features: {', '.join(tech['key_features'])}")
        
        # Portfolio Context
        portfolio = context['portfolio_context']
        print(f"\n📊 Category: {portfolio['category']}")
        print(f"🎯 Skill Domains: {', '.join(portfolio['skill_domains'])}")
        
        # Business Context
        business = context['business_context']
        print(f"\n💼 Market Opportunity: {business['market_opportunity']['level']}")
        print(f"🏆 Competitive Advantages: {', '.join(business['competitive_advantages'])}")
        print(f"📈 Development Priorities: {', '.join(business['development_priorities'])}")
        
        # Save to file
        output_file = f"context_{project_name}.json"
        with open(output_file, 'w') as f:
            json.dump(context, f, indent=2)
        print(f"\n✅ Context saved to {output_file}")

if __name__ == "__main__":
    main() 