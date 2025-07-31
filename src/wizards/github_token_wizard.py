#!/usr/bin/env python3
"""
GitHub Token Wizard - Easy token generation and setup
"""

import sys
import webbrowser
import json
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal

class GitHubTokenWizard(QtWidgets.QWizard):
    """Wizard for generating and setting up GitHub tokens."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 GitHub Token Setup Wizard")
        
        # Center the wizard on screen
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        x = (screen.width() - 800) // 2
        y = (screen.height() - 600) // 2
        self.setGeometry(x, y, 800, 600)
        
        # Make sure it's on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        # Configure wizard
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        self.setOption(QtWidgets.QWizard.HaveHelpButton, True)
        self.setOption(QtWidgets.QWizard.HaveFinishButtonOnEarlyPages, False)
        
        # Add pages
        self.addPage(WelcomePage())
        self.addPage(TokenGenerationPage())
        self.addPage(TokenSetupPage())
        self.addPage(VerificationPage())
        self.addPage(CompletionPage())
        
        # Connect signals
        self.helpRequested.connect(self.show_help)
        self.finished.connect(self.on_wizard_finished)
        
        # Store token
        self.github_token = None
        self.github_username = None

    def show_help(self):
        """Show help information."""
        QtWidgets.QMessageBox.information(
            self, "Help",
            "This wizard will help you create a GitHub Personal Access Token.\n\n"
            "The token allows the Project Scanner to access your private repositories "
            "and perform comprehensive analysis of your GitHub portfolio.\n\n"
            "Your token will be stored securely and only used for repository scanning."
        )

    def on_wizard_finished(self, result):
        """Handle wizard completion."""
        if result == QtWidgets.QWizard.Accepted:
            # Save token to config
            self.save_token_to_config()
            QtWidgets.QMessageBox.information(
                self, "Setup Complete",
                "✅ GitHub token setup completed successfully!\n\n"
                "Your token has been saved and you can now scan private repositories."
            )

    def save_token_to_config(self):
        """Save token to configuration file."""
        if self.github_token and self.github_username:
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / "github_config.json"
            config_data = {
                "username": self.github_username,
                "token": self.github_token,
                "setup_date": str(Path().cwd()),
                "wizard_version": "1.0"
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)


class WelcomePage(QtWidgets.QWizardPage):
    """Welcome page explaining the wizard."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("🔐 Welcome to GitHub Token Setup")
        self.setSubTitle("This wizard will help you create a GitHub Personal Access Token for private repository access.")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Welcome text
        welcome_text = QtWidgets.QLabel(
            "This wizard will guide you through:\n\n"
            "1. 🌐 Opening GitHub token creation page\n"
            "2. ⚙️ Configuring the correct permissions\n"
            "3. 🔑 Copying and pasting your token\n"
            "4. ✅ Verifying the token works\n"
            "5. 💾 Securely saving the token\n\n"
            "Your token will be used to access your private repositories "
            "for comprehensive portfolio analysis."
        )
        welcome_text.setWordWrap(True)
        layout.addWidget(welcome_text)
        
        # Benefits section
        benefits_group = QtWidgets.QGroupBox("🎯 Benefits of Setting Up Your Token:")
        benefits_layout = QtWidgets.QVBoxLayout(benefits_group)
        
        benefits = [
            "🔍 Scan private repositories",
            "📊 Complete portfolio analysis",
            "🔄 Incremental updates",
            "💾 Persistent analysis cache",
            "🚀 Faster scanning with authentication"
        ]
        
        for benefit in benefits:
            label = QtWidgets.QLabel(f"• {benefit}")
            benefits_layout.addWidget(label)
        
        layout.addWidget(benefits_group)
        
        # Security note
        security_note = QtWidgets.QLabel(
            "🔒 Security: Your token will be stored locally and only used for repository scanning. "
            "It will never be shared or uploaded."
        )
        security_note.setStyleSheet("color: #28a745; font-weight: bold;")
        layout.addWidget(security_note)
    
    def isComplete(self):
        """Welcome page is always complete."""
        return True


class TokenGenerationPage(QtWidgets.QWizardPage):
    """Page for generating the GitHub token."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("🌐 Generate GitHub Token")
        self.setSubTitle("Let's create your GitHub Personal Access Token.")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Instructions
        instructions = QtWidgets.QLabel(
            "Follow these steps to create your GitHub token:\n\n"
            "1. Click 'Open GitHub Token Page' below\n"
            "2. Sign in to your GitHub account\n"
            "3. Configure the token settings as shown\n"
            "4. Generate the token\n"
            "5. Copy the token (you'll need it in the next step)"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Open GitHub button
        self.open_github_btn = QtWidgets.QPushButton("🌐 Open GitHub Token Page")
        self.open_github_btn.clicked.connect(self.open_github_token_page)
        layout.addWidget(self.open_github_btn)
        
        # Token settings guide
        settings_group = QtWidgets.QGroupBox("⚙️ Required Token Settings:")
        settings_layout = QtWidgets.QVBoxLayout(settings_group)
        
        settings = [
            "📝 Note: 'Project Scanner Token'",
            "⏰ Expiration: 'No expiration' (or 90 days)",
            "📋 Scopes: Select these permissions:",
            "   • repo (Full control of private repositories)",
            "   • read:user (Read user profile)",
            "   • read:email (Read email addresses)"
        ]
        
        for setting in settings:
            label = QtWidgets.QLabel(setting)
            settings_layout.addWidget(label)
        
        layout.addWidget(settings_group)
        
        # Continue button
        self.continue_btn = QtWidgets.QPushButton("✅ I've Generated My Token")
        self.continue_btn.clicked.connect(self.mark_complete)
        layout.addWidget(self.continue_btn)

    def open_github_token_page(self):
        """Open GitHub token generation page."""
        webbrowser.open("https://github.com/settings/tokens/new")
        self.open_github_btn.setText("🌐 GitHub Token Page Opened")
        self.open_github_btn.setEnabled(False)

    def mark_complete(self):
        """Mark this page as complete."""
        self.setField("token_generated", True)
        self.opened_github = True
        self.completeChanged.emit()
    
    def isComplete(self):
        """Page is complete when user has opened GitHub."""
        return hasattr(self, 'opened_github') and self.opened_github


class TokenSetupPage(QtWidgets.QWizardPage):
    """Page for entering the generated token."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("🔑 Enter Your GitHub Token")
        self.setSubTitle("Paste your generated token below.")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Username field
        layout.addWidget(QtWidgets.QLabel("GitHub Username:"))
        self.username_edit = QtWidgets.QLineEdit()
        self.username_edit.setPlaceholderText("Enter your GitHub username")
        layout.addWidget(self.username_edit)
        
        # Token field
        layout.addWidget(QtWidgets.QLabel("GitHub Personal Access Token:"))
        self.token_edit = QtWidgets.QLineEdit()
        self.token_edit.setPlaceholderText("Paste your token here")
        self.token_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.token_edit)
        
        # Show/hide token button
        self.show_token_btn = QtWidgets.QPushButton("👁️ Show/Hide Token")
        self.show_token_btn.clicked.connect(self.toggle_token_visibility)
        layout.addWidget(self.show_token_btn)
        
        # Token format validation
        self.validation_label = QtWidgets.QLabel("")
        layout.addWidget(self.validation_label)
        
        # Connect validation
        self.token_edit.textChanged.connect(self.validate_token)
        self.username_edit.textChanged.connect(self.validate_token)

    def toggle_token_visibility(self):
        """Toggle token visibility."""
        if self.token_edit.echoMode() == QtWidgets.QLineEdit.Password:
            self.token_edit.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.show_token_btn.setText("🙈 Hide Token")
        else:
            self.token_edit.setEchoMode(QtWidgets.QLineEdit.Password)
            self.show_token_btn.setText("👁️ Show Token")

    def validate_token(self):
        """Validate the token format."""
        token = self.token_edit.text().strip()
        username = self.username_edit.text().strip()
        
        if not username:
            self.validation_label.setText("❌ Please enter your GitHub username")
            self.validation_label.setStyleSheet("color: #dc3545;")
            return False
        
        if not token:
            self.validation_label.setText("❌ Please enter your GitHub token")
            self.validation_label.setStyleSheet("color: #dc3545;")
            return False
        
        if len(token) < 20:
            self.validation_label.setText("❌ Token seems too short. Please check your token.")
            self.validation_label.setStyleSheet("color: #dc3545;")
            return False
        
        if not token.startswith("ghp_"):
            self.validation_label.setText("⚠️ Token format looks unusual. Please verify your token.")
            self.validation_label.setStyleSheet("color: #ffc107;")
            return False
        
        self.validation_label.setText("✅ Token format looks good!")
        self.validation_label.setStyleSheet("color: #28a745;")
        return True

    def isComplete(self):
        """Check if page is complete."""
        return self.validate_token()


class VerificationPage(QtWidgets.QWizardPage):
    """Page for verifying the token works."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("✅ Verify Your Token")
        self.setSubTitle("Let's test your token to make sure it works.")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Status
        self.status_label = QtWidgets.QLabel("Click 'Test Token' to verify your setup.")
        layout.addWidget(self.status_label)
        
        # Test button
        self.test_btn = QtWidgets.QPushButton("🧪 Test Token")
        self.test_btn.clicked.connect(self.test_token)
        layout.addWidget(self.test_btn)
        
        # Results
        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

    def test_token(self):
        """Test the GitHub token."""
        self.test_btn.setEnabled(False)
        self.status_label.setText("Testing token...")
        
        # Get token and username from previous page
        token_page = self.wizard().page(2)  # TokenSetupPage
        token = token_page.token_edit.text().strip()
        username = token_page.username_edit.text().strip()
        
        # Test the token
        self.test_token_worker = TokenTestWorker(token, username)
        self.test_token_worker.result.connect(self.on_test_result)
        self.test_token_worker.start()

    def on_test_result(self, success, message):
        """Handle token test result."""
        self.test_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("✅ Token verification successful!")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            self.results_text.append("✅ Token is working correctly!")
            self.results_text.append(f"📊 Found {message} repositories")
            
            # Store token in wizard
            token_page = self.wizard().page(2)
            self.wizard().github_token = token_page.token_edit.text().strip()
            self.wizard().github_username = token_page.username_edit.text().strip()
            
            # Mark as successful
            self.test_successful = True
            self.completeChanged.emit()
        else:
            self.status_label.setText("❌ Token verification failed!")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.results_text.append("❌ Token verification failed!")
            self.results_text.append(f"Error: {message}")
    
    def isComplete(self):
        """Page is complete when token has been tested successfully."""
        return hasattr(self, 'test_successful') and self.test_successful


class CompletionPage(QtWidgets.QWizardPage):
    """Final completion page."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("🎉 Setup Complete!")
        self.setSubTitle("Your GitHub token has been configured successfully.")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Success message
        success_text = QtWidgets.QLabel(
            "✅ Your GitHub token has been set up successfully!\n\n"
            "You can now:\n"
            "• 🔍 Scan private repositories\n"
            "• 📊 Get comprehensive portfolio analysis\n"
            "• 💾 Save analysis results for reuse\n"
            "• 🔄 Perform incremental updates\n\n"
            "Click 'Finish' to complete the setup."
        )
        success_text.setWordWrap(True)
        layout.addWidget(success_text)
        
        # Next steps
        next_steps_group = QtWidgets.QGroupBox("🚀 Next Steps:")
        next_steps_layout = QtWidgets.QVBoxLayout(next_steps_group)
        
        steps = [
            "1. Return to the main Project Scanner GUI",
            "2. Enter your GitHub username",
            "3. Click 'Scan GitHub Library'",
            "4. Enjoy comprehensive analysis of your portfolio!"
        ]
        
        for step in steps:
            label = QtWidgets.QLabel(step)
            next_steps_layout.addWidget(label)
        
        layout.addWidget(next_steps_group)
    
    def isComplete(self):
        """Completion page is always complete."""
        return True


class TokenTestWorker(QThread):
    """Worker for testing GitHub token."""
    result = pyqtSignal(bool, str)
    
    def __init__(self, token, username):
        super().__init__()
        self.token = token
        self.username = username
    
    def run(self):
        """Test the GitHub token."""
        try:
            import requests
            
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Test public repos
            public_url = f"https://api.github.com/users/{self.username}/repos"
            public_response = requests.get(public_url, headers=headers)
            public_repos = len(public_response.json()) if public_response.status_code == 200 else 0
            
            # Test private repos
            private_url = "https://api.github.com/user/repos"
            private_response = requests.get(private_url, headers=headers)
            private_repos = len(private_response.json()) if private_response.status_code == 200 else 0
            
            total_repos = public_repos + private_repos
            
            if total_repos > 0:
                self.result.emit(True, f"{total_repos} (Public: {public_repos}, Private: {private_repos})")
            else:
                self.result.emit(False, "No repositories found or token doesn't have correct permissions")
                
        except Exception as e:
            self.result.emit(False, str(e))


def main():
    """Run the GitHub token wizard."""
    try:
        app = QtWidgets.QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show wizard
        wizard = GitHubTokenWizard()
        wizard.show()
        
        # Keep the wizard open
        return app.exec_()
        
    except Exception as e:
        print(f"Error launching token wizard: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    main() 