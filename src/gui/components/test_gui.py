"""
MODULE: test_gui
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""
Test script to verify the GUI launches correctly.
"""

import sys
import subprocess
import time
from pathlib import Path

# Concept: TODO - Explain the core idea behind test_gui_launch
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 32 lines > 30 limit)
def test_gui_launch():
# Concept: TODO
# Trade-off: TODO
# Execution: TODO
    """Test that the GUI launches without errors."""
    print("🧪 Testing GUI launch...")
    
    try:
        # Launch GUI in background
        process = subprocess.Popen(
            [sys.executable, "launch.py", "gui"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a few seconds for GUI to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ GUI launched successfully!")
            # Terminate the process
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ GUI failed to launch:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing GUI: {e}")
        return False

# Concept: TODO - Explain the core idea behind test_launcher
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def test_launcher():
    """Test the launcher script."""
# Concept: TODO - Purpose of test_gui_launch
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    print("🧪 Testing launcher script...")
    
    try:
        result = subprocess.run(
            [sys.executable, "launch.py", "help"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if "Project Scanner - Advanced Code Analysis Tool" in result.stdout:
            print("✅ Launcher script works correctly!")
            return True
        else:
            print("❌ Launcher script output unexpected")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Launcher script failed: {e}")
        return False

# Concept: TODO - Explain the core idea behind test_scanner
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def test_scanner():
    """Test the scanner functionality."""
# Concept: TODO - Purpose of test_launcher
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    print("🧪 Testing scanner functionality...")
    
    try:
        result = subprocess.run(
            [sys.executable, "launch.py", "scan", ".", "--verbose"],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0 and "Scan completed successfully!" in result.stdout:
            print("✅ Scanner works correctly!")
            return True
        else:
            print(f"❌ Scanner failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Scanner timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing scanner: {e}")
        return False

# Concept: TODO - Explain the core idea behind main
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 32 lines > 30 limit)
def main():
    """Run all tests."""
# Concept: TODO - Purpose of test_scanner
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    print("🚀 Project Scanner - Test Suite")
    print("=" * 40)
    
    tests = [
        ("Launcher Script", test_launcher),
        ("Scanner Functionality", test_scanner),
        ("GUI Launch", test_gui_launch),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Project is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
# Concept: TODO - Purpose of main
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach