#!/usr/bin/env python3
import json
from pathlib import Path

def analyze_portfolio():
    """Analyze the portfolio and identify high-value opportunities."""
    
    # Load the enhanced library summary
    summary_file = Path("github_library_enhanced/enhanced_library_summary.json")
    if not summary_file.exists():
        print("❌ Enhanced library summary not found!")
        return
    
    with open(summary_file, 'r') as f:
        data = json.load(f)
    
    print("🎯 PORTFOLIO ANALYSIS & STRATEGIC TASK LIST")
    print("=" * 60)
    
    # Sort repositories by file count (complexity)
    repos = sorted(data['repositories'], key=lambda x: x.get('files_scanned', 0), reverse=True)
    
    print(f"\n📊 PORTFOLIO OVERVIEW:")
    print(f"   • Total Repositories: {data['total_repositories']}")
    print(f"   • Public: {data['public_repositories']}")
    print(f"   • Private: {data['private_repositories']}")
    print(f"   • Primary Language: Python ({data['languages'].get('Python', 0)} projects)")
    
    print(f"\n🏆 TOP 15 MOST COMPLEX PROJECTS:")
    for i, repo in enumerate(repos[:15], 1):
        status = "🔒 PRIVATE" if repo['private'] else "🌐 PUBLIC"
        print(f"   {i:2d}. {repo['name']:<25} ({repo['files_scanned']:3d} files) {status}")
    
    # Identify high-value opportunities
    print(f"\n💎 HIGH-VALUE OPPORTUNITIES:")
    
    # 1. Large Python projects (potential for monetization)
    large_python = [r for r in repos if r['language'] == 'Python' and r['files_scanned'] > 50]
    if large_python:
        print(f"   🐍 Large Python Projects ({len(large_python)}):")
        for repo in large_python[:5]:
            print(f"      • {repo['name']} ({repo['files_scanned']} files)")
    
    # 2. Private projects (exclusive value)
    private_projects = [r for r in repos if r['private'] and r['files_scanned'] > 10]
    if private_projects:
        print(f"   🔒 High-Value Private Projects ({len(private_projects)}):")
        for repo in private_projects[:5]:
            print(f"      • {repo['name']} ({repo['files_scanned']} files)")
    
    # 3. Unique technology stacks
    unique_tech = [r for r in repos if r['language'] and r['language'] not in ['Python', 'null']]
    if unique_tech:
        print(f"   🛠️  Diverse Tech Stack ({len(unique_tech)}):")
        for repo in unique_tech:
            print(f"      • {repo['name']} ({repo['language']})")
    
    print(f"\n🎯 STRATEGIC TASK LIST:")
    print("=" * 60)
    
    tasks = [
        {
            "priority": "🔥 CRITICAL",
            "task": "Monetize Victor.os (1254 files)",
            "action": "Package as SaaS product",
            "value": "High revenue potential"
        },
        {
            "priority": "🔥 CRITICAL", 
            "task": "Launch TradingRobotPlugWeb (80 files)",
            "action": "Deploy as web service",
            "value": "Trading automation market"
        },
        {
            "priority": "🔥 CRITICAL",
            "task": "Commercialize ideas repository (248 files)",
            "action": "Extract and patent key concepts",
            "value": "IP protection and licensing"
        },
        {
            "priority": "⚡ HIGH",
            "task": "Optimize MeTuber (225 files)",
            "action": "Performance improvements and scaling",
            "value": "YouTube automation market"
        },
        {
            "priority": "⚡ HIGH",
            "task": "Enhance Dream.os (184 files)",
            "action": "Add AI features and user interface",
            "value": "AI-powered productivity tool"
        },
        {
            "priority": "⚡ HIGH",
            "task": "Scale Email-Cleanup-App (93 files)",
            "action": "Enterprise features and API",
            "value": "B2B email management market"
        },
        {
            "priority": "📈 MEDIUM",
            "task": "Document HCshinobi (116 files)",
            "action": "Create comprehensive documentation",
            "value": "Open source community building"
        },
        {
            "priority": "📈 MEDIUM",
            "task": "Optimize DreamVault (55 files)",
            "action": "Performance and security audit",
            "value": "Data storage and privacy market"
        },
        {
            "priority": "📈 MEDIUM",
            "task": "Enhance projectscanner (50 files)",
            "action": "Add more analysis features",
            "value": "Developer tool market"
        },
        {
            "priority": "📈 MEDIUM",
            "task": "Scale Side-projects (92 files)",
            "action": "Organize and prioritize development",
            "value": "Portfolio optimization"
        }
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{i:2d}. {task['priority']}")
        print(f"    Task: {task['task']}")
        print(f"    Action: {task['action']}")
        print(f"    Value: {task['value']}")
    
    print(f"\n🚀 IMMEDIATE NEXT STEPS:")
    print("=" * 60)
    print("1. 🔥 Deploy Victor.os as MVP")
    print("2. 🔥 Launch TradingRobotPlugWeb beta")
    print("3. 🔥 Extract IP from ideas repository")
    print("4. ⚡ Optimize MeTuber performance")
    print("5. ⚡ Enhance Dream.os with AI features")
    
    return tasks

if __name__ == "__main__":
    analyze_portfolio() 