"""
MODULE: demo_gui
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""
Demo script showing how to use the enhanced ProjectScanner GUI features.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from projectscanner.gui import ProjectScannerGUI, ScanWorker, GitHubScanner
from PyQt5 import QtWidgets


# Concept: TODO - Explain the core idea behind demo_scan_local_directory
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 50 lines > 30 limit)
def demo_scan_local_directory():
# Concept: TODO
# Trade-off: TODO
# Execution: TODO
    """Demonstrate scanning a local directory."""
    print("Demo: Scanning local directory")
    
    # Example: scan the current project
    project_path = Path(__file__).parent
    
    # Create a scan worker
    worker = ScanWorker(project_path)
    
    # Connect signals to see progress
    # Concept: TODO - Explain the core idea behind on_progress
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def on_progress(message):
        print(f"Progress: {message}")
    
    # Concept: TODO - Explain the core idea behind on_finished
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def on_finished(result):
        print(f"Scan finished! Found {len(result['analysis_data'])} files")
        print(f"Results saved to: {result['analysis_file']}")
    
    # Concept: TODO - Explain the core idea behind on_error
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def on_error(error):
    # Concept: TODO - Purpose of on_error
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        print(f"Scan error: {error}")
    
    worker.progress.connect(on_progress)
    worker.finished.connect(on_finished)
    worker.error.connect(on_error)
    
    # Start the scan
    worker.start()
    
    # Wait for completion (in a real GUI, this would be non-blocking)
    worker.wait()
    
    return worker


# Concept: TODO - Explain the core idea behind demo_github_cloning
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def demo_github_cloning():
# Concept: TODO
# Trade-off: TODO
# Execution: TODO
    """Demonstrate GitHub repository cloning."""
    print("\nDemo: GitHub repository cloning")
    
    # Example repository
    repo_url = "https://github.com/python/cpython"
    
    try:
        # Create temporary directory
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        
        print(f"Cloning {repo_url} to {temp_dir}")
        
        # Clone the repository
        clone_path = GitHubScanner.clone_repository(repo_url, temp_dir)
        
        print(f"Repository cloned to: {clone_path}")
        print(f"Repository size: {sum(f.stat().st_size for f in clone_path.rglob('*') if f.is_file())} bytes")
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        print("Temporary directory cleaned up")
        
    except Exception as e:
        print(f"Error cloning repository: {e}")


# Concept: TODO - Explain the core idea behind demo_gui_features
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 35 lines > 30 limit)
def demo_gui_features():
    """Demonstrate GUI features."""
# Concept: TODO - Purpose of demo_github_cloning
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
# Concept: TODO - Purpose of demo_github_cloning
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    print("\nDemo: GUI Features")
    
    # Create GUI application
    app = QtWidgets.QApplication(sys.argv)
    
    # Create the main window
    gui = ProjectScannerGUI()
    
    print("GUI Features available:")
    print("1. Directory scanning with browse dialog")
    print("2. GitHub repository scanning")
    print("3. Project library management")
    print("4. Real-time progress tracking")
    print("5. Results viewer with tree structure")
    print("6. Export/import library functionality")
    
    # Show the GUI
    gui.show()
    
    print("GUI window opened. You can:")
    print("- Browse and scan local directories")
    print("- Enter GitHub URLs to scan repositories")
    print("- Save scans to the project library")
    print("- View and manage your scan history")
    
    # Run the application
    app.exec_()


if __name__ == "__main__":
    print("ProjectScanner Enhanced GUI Demo")
    print("=" * 40)
    
    # Demo 1: Local directory scanning
    demo_scan_local_directory()
    
    # Demo 2: GitHub repository cloning
    demo_github_cloning()
    
    # Demo 3: GUI features
    demo_gui_features() 
# Concept: TODO - Purpose of demo_gui_features
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach