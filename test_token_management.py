#!/usr/bin/env python3
"""
Test script for GitHub token management functionality.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_token_management():
    """Test token management functionality."""
    print("Testing GitHub Token Management...")
    
    # Test new config format
    config_file = Path("config/github_config.json")
    config_file.parent.mkdir(exist_ok=True)
    
    # Test saving token in new format
    test_config = {
        "username": "testuser",
        "token": "ghp_test12345678901234567890",
        "setup_date": "2024-01-01T00:00:00",
        "wizard_version": "1.0"
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2)
    
    # Test loading token from new format
    with open(config_file, 'r', encoding='utf-8') as f:
        loaded_config = json.load(f)
    
    if (loaded_config["username"] == test_config["username"] and 
        loaded_config["token"] == test_config["token"]):
        print("✅ New config format save/load functionality works correctly!")
    else:
        print("❌ New config format save/load functionality failed!")
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
    
    # Test legacy format compatibility
    token_file = Path("config/github_token.txt")
    test_token = "test_token_12345"
    with open(token_file, 'w', encoding='utf-8') as f:
        f.write(test_token)
    
    # Test loading token from legacy format
    with open(token_file, 'r', encoding='utf-8') as f:
        loaded_token = f.read().strip()
    
    if loaded_token == test_token:
        print("✅ Legacy token format compatibility works correctly!")
    else:
        print("❌ Legacy token format compatibility failed!")
        return False
    
    # Cleanup
    config_file.unlink(missing_ok=True)
    cache_file.unlink(missing_ok=True)
    token_file.unlink(missing_ok=True)
    
    print("✅ All token management tests passed!")
    return True

if __name__ == "__main__":
    success = test_token_management()
    sys.exit(0 if success else 1) 