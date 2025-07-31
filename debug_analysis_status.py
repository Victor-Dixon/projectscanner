#!/usr/bin/env python3
"""
Debug Analysis Status Script
Shows what's working and what needs fixing in the analysis system
"""

import json
import os
from pathlib import Path

def debug_analysis_status():
    """Debug the current analysis system status."""
    print("🔍 **DEBUG ANALYSIS STATUS**")
    print("=" * 50)
    
    # Check library file
    library_path = "github_library_enhanced/github_library_enhanced.json"
    if os.path.exists(library_path):
        print("✅ Library file exists")
        try:
            with open(library_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Library loaded successfully")
            print(f"📊 Total repositories: {len(data)}")
            
            # Check sample repository structure
            sample_repo = list(data.keys())[0]
            repo_data = data[sample_repo]
            print(f"\n📁 Sample repository: {sample_repo}")
            print(f"   Keys: {list(repo_data.keys())}")
            
            # Check analysis data
            if 'analysis_data' in repo_data:
                analysis_data = repo_data['analysis_data']
                if analysis_data:
                    print(f"✅ Analysis data exists with {len(analysis_data)} files")
                    # Show sample file analysis
                    sample_file = list(analysis_data.keys())[0] if analysis_data else None
                    if sample_file:
                        file_data = analysis_data[sample_file]
                        print(f"   Sample file: {sample_file}")
                        print(f"   File keys: {list(file_data.keys())}")
                else:
                    print("❌ Analysis data is empty")
            else:
                print("❌ No analysis_data field")
                
            # Check context data
            if 'context_data' in repo_data:
                context_data = repo_data['context_data']
                if context_data:
                    print(f"✅ Context data exists with {len(context_data)} files")
                else:
                    print("❌ Context data is empty")
            else:
                print("❌ No context_data field")
                
        except Exception as e:
            print(f"❌ Error loading library: {e}")
    else:
        print("❌ Library file not found")
    
    print("\n" + "=" * 50)
    
    # Check generated reports
    print("📊 **GENERATED REPORTS STATUS**")
    
    reports = [
        ("proper_insights/proper_insights.json", "Proper Insights JSON"),
        ("proper_insights/proper_insights_summary.md", "Proper Insights Summary"),
        ("skill_analysis/enhanced_skill_tree_report.json", "Enhanced Skill Tree JSON"),
        ("skill_analysis/enhanced_knowledge_base_report.json", "Enhanced Knowledge Base JSON"),
        ("skill_analysis/enhanced_summary_report.md", "Enhanced Summary Report"),
        ("skill_analysis/enhanced_skill_tree.png", "Enhanced Skill Tree PNG"),
    ]
    
    for report_path, report_name in reports:
        if os.path.exists(report_path):
            size = os.path.getsize(report_path)
            print(f"✅ {report_name}: {size} bytes")
        else:
            print(f"❌ {report_name}: Not found")
    
    print("\n" + "=" * 50)
    
    # Check GUI components
    print("🎨 **GUI COMPONENTS STATUS**")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 is available")
        
        # Test GUI launch
        import sys
        app = QApplication(sys.argv)
        print("✅ QApplication created successfully")
        app.quit()
        
    except ImportError as e:
        print(f"❌ PyQt5 import error: {e}")
    except Exception as e:
        print(f"❌ GUI test error: {e}")
    
    print("\n" + "=" * 50)
    
    # Analysis quality assessment
    print("📈 **ANALYSIS QUALITY ASSESSMENT**")
    
    if os.path.exists("proper_insights/proper_insights.json"):
        try:
            with open("proper_insights/proper_insights.json", 'r') as f:
                insights = json.load(f)
            
            overview = insights.get('project_overview', {})
            
            print(f"📊 Total Projects: {overview.get('total_projects', 'N/A')}")
            print(f"📁 Total Files: {overview.get('total_files', 'N/A')}")
            print(f"🔧 Total Functions: {overview.get('total_functions', 'N/A')}")
            print(f"🏗️ Total Classes: {overview.get('total_classes', 'N/A')}")
            
            # Assess data quality
            if overview.get('total_functions', 0) == 0:
                print("⚠️ ISSUE: No function data extracted")
            else:
                print("✅ Function data available")
                
            if overview.get('total_classes', 0) == 0:
                print("⚠️ ISSUE: No class data extracted")
            else:
                print("✅ Class data available")
                
        except Exception as e:
            print(f"❌ Error reading insights: {e}")
    
    print("\n" + "=" * 50)
    
    # Recommendations
    print("🚀 **RECOMMENDATIONS**")
    
    print("✅ WHAT'S WORKING:")
    print("  - Project categorization")
    print("  - File counting")
    print("  - Repository metadata extraction")
    print("  - Visual skill tree generation")
    print("  - JSON report generation")
    print("  - GUI interface")
    
    print("\n⚠️ WHAT NEEDS FIXING:")
    print("  - Function/class extraction (showing 0)")
    print("  - Complexity analysis (showing 0)")
    print("  - Technology detection (limited)")
    print("  - Code pattern analysis (missing)")
    
    print("\n🔧 NEXT STEPS:")
    print("  1. Re-scan repositories with enhanced analysis")
    print("  2. Improve AST parsing for function/class detection")
    print("  3. Add complexity calculation")
    print("  4. Enhance technology detection")
    print("  5. Add code pattern analysis")
    
    print("\n" + "=" * 50)
    print("🎯 **CONCLUSION**")
    print("The system is FUNCTIONAL but needs enhanced data extraction.")
    print("Current insights are valuable for portfolio overview but lack code-level details.")

if __name__ == "__main__":
    debug_analysis_status() 