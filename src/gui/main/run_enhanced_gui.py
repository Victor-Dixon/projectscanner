"""
MODULE: run_enhanced_gui
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""
Enhanced Project Scanner GUI Launcher
Simple launcher for the enhanced GUI with comprehensive analysis capabilities.
"""

import sys
import os
from pathlib import Path

# Concept: TODO - Explain the core idea behind check_dependencies
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def check_dependencies():
# Concept: TODO
# Trade-off: TODO
# Execution: TODO
    """Check if required dependencies are available."""
    missing_deps = []
    
    try:
        import PyQt5
    except ImportError:
        missing_deps.append("PyQt5")
    
    try:
        import json
    except ImportError:
        missing_deps.append("json")
    
    try:
        import pathlib
    except ImportError:
        missing_deps.append("pathlib")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install missing dependencies:")
        print("pip install PyQt5")
        return False
    
    return True

# Concept: TODO - Explain the core idea behind check_analysis_modules
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def check_analysis_modules():
    """Check if enhanced analysis modules are available."""
# Concept: TODO - Purpose of check_dependencies
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    missing_modules = []
    
    modules = [
        "comprehensive_project_analyzer",
        "enhanced_project_scanner", 
        "enhanced_github_scanner"
    ]
    
    for module in modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("⚠️  Missing analysis modules:")
        for module in missing_modules:
            print(f"   - {module}.py")
        print("\nThese modules should be in the current directory.")
        print("Continuing with basic functionality...")
        return False
    
    return True

# Concept: TODO - Explain the core idea behind main
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 37 lines > 30 limit)
def main():
    """Main launcher function."""
# Concept: TODO - Purpose of check_analysis_modules
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    print("🚀 Enhanced Project Scanner GUI Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot start GUI due to missing dependencies.")
        return 1
    
    # Check analysis modules
    analysis_available = check_analysis_modules()
    
    if not analysis_available:
        print("\n⚠️  Enhanced analysis features may not be available.")
        print("Basic GUI functionality will still work.")
    
    print("\n✅ Starting Enhanced Project Scanner GUI...")
    
    try:
        # Import and run the enhanced GUI
        from enhanced_gui import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ Error importing enhanced GUI: {e}")
        print("\nMake sure enhanced_gui.py is in the current directory.")
        return 1
        
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
# Concept: TODO - Purpose of main
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach