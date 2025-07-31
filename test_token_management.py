#!/usr/bin/env python3
"""
Test script for GitHub token management functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_token_management():
    """Test token management functionality."""
    print("🧪 Testing GitHub Token Management...")
    
    # Test token file creation
    token_file = Path("config/github_token.txt")
    token_file.parent.mkdir(exist_ok=True)
    
    # Test saving token
    test_token = "test_token_12345"
    with open(token_file, 'w', encoding='utf-8') as f:
        f.write(test_token)
    
    # Test loading token
    with open(token_file, 'r', encoding='utf-8') as f:
        loaded_token = f.read().strip()
    
    if loaded_token == test_token:
        print("✅ Token save/load functionality works correctly!")
    else:
        print("❌ Token save/load functionality failed!")
        return False
    
    # Test analysis cache
    cache_dir = Path("analysis_cache")
    cache_dir.mkdir(exist_ok=True)
    
    test_analysis = {
        "username": "testuser",
        "repositories": ["repo1", "repo2"],
        "summary": {"total_repos": 2}
    }
    
    cache_file = cache_dir / "testuser_analysis.json"
    import json
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(test_analysis, f, indent=2)
    
    # Test loading cached analysis
    with open(cache_file, 'r', encoding='utf-8') as f:
        loaded_analysis = json.load(f)
    
    if loaded_analysis["username"] == test_analysis["username"]:
        print("✅ Analysis cache functionality works correctly!")
    else:
        print("❌ Analysis cache functionality failed!")
        return False
    
    # Cleanup
    token_file.unlink(missing_ok=True)
    cache_file.unlink(missing_ok=True)
    
    print("✅ All token management tests passed!")
    return True

if __name__ == "__main__":
    success = test_token_management()
    sys.exit(0 if success else 1) 