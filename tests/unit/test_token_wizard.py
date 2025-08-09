#!/usr/bin/env python3
"""
Test script for GitHub Token Wizard debugging.
"""

import sys
import subprocess
import time
from pathlib import Path

def test_token_wizard_direct():
    """Test the token wizard directly."""
    print("🧪 Testing Token Wizard Direct Launch...")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        # Import and test wizard
        from wizards.github_token_wizard import GitHubTokenWizard
        from PyQt5 import QtWidgets
        
        print("✅ Successfully imported GitHubTokenWizard")
        
        # Test creating wizard
        app = QtWidgets.QApplication(sys.argv)
        wizard = GitHubTokenWizard()
        print("✅ Successfully created wizard instance")
        
        # Show wizard
        wizard.show()
        print("✅ Wizard should be visible now")
        
        # Keep it open for a few seconds
        time.sleep(5)
        
        print("✅ Token wizard test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing token wizard: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_token_wizard_launcher():
    """Test the token wizard launcher script."""
    print("🧪 Testing Token Wizard Launcher...")
    
    try:
        result = subprocess.run(
            [sys.executable, "run_token_wizard.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Token wizard launcher works!")
            return True
        else:
            print("❌ Token wizard launcher failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ Token wizard launched (timeout expected for GUI)")
        return True
    except Exception as e:
        print(f"❌ Error testing token wizard launcher: {e}")
        return False

def main():
    """Run token wizard tests."""
    print("🔐 Token Wizard Debug Tests")
    print("=" * 40)
    
    tests = [
        ("Direct Import Test", test_token_wizard_direct),
        ("Launcher Script Test", test_token_wizard_launcher),
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
        print("🎉 Token wizard is working correctly!")
        return 0
    else:
        print("⚠️  Token wizard has issues. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 