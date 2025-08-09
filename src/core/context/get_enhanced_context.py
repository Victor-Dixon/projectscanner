#!/usr/bin/env python3
"""
Get Enhanced Project Context
Simple interface to get rich context for any project using the enhanced scanner
"""

import json
import sys
from pathlib import Path
from enhanced_project_scanner import EnhancedProjectScanner

def get_project_context(project_name: str) -> dict:
    """Get comprehensive context for a specific project."""
    scanner = EnhancedProjectScanner()
    
    # Check if scan results exist
    scan_file = Path("enhanced_scan_results/detailed_scan_results.json")
    if not scan_file.exists():
        print("🔍 No scan results found. Running enhanced scan...")
        scanner.scan_all_repositories()
    
    # Load scan results
    with open(scan_file, 'r') as f:
        scanner.scan_results = json.load(f)
    
    # Generate portfolio context
    scanner.generate_portfolio_context()
    
    return scanner.generate_llm_context_for_project(project_name)

def get_portfolio_summary() -> dict:
    """Get comprehensive portfolio summary."""
    scanner = EnhancedProjectScanner()
    
    # Check if scan results exist
    scan_file = Path("enhanced_scan_results/detailed_scan_results.json")
    if not scan_file.exists():
        print("🔍 No scan results found. Running enhanced scan...")
        scanner.scan_all_repositories()
    
    # Load scan results
    with open(scan_file, 'r') as f:
        scanner.scan_results = json.load(f)
    
    # Generate portfolio context
    scanner.generate_portfolio_context()
    
    return {
        'portfolio_overview': {
            'total_repositories': len(scanner.scan_results),
            'total_files': sum(repo['complexity_metrics']['total_files'] for repo in scanner.scan_results.values()),
            'total_lines': sum(repo['complexity_metrics']['total_lines'] for repo in scanner.scan_results.values()),
            'avg_complexity': sum(repo['complexity_metrics']['avg_complexity'] for repo in scanner.scan_results.values()) / len(scanner.scan_results) if scanner.scan_results else 0
        },
        'project_categories': dict(scanner.portfolio_context['project_categories']),
        'technology_ecosystem': dict(scanner.portfolio_context['technology_ecosystem']),
        'business_opportunities': dict(scanner.portfolio_context['business_opportunities']),
        'skill_domains': dict(scanner.portfolio_context['skill_domains'])
    }

def list_all_projects() -> list:
    """List all projects in the portfolio."""
    scan_file = Path("enhanced_scan_results/detailed_scan_results.json")
    if not scan_file.exists():
        print("🔍 No scan results found. Run enhanced scan first.")
        return []
    
    with open(scan_file, 'r') as f:
        scan_results = json.load(f)
    
    return list(scan_results.keys())

def run_enhanced_scan():
    """Run the enhanced scan on all repositories."""
    print("🚀 Starting enhanced project scan...")
    scanner = EnhancedProjectScanner()
    scanner.scan_all_repositories()
    print("✅ Enhanced scan complete!")

def main():
    """Main interface for getting enhanced project context."""
    if len(sys.argv) < 2:
        print("Usage: python get_enhanced_context.py <project_name>")
        print("       python get_enhanced_context.py --list")
        print("       python get_enhanced_context.py --portfolio")
        print("       python get_enhanced_context.py --scan")
        return
    
    command = sys.argv[1]
    
    if command == "--list":
        projects = list_all_projects()
        if projects:
            print("📁 Available Projects:")
            for i, project in enumerate(projects, 1):
                print(f"   {i:2d}. {project}")
        else:
            print("❌ No projects found. Run --scan first.")
        return
    
    elif command == "--portfolio":
        summary = get_portfolio_summary()
        print("🎯 Portfolio Summary:")
        print(f"   Total Repositories: {summary['portfolio_overview']['total_repositories']}")
        print(f"   Total Files: {summary['portfolio_overview']['total_files']}")
        print(f"   Total Lines: {summary['portfolio_overview']['total_lines']}")
        print(f"   Avg Complexity: {summary['portfolio_overview']['avg_complexity']:.2f}")
        
        print("\n📊 Project Categories:")
        for category, projects in summary['project_categories'].items():
            print(f"   {category}: {len(projects)} projects")
        
        print("\n💎 Business Opportunities:")
        for level, projects in summary['business_opportunities'].items():
            print(f"   {level}: {len(projects)} projects")
        
        print("\n🛠️  Technology Ecosystem:")
        for tech, count in summary['technology_ecosystem']['technologies'].most_common(10):
            print(f"   {tech}: {count} projects")
        
        return
    
    elif command == "--scan":
        run_enhanced_scan()
        return
    
    else:
        project_name = command
        context = get_project_context(project_name)
        
        if "error" in context:
            print(f"❌ {context['error']}")
            print("💡 Try running: python get_enhanced_context.py --scan")
            return
        
        # Print formatted context
        print(f"🎯 Enhanced Project Context: {project_name}")
        print("=" * 60)
        
        # Project Overview
        overview = context['project_overview']
        print(f"📋 Description: {overview['description']}")
        print(f"🏗️  Development Stage: {overview['development_stage']}")
        print(f"💰 Business Value: {overview['business_value']}")
        print(f"💎 Monetization Potential: {overview['monetization_potential']}")
        
        # Technical Context
        tech = context['technical_context']
        print(f"\n🛠️  Languages: {', '.join(tech['languages'])}")
        print(f"🔧 Technologies: {', '.join(tech['technologies'])}")
        print(f"🏛️  Architecture: {', '.join(tech['architecture_patterns'])}")
        print(f"✨ Key Features: {', '.join(tech['key_features'])}")
        print(f"📊 Complexity: {tech['complexity_metrics']['avg_complexity']:.2f} avg, {tech['complexity_metrics']['max_complexity']} max")
        print(f"📁 Files: {tech['complexity_metrics']['total_files']} files, {tech['complexity_metrics']['total_lines']} lines")
        
        # Portfolio Context
        portfolio = context['portfolio_context']
        print(f"\n📊 Category: {portfolio['category']}")
        print(f"🎯 Skill Domains: {', '.join(portfolio['skill_domains'])}")
        print(f"📈 Portfolio Position: #{portfolio['portfolio_position']['category_rank']} of {portfolio['portfolio_position']['category_size']} in category")
        
        # Similar Projects
        if portfolio['similar_projects']:
            print(f"\n🔗 Similar Projects:")
            for similar in portfolio['similar_projects'][:3]:
                print(f"   • {similar['name']} (score: {similar['similarity_score']})")
        
        # Business Context
        business = context['business_context']
        print(f"\n💼 Market Opportunity: {business['market_opportunity']['level']}")
        if business['market_opportunity']['factors']:
            print(f"   Factors: {', '.join(business['market_opportunity']['factors'])}")
        print(f"🏆 Competitive Advantages: {', '.join(business['competitive_advantages'])}")
        print(f"📈 Development Priorities: {', '.join(business['development_priorities'])}")
        
        # Save to file
        output_file = f"enhanced_context_{project_name}.json"
        with open(output_file, 'w') as f:
            json.dump(context, f, indent=2)
        print(f"\n✅ Enhanced context saved to {output_file}")

if __name__ == "__main__":
    main() 