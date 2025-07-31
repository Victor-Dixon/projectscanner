#!/usr/bin/env python3
"""
GitHub Token Setup Wizard GUI - Visual interface for private repository scanning.
"""

import sys
import json
import webbrowser
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
        QTabWidget, QGroupBox, QCheckBox, QSpinBox, QMessageBox,
        QScrollArea, QFrame, QSplitter
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QIcon, QPixmap
except ImportError:
    print("❌ PyQt5 not found. Install with: pip install PyQt5")
    sys.exit(1)


class TokenValidationWorker(QThread):
    """Background worker for token validation."""
    validation_complete = pyqtSignal(bool, str)
    progress_update = pyqtSignal(str)
    
    def __init__(self, username: str, token: str):
        super().__init__()
        self.username = username
        self.token = token
    
    def run(self):
        """Validate the GitHub token."""
        try:
            import requests
            
            self.progress_update.emit("Testing GitHub token...")
            
            headers = {'Authorization': f'token {self.token}'}
            response = requests.get('https://api.github.com/user', headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                self.progress_update.emit(f"✅ Token valid! Authenticated as: {user_data.get('login', 'Unknown')}")
                self.validation_complete.emit(True, user_data.get('login', 'Unknown'))
            else:
                self.progress_update.emit(f"❌ Token validation failed: {response.status_code}")
                self.validation_complete.emit(False, f"HTTP {response.status_code}")
                
        except ImportError:
            self.progress_update.emit("❌ Error: requests library not found")
            self.validation_complete.emit(False, "Missing requests library")
        except Exception as e:
            self.progress_update.emit(f"❌ Error testing token: {str(e)}")
            self.validation_complete.emit(False, str(e))


class EnhancedScannerWorker(QThread):
    """Background worker for enhanced GitHub scanning."""
    progress_update = pyqtSignal(str)
    scan_complete = pyqtSignal(bool, str)
    repo_progress = pyqtSignal(str, int, int)  # repo_name, current, total
    
    def __init__(self, username: str, token: str, output_dir: str):
        super().__init__()
        self.username = username
        self.token = token
        self.output_dir = output_dir
    
    def run(self):
        """Run the enhanced GitHub scanner."""
        try:
            from github_library_scanner_private import EnhancedGitHubLibraryScanner
            
            self.progress_update.emit("🚀 Starting enhanced GitHub scanner...")
            
            scanner = EnhancedGitHubLibraryScanner(self.username, self.token, self.output_dir)
            
            # Override the scan methods to emit progress
            original_scan_repo = scanner.scan_repository
            
            def scan_repo_with_progress(repo_data, force_rescan=False):
                repo_name = repo_data['name']
                self.progress_update.emit(f"🔍 Scanning repository: {repo_name}")
                return original_scan_repo(repo_data, force_rescan)
            
            scanner.scan_repository = scan_repo_with_progress
            
            # Scan all repositories
            scanner.scan_all_repositories()
            
            # Generate summary
            summary = scanner.generate_library_summary()
            
            self.progress_update.emit("✅ Enhanced scan completed successfully!")
            self.scan_complete.emit(True, json.dumps(summary, indent=2))
            
        except ImportError:
            self.progress_update.emit("❌ Error: Could not import enhanced scanner")
            self.scan_complete.emit(False, "Missing enhanced scanner module")
        except Exception as e:
            self.progress_update.emit(f"❌ Error running scanner: {str(e)}")
            self.scan_complete.emit(False, str(e))


class GitHubTokenWizardGUI(QMainWindow):
    """GUI for GitHub token setup wizard."""
    
    def __init__(self):
        super().__init__()
        self.username = ""
        self.token = ""
        self.output_dir = "github_library_enhanced"
        self.validation_worker = None
        self.scanner_worker = None
        
        self.init_ui()
        self.load_existing_config()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🔐 GitHub Token Setup Wizard")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("GitHub Token Setup Wizard")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("This wizard will help you set up access to your private GitHub repositories.")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Setup tab
        self.create_setup_tab()
        
        # Progress tab
        self.create_progress_tab()
        
        # Results tab
        self.create_results_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready to set up GitHub token access")
    
    def create_setup_tab(self):
        """Create the setup configuration tab."""
        setup_widget = QWidget()
        setup_layout = QVBoxLayout(setup_widget)
        
        # Step 1: Username
        username_group = QGroupBox("Step 1: GitHub Username")
        username_layout = QVBoxLayout(username_group)
        
        username_label = QLabel("Enter your GitHub username:")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("e.g., Dadudekc")
        
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        setup_layout.addWidget(username_group)
        
        # Step 2: Token Creation
        token_group = QGroupBox("Step 2: Create GitHub Personal Access Token")
        token_layout = QVBoxLayout(token_group)
        
        token_instructions = QLabel(
            "Click the button below to open GitHub settings and create a token.\n"
            "Follow these steps:\n"
            "1. Click 'Generate new token' → 'Generate new token (classic)'\n"
            "2. Set expiration to 90 days\n"
            "3. Select these scopes:\n"
            "   ✅ repo (Full control of private repositories)\n"
            "   ✅ read:org (Read organization data)\n"
            "   ✅ read:user (Read user data)\n"
            "4. Click 'Generate token'\n"
            "5. Copy the token (you won't see it again!)"
        )
        token_instructions.setWordWrap(True)
        
        open_github_btn = QPushButton("🌐 Open GitHub Settings")
        open_github_btn.clicked.connect(self.open_github_settings)
        
        token_layout.addWidget(token_instructions)
        token_layout.addWidget(open_github_btn)
        setup_layout.addWidget(token_group)
        
        # Step 3: Token Input
        token_input_group = QGroupBox("Step 3: Enter Your GitHub Token")
        token_input_layout = QVBoxLayout(token_input_group)
        
        token_input_label = QLabel("Paste your GitHub Personal Access Token below:")
        self.token_edit = QLineEdit()
        self.token_edit.setEchoMode(QLineEdit.Password)
        self.token_edit.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx")
        
        # Show/hide token button
        show_token_btn = QPushButton("👁️ Show/Hide Token")
        show_token_btn.clicked.connect(self.toggle_token_visibility)
        
        token_input_layout.addWidget(token_input_label)
        token_input_layout.addWidget(self.token_edit)
        token_input_layout.addWidget(show_token_btn)
        setup_layout.addWidget(token_input_group)
        
        # Step 4: Configuration
        config_group = QGroupBox("Step 4: Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Output directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.output_dir_edit = QLineEdit(self.output_dir)
        output_layout.addWidget(self.output_dir_edit)
        config_layout.addLayout(output_layout)
        
        # Options
        self.force_rescan_cb = QCheckBox("Force rescan of existing repositories")
        self.max_repos_spin = QSpinBox()
        self.max_repos_spin.setRange(1, 1000)
        self.max_repos_spin.setValue(100)
        self.max_repos_spin.setSpecialValueText("No limit")
        
        max_repos_layout = QHBoxLayout()
        max_repos_layout.addWidget(QLabel("Max repositories:"))
        max_repos_layout.addWidget(self.max_repos_spin)
        max_repos_layout.addStretch()
        
        config_layout.addWidget(self.force_rescan_cb)
        config_layout.addLayout(max_repos_layout)
        setup_layout.addWidget(config_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.validate_btn = QPushButton("🔍 Validate Token")
        self.validate_btn.clicked.connect(self.validate_token)
        
        self.start_scan_btn = QPushButton("🚀 Start Enhanced Scan")
        self.start_scan_btn.clicked.connect(self.start_enhanced_scan)
        self.start_scan_btn.setEnabled(False)
        
        button_layout.addWidget(self.validate_btn)
        button_layout.addWidget(self.start_scan_btn)
        button_layout.addStretch()
        
        setup_layout.addLayout(button_layout)
        setup_layout.addStretch()
        
        self.tab_widget.addTab(setup_widget, "🔧 Setup")
    
    def create_progress_tab(self):
        """Create the progress monitoring tab."""
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        
        # Progress display
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setFont(QFont("Consolas", 10))
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        progress_layout.addWidget(QLabel("Scan Progress:"))
        progress_layout.addWidget(self.progress_text)
        progress_layout.addWidget(self.progress_bar)
        
        self.tab_widget.addTab(progress_widget, "📊 Progress")
    
    def create_results_tab(self):
        """Create the results display tab."""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.save_config_btn = QPushButton("💾 Save Configuration")
        self.save_config_btn.clicked.connect(self.save_configuration)
        
        self.open_output_btn = QPushButton("📁 Open Output Directory")
        self.open_output_btn.clicked.connect(self.open_output_directory)
        
        button_layout.addWidget(self.save_config_btn)
        button_layout.addWidget(self.open_output_btn)
        button_layout.addStretch()
        
        results_layout.addWidget(QLabel("Scan Results:"))
        results_layout.addWidget(self.results_text)
        results_layout.addLayout(button_layout)
        
        self.tab_widget.addTab(results_widget, "📋 Results")
    
    def open_github_settings(self):
        """Open GitHub settings page in browser."""
        try:
            webbrowser.open("https://github.com/settings/tokens")
            self.log_progress("🌐 Opened GitHub settings page")
        except Exception as e:
            self.log_progress(f"❌ Could not open browser: {e}")
            self.log_progress("Please manually visit: https://github.com/settings/tokens")
    
    def toggle_token_visibility(self):
        """Toggle token visibility."""
        if self.token_edit.echoMode() == QLineEdit.Password:
            self.token_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.token_edit.setEchoMode(QLineEdit.Password)
    
    def validate_token(self):
        """Validate the GitHub token."""
        username = self.username_edit.text().strip()
        token = self.token_edit.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Missing Username", "Please enter your GitHub username.")
            return
        
        if not token:
            QMessageBox.warning(self, "Missing Token", "Please enter your GitHub Personal Access Token.")
            return
        
        self.username = username
        self.token = token
        
        # Switch to progress tab
        self.tab_widget.setCurrentIndex(1)
        self.progress_text.clear()
        self.log_progress("🔍 Validating GitHub token...")
        
        # Start validation worker
        self.validation_worker = TokenValidationWorker(username, token)
        self.validation_worker.progress_update.connect(self.log_progress)
        self.validation_worker.validation_complete.connect(self.on_validation_complete)
        self.validation_worker.start()
    
    def on_validation_complete(self, success: bool, message: str):
        """Handle token validation completion."""
        if success:
            self.log_progress(f"✅ Token validation successful!")
            self.log_progress(f"   Authenticated as: {message}")
            self.start_scan_btn.setEnabled(True)
            QMessageBox.information(self, "Token Valid", "GitHub token is valid! You can now start the enhanced scan.")
        else:
            self.log_progress(f"❌ Token validation failed: {message}")
            QMessageBox.critical(self, "Token Invalid", f"Token validation failed: {message}")
    
    def start_enhanced_scan(self):
        """Start the enhanced GitHub scanner."""
        if not self.username or not self.token:
            QMessageBox.warning(self, "Missing Information", "Please validate your token first.")
            return
        
        # Switch to progress tab
        self.tab_widget.setCurrentIndex(1)
        self.progress_text.clear()
        self.log_progress("🚀 Starting enhanced GitHub scanner...")
        
        # Start scanner worker
        self.scanner_worker = EnhancedScannerWorker(
            self.username, 
            self.token, 
            self.output_dir_edit.text()
        )
        self.scanner_worker.progress_update.connect(self.log_progress)
        self.scanner_worker.scan_complete.connect(self.on_scan_complete)
        self.scanner_worker.start()
    
    def on_scan_complete(self, success: bool, results: str):
        """Handle scan completion."""
        if success:
            self.log_progress("✅ Enhanced scan completed successfully!")
            
            # Switch to results tab
            self.tab_widget.setCurrentIndex(2)
            self.results_text.setText(results)
            
            QMessageBox.information(self, "Scan Complete", "Enhanced GitHub scan completed successfully!")
        else:
            self.log_progress(f"❌ Scan failed: {results}")
            QMessageBox.critical(self, "Scan Failed", f"Enhanced scan failed: {results}")
    
    def log_progress(self, message: str):
        """Log a progress message."""
        self.progress_text.append(f"{message}")
        self.statusBar().showMessage(message)
    
    def save_configuration(self):
        """Save the current configuration."""
        try:
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / "github_token.json"
            
            config = {
                'username': self.username,
                'token': self.token,
                'output_dir': self.output_dir_edit.text(),
                'created_at': str(Path().cwd())
            }
            
            with config_file.open('w') as f:
                json.dump(config, f, indent=2)
            
            # Add to .gitignore
            gitignore_file = Path(".gitignore")
            if gitignore_file.exists():
                with gitignore_file.open('r') as f:
                    content = f.read()
                if "config/github_token.json" not in content:
                    with gitignore_file.open('a') as f:
                        f.write("\n# GitHub token configuration\nconfig/github_token.json\n")
            else:
                with gitignore_file.open('w') as f:
                    f.write("# GitHub token configuration\nconfig/github_token.json\n")
            
            QMessageBox.information(self, "Configuration Saved", 
                                  f"Configuration saved to: {config_file}\n"
                                  "Token file added to .gitignore for security.")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving configuration: {e}")
    
    def open_output_directory(self):
        """Open the output directory."""
        try:
            import subprocess
            import platform
            
            output_dir = Path(self.output_dir_edit.text())
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)
            
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(output_dir)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(output_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(output_dir)])
                
        except Exception as e:
            QMessageBox.warning(self, "Open Error", f"Could not open output directory: {e}")
    
    def load_existing_config(self):
        """Load existing configuration if available."""
        config_file = Path("config/github_token.json")
        if config_file.exists():
            try:
                with config_file.open('r') as f:
                    config = json.load(f)
                
                self.username_edit.setText(config.get('username', ''))
                self.token_edit.setText(config.get('token', ''))
                self.output_dir_edit.setText(config.get('output_dir', self.output_dir))
                
                self.username = config.get('username', '')
                self.token = config.get('token', '')
                
                QMessageBox.information(self, "Configuration Loaded", 
                                      f"Loaded existing configuration for: {self.username}")
                
            except Exception as e:
                self.log_progress(f"⚠️  Could not load existing configuration: {e}")


def main():
    """Main function for the GUI wizard."""
    app = QApplication(sys.argv)
    app.setApplicationName("GitHub Token Setup Wizard")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the wizard
    wizard = GitHubTokenWizardGUI()
    wizard.show()
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 