#!/usr/bin/env python3
"""
GitHub Token Setup Wizard - Easy setup for private repository scanning.
"""

import sys
import json
import webbrowser
import subprocess
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class GitHubTokenWizard:
    """Wizard for setting up GitHub Personal Access Tokens."""
    
    def __init__(self):
        self.token = None
        self.username = None
        self.output_dir = "github_library_enhanced"
        
    def print_header(self):
        """Print the wizard header."""
        print("=" * 60)
        print("🔐 GitHub Token Setup Wizard")
        print("=" * 60)
        print("This wizard will help you set up access to your private repositories.")
        print("Follow the steps below to create a GitHub Personal Access Token.")
        print()
    
    def get_username(self) -> str:
        """Get the GitHub username from user."""
        print("Step 1: Enter your GitHub username")
        print("-" * 40)
        
        while True:
            username = input("GitHub username: ").strip()
            if username:
                self.username = username
                print(f"✅ Username set to: {username}")
                return username
            else:
                print("❌ Please enter a valid username.")
    
    def open_github_settings(self):
        """Open GitHub settings page in browser."""
        print("\nStep 2: Create GitHub Personal Access Token")
        print("-" * 40)
        print("I'll open GitHub in your browser to create a token.")
        print("Follow these steps:")
        print("1. Click 'Generate new token' → 'Generate new token (classic)'")
        print("2. Set expiration to 90 days")
        print("3. Select these scopes:")
        print("   ✅ repo (Full control of private repositories)")
        print("   ✅ read:org (Read organization data)")
        print("   ✅ read:user (Read user data)")
        print("4. Click 'Generate token'")
        print("5. Copy the token (you won't see it again!)")
        print()
        
        input("Press Enter to open GitHub settings...")
        
        # Open GitHub settings page
        settings_url = "https://github.com/settings/tokens"
        try:
            webbrowser.open(settings_url)
            print(f"🌐 Opened: {settings_url}")
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
            print(f"Please manually visit: {settings_url}")
    
    def get_token(self) -> Optional[str]:
        """Get the GitHub token from user."""
        print("\nStep 3: Enter your GitHub Personal Access Token")
        print("-" * 40)
        print("⚠️  IMPORTANT: The token will be hidden when you type it.")
        print("   This is for security - tokens are sensitive like passwords!")
        print()
        
        while True:
            try:
                import getpass
                token = getpass.getpass("GitHub Personal Access Token: ")
                
                if not token:
                    print("❌ Please enter a valid token.")
                    continue
                
                # Basic validation (GitHub tokens start with ghp_)
                if not token.startswith('ghp_'):
                    print("⚠️  Warning: GitHub tokens usually start with 'ghp_'")
                    response = input("Continue anyway? (y/N): ").lower()
                    if response != 'y':
                        continue
                
                self.token = token
                print("✅ Token received!")
                return token
                
            except KeyboardInterrupt:
                print("\n❌ Setup cancelled.")
                return None
            except Exception as e:
                print(f"❌ Error: {e}")
                return None
    
    def test_token(self, username: str, token: str) -> bool:
        """Test the GitHub token by making an API call."""
        print("\nStep 4: Testing your GitHub token")
        print("-" * 40)
        
        try:
            import requests
            
            # Test the token with a simple API call
            headers = {'Authorization': f'ttoken {token}'}
            response = requests.get(f'https://api.github.com/user', headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Token is valid!")
                print(f"   Authenticated as: {user_data.get('login', 'Unknown')}")
                print(f"   Name: {user_data.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ Token validation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except ImportError:
            print("❌ Error: requests library not found.")
            print("   Install with: pip install requests")
            return False
        except Exception as e:
            print(f"❌ Error testing token: {e}")
            return False
    
    def save_token_config(self, username: str, token: str):
        """Save token configuration securely."""
        print("\nStep 5: Saving configuration")
        print("-" * 40)
        
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "github_token.json"
        
        # Save configuration (token will be stored locally)
        config = {
            'username': username,
            'token': token,
            'created_at': str(Path().cwd()),
            'output_dir': self.output_dir
        }
        
        try:
            with config_file.open('w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to: {config_file}")
            print("   ⚠️  Keep this file secure - it contains your token!")
            
            # Add to .gitignore if not already there
            gitignore_file = Path(".gitignore")
            if gitignore_file.exists():
                with gitignore_file.open('r') as f:
                    content = f.read()
                if "config/github_token.json" not in content:
                    with gitignore_file.open('a') as f:
                        f.write("\n# GitHub token configuration\nconfig/github_token.json\n")
                    print("✅ Added token file to .gitignore")
            else:
                with gitignore_file.open('w') as f:
                    f.write("# GitHub token configuration\nconfig/github_token.json\n")
                print("✅ Created .gitignore with token protection")
                
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def run_enhanced_scanner(self, username: str, token: str):
        """Run the enhanced GitHub library scanner."""
        print("\nStep 6: Running Enhanced GitHub Scanner")
        print("-" * 40)
        print("🚀 Starting scan of your repositories (public + private)...")
        print()
        
        try:
            # Import and run the enhanced scanner
            from github_library_scanner_private import EnhancedGitHubLibraryScanner
            
            scanner = EnhancedGitHubLibraryScanner(username, token, self.output_dir)
            scanner.scan_all_repositories()
            
            # Generate summary
            summary = scanner.generate_library_summary()
            print("\n📊 Scan Summary:")
            print(json.dumps(summary, indent=2))
            
            return True
            
        except ImportError:
            print("❌ Error: Could not import enhanced scanner.")
            print("   Make sure github_library_scanner_private.py exists.")
            return False
        except Exception as e:
            print(f"❌ Error running scanner: {e}")
            return False
    
    def show_next_steps(self):
        """Show next steps after successful setup."""
        print("\n🎉 Setup Complete!")
        print("=" * 60)
        print("Your GitHub token is now configured and working!")
        print()
        print("📁 Your enhanced library is saved in: github_library_enhanced/")
        print("🔐 Your token is stored in: config/github_token.json")
        print()
        print("🔄 To run future scans:")
        print("   python github_library_scanner_private.py YOUR_USERNAME --token YOUR_TOKEN")
        print()
        print("📊 To analyze your enhanced library:")
        print("   python deep_github_analysis.py")
        print()
        print("🔒 Security reminders:")
        print("   • Keep your token secure")
        print("   • Token expires in 90 days")
        print("   • Don't commit token to Git")
        print()
    
    def run_wizard(self):
        """Run the complete wizard."""
        try:
            self.print_header()
            
            # Step 1: Get username
            username = self.get_username()
            
            # Step 2: Open GitHub settings
            self.open_github_settings()
            
            # Step 3: Get token
            token = self.get_token()
            if not token:
                print("❌ Setup cancelled.")
                return False
            
            # Step 4: Test token
            if not self.test_token(username, token):
                print("❌ Token validation failed. Please check your token.")
                return False
            
            # Step 5: Save configuration
            self.save_token_config(username, token)
            
            # Step 6: Run enhanced scanner
            if not self.run_enhanced_scanner(username, token):
                print("❌ Scanner failed. Check the error messages above.")
                return False
            
            # Show next steps
            self.show_next_steps()
            
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False


def load_existing_config() -> Optional[dict]:
    """Load existing GitHub token configuration."""
    config_file = Path("config/github_token.json")
    if config_file.exists():
        try:
            with config_file.open('r') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def main():
    """Main function for the GitHub token wizard."""
    print("🔐 GitHub Token Setup Wizard")
    print("=" * 40)
    
    # Check for existing configuration
    existing_config = load_existing_config()
    if existing_config:
        print("📁 Found existing GitHub token configuration!")
        print(f"   Username: {existing_config.get('username', 'Unknown')}")
        print(f"   Output directory: {existing_config.get('output_dir', 'Unknown')}")
        print()
        
        response = input("Use existing configuration? (Y/n): ").lower()
        if response != 'n':
            # Use existing configuration
            username = existing_config['username']
            token = existing_config['token']
            output_dir = existing_config.get('output_dir', 'github_library_enhanced')
            
            print(f"✅ Using existing configuration for: {username}")
            
            # Test token
            wizard = GitHubTokenWizard()
            if wizard.test_token(username, token):
                print("✅ Token is still valid!")
                
                # Run scanner
                if wizard.run_enhanced_scanner(username, token):
                    wizard.show_next_steps()
                    return True
                else:
                    print("❌ Scanner failed with existing configuration.")
                    print("   You may need to regenerate your token.")
            else:
                print("❌ Token is invalid or expired.")
                print("   You need to create a new token.")
        
        print("Starting fresh setup...")
        print()
    
    # Run the wizard
    wizard = GitHubTokenWizard()
    return wizard.run_wizard()


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please try again.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!") 