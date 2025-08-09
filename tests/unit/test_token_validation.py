#!/usr/bin/env python3
"""
Test script for token validation logic.
"""

import sys
from pathlib import Path

def test_token_validation():
    """Test the token validation logic."""
    print("🧪 Testing Token Validation Logic...")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        # Import the TokenSetupPage class
        from wizards.github_token_wizard import TokenSetupPage
        from PyQt5 import QtWidgets
        
        # Create QApplication
        app = QtWidgets.QApplication(sys.argv)
        
        # Create the page
        page = TokenSetupPage()
        
        # Test cases
        test_cases = [
            ("", "", False, "Empty token and username"),
            ("testuser", "", False, "Empty token"),
            ("", "ghp_test12345678901234567890", False, "Empty username"),
            ("testuser", "short", False, "Token too short"),
            ("testuser", "ghp_test12345678901234567890", True, "Valid ghp_ token"),
            ("testuser", "gho_test12345678901234567890", True, "Valid gho_ token"),
            ("testuser", "ghu_test12345678901234567890", True, "Valid ghu_ token"),
            ("testuser", "ghs_test12345678901234567890", True, "Valid ghs_ token"),
            ("testuser", "ghr_test12345678901234567890", True, "Valid ghr_ token"),
            ("testuser", "invalid_token_format_but_long_enough", True, "Invalid format but allowed"),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for username, token, expected, description in test_cases:
            # Set the values
            page.username_edit.setText(username)
            page.token_edit.setText(token)
            
            # Check validation
            result = page.validate_token()
            
            if result == expected:
                print(f"✅ {description}: {result}")
                passed += 1
            else:
                print(f"❌ {description}: expected {expected}, got {result}")
        
        print(f"\n📊 Token Validation Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All token validation tests passed!")
            return True
        else:
            print("⚠️ Some token validation tests failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token validation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run token validation tests."""
    print("🔐 Token Validation Tests")
    print("=" * 40)
    
    success = test_token_validation()
    
    if success:
        print("\n✅ Token validation is working correctly!")
        return 0
    else:
        print("\n❌ Token validation has issues!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 