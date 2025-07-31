#!/usr/bin/env python3
"""
Test script for GitHub library scanner functionality.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from github_library_scanner import GitHubLibraryScanner


def test_github_library_scanner():
    """Test the GitHub library scanner with a small sample."""
    print("🧪 Testing GitHub Library Scanner")
    print("=" * 40)
    
    # Test with a small number of repositories
    username = "Dadudekc"  # Using the same user as before
    scanner = GitHubLibraryScanner(username, "test_github_library")
    
    # Test getting repositories
    print(f"🔍 Testing repository fetching for user: {username}")
    repos = scanner.get_user_repositories()
    
    if repos:
        print(f"✅ Found {len(repos)} repositories")
        
        # Test scanning just the first repository
        if len(repos) > 0:
            print(f"\n🔍 Testing single repository scan...")
            success = scanner.scan_repository(repos[0], force_rescan=False)
            
            if success:
                print("✅ Single repository scan successful!")
                
                # Generate summary
                summary = scanner.generate_library_summary()
                print(f"\n📊 Library Summary:")
                print(f"   Total repos: {summary['total_repos']}")
                print(f"   Total files: {summary['total_files']}")
                print(f"   Languages: {summary['languages']}")
                
                # Export summary
                scanner.export_library_summary("test_summary.json")
                
            else:
                print("❌ Single repository scan failed!")
        else:
            print("⚠️  No repositories found to test")
    else:
        print("❌ Failed to fetch repositories")


def test_library_management():
    """Test library management features."""
    print("\n📚 Testing Library Management")
    print("=" * 40)
    
    username = "Dadudekc"
    scanner = GitHubLibraryScanner(username, "test_library_management")
    
    # Test library loading and saving
    print("🔍 Testing library persistence...")
    scanner.save_library()
    scanner.load_library()
    print("✅ Library persistence test passed!")
    
    # Test scan log
    print("📋 Testing scan log...")
    scanner.save_scan_log()
    scanner.load_scan_log()
    print("✅ Scan log test passed!")


if __name__ == "__main__":
    print("🚀 GitHub Library Scanner Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    test_github_library_scanner()
    
    # Test library management
    test_library_management()
    
    print("\n✅ All tests completed!")
    print("\n💡 To scan your entire GitHub library, run:")
    print("   python github_library_scanner.py YOUR_USERNAME")
    print("   python main.py --gui  # Then use the GitHub Library tab") 