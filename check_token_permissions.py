#!/usr/bin/env python3
"""
Check GitHub token permissions and accessible repositories.
"""

import requests
import json

def check_token_permissions(token):
    """Check what the token can access."""
    headers = {'Authorization': f'token {token}'}
    
    print("🔍 Checking GitHub token permissions...")
    print(f"Token: {token[:10]}...{token[-4:]}")
    print()
    
    # Check user info
    try:
        response = requests.get('https://api.github.com/user', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Token is valid!")
            print(f"   User: {user_data.get('login', 'Unknown')}")
            print(f"   Name: {user_data.get('name', 'Unknown')}")
            print(f"   Public repos: {user_data.get('public_repos', 0)}")
            print(f"   Private repos: {user_data.get('total_private_repos', 0)}")
            print()
        else:
            print(f"❌ Token validation failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return
    
    # Check repositories
    try:
        print("📦 Checking accessible repositories...")
        response = requests.get('https://api.github.com/user/repos?per_page=100', headers=headers)
        if response.status_code == 200:
            repos = response.json()
            private_count = sum(1 for repo in repos if repo.get('private', False))
            public_count = sum(1 for repo in repos if not repo.get('private', False))
            
            print(f"   Total repos found: {len(repos)}")
            print(f"   Public repos: {public_count}")
            print(f"   Private repos: {private_count}")
            print()
            
            if private_count == 0:
                print("⚠️  No private repositories found!")
                print("   This could mean:")
                print("   1. Your token doesn't have 'repo' scope")
                print("   2. You don't have any private repositories")
                print("   3. The token permissions are insufficient")
                print()
                print("🔧 To fix this:")
                print("   1. Go to https://github.com/settings/tokens")
                print("   2. Edit your token")
                print("   3. Make sure 'repo' scope is selected")
                print("   4. Save the changes")
                print()
            
            print("📋 First 10 repositories:")
            for i, repo in enumerate(repos[:10], 1):
                visibility = "🔒 PRIVATE" if repo.get('private') else "🌐 PUBLIC"
                print(f"   {i:2d}. {repo['name']} ({visibility})")
                
        else:
            print(f"❌ Error fetching repositories: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking repositories: {e}")

if __name__ == "__main__":
    # Replace with your GitHub token
    token = input("Enter your GitHub token: ")
    check_token_permissions(token) 