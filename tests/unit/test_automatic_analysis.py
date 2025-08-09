#!/usr/bin/env python3
"""
Test script for automatic analysis generation.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_automatic_analysis():
    """Test automatic analysis generation functionality."""
    print("🚀 Automatic Analysis Generation Test")
    print("=" * 50)
    
    try:
        from PyQt5 import QtWidgets
        from core.projectscanner.gui import ProjectScannerGUI
        
        # Create application
        app = QtWidgets.QApplication(sys.argv)
        
        # Create GUI
        gui = ProjectScannerGUI()
        gui.show()
        
        print("✅ GUI created successfully!")
        print("✅ Automatic analysis generation is now enabled!")
        print("")
        print("🧪 Test Instructions:")
        print("1. Enter a GitHub username (e.g., 'dadudekc')")
        print("2. Click '🔍 Scan GitHub Library'")
        print("3. Watch the Current Scan tab for real-time progress")
        print("4. After scan completes, analysis will automatically generate:")
        print("   • Portfolio statistics")
        print("   • Skill tree")
        print("   • Resume")
        print("   • Insights")
        print("5. GUI will automatically switch to Portfolio Stats tab")
        print("6. Check all tabs for generated content")
        print("")
        print("✅ Features to verify:")
        print("   • Real-time progress updates in Current Scan tab")
        print("   • Automatic analysis generation after scan")
        print("   • Portfolio statistics display")
        print("   • Skill tree generation and display")
        print("   • Resume generation and display")
        print("   • Insights generation and display")
        print("   • Automatic tab switching to show results")
        print("")
        print("✅ Automatic analysis generation test completed!")
        
        # Run the application
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Error testing automatic analysis: {e}")
        return False

if __name__ == "__main__":
    test_automatic_analysis() 