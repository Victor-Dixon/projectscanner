import json
import sys
import re
import os
import threading
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal

from .scanner import ProjectScanner


class ScanWorker(QThread):
    """Background worker for scanning projects."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, project_path: Path, output_dir: Optional[Path] = None):
        super().__init__()
        self.project_path = project_path
        self.output_dir = output_dir or project_path
        self.scanner = None

    def run(self):
        try:
            self.progress.emit(f"Starting scan of {self.project_path}")
            self.scanner = ProjectScanner(
                project_root=str(self.project_path),
                output_dir=str(self.output_dir)
            )
            
            # Custom progress callback
            def progress_callback(message):
                self.progress.emit(message)
            
            self.scanner.scan_project(progress_callback=progress_callback)
            
            # Generate reports
            self.progress.emit("Generating reports...")
            self.scanner.categorize_agents()
            self.scanner.report_generator.save_report()
            self.scanner.export_chatgpt_context()
            
            # Load the generated reports
            analysis_file = self.scanner.report_generator.analysis_file
            context_file = self.scanner.report_generator.context_file
            
            analysis_path = self.output_dir / analysis_file
            context_path = self.output_dir / context_file
            
            result = {
                'project_path': str(self.project_path),
                'output_dir': str(self.output_dir),
                'analysis_file': str(analysis_path),
                'context_file': str(context_path),
                'analysis_data': {},
                'context_data': {}
            }
            
            if analysis_path.exists():
                with analysis_path.open('r', encoding='utf-8') as f:
                    result['analysis_data'] = json.load(f)
            
            if context_path.exists():
                with context_path.open('r', encoding='utf-8') as f:
                    result['context_data'] = json.load(f)
            
            self.progress.emit("Scan completed successfully!")
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(f"Scan failed: {str(e)}")


class GitHubLibraryWorker(QThread):
    """Background worker for scanning GitHub libraries."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    repo_progress = pyqtSignal(str, int, int)  # repo_name, current, total

    def __init__(self, github_username: str, output_dir: str = "github_library", force_rescan: bool = False, max_repos: Optional[int] = None, github_token: Optional[str] = None):
        super().__init__()
        self.github_username = github_username
        self.output_dir = output_dir
        self.force_rescan = force_rescan
        self.max_repos = max_repos
        self.github_token = github_token
        self.library_data = {}
        self.scan_log = {"scanned_repos": [], "failed_repos": [], "last_scan": None}

    def run(self):
        try:
            self.progress.emit(f"Starting GitHub library scan for user: {self.github_username}")
            
            # Choose scanner based on token availability
            if self.github_token:
                self.progress.emit("Using private repository scanner with token")
                from scanners.github_library_scanner_private import EnhancedGitHubLibraryScanner
                scanner = EnhancedGitHubLibraryScanner(self.github_username, self.github_token, self.output_dir)
            else:
                self.progress.emit("Using public repository scanner")
                from scanners.github_library_scanner import GitHubLibraryScanner
                scanner = GitHubLibraryScanner(self.github_username, self.output_dir)
            
            # Override the scan methods to emit progress
            original_scan_repo = scanner.scan_repository
            
            def scan_repo_with_progress(repo_data, force_rescan=False):
                repo_name = repo_data['name']
                self.progress.emit(f"Scanning repository: {repo_name}")
                return original_scan_repo(repo_data, force_rescan)
            
            scanner.scan_repository = scan_repo_with_progress
            
            # Scan all repositories
            scanner.scan_all_repositories(
                force_rescan=self.force_rescan,
                max_repos=self.max_repos
            )
            
            # Get the results
            self.library_data = scanner.library
            self.scan_log = scanner.scan_log
            
            summary = scanner.generate_library_summary()
            
            result = {
                'username': self.github_username,
                'output_dir': self.output_dir,
                'library_data': self.library_data,
                'scan_log': self.scan_log,
                'summary': summary,
                'token_used': bool(self.github_token)
            }
            
            self.progress.emit("GitHub library scan completed successfully!")
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(f"GitHub library scan failed: {str(e)}")


class ProjectScannerGUI(QtWidgets.QMainWindow):
    """Enhanced GUI for ProjectScanner with clean organization and prominent start processing button."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProjectScanner - Advanced Analysis Tool")
        
        # Get screen size for responsive sizing
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        width = min(1800, screen.width() - 100)
        height = min(1200, screen.height() - 100)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        
        self.setGeometry(x, y, width, height)
        self.setMinimumSize(1200, 800)  # Minimum size for usability
        
        # Initialize data structures
        self.library_data = {}
        self.current_scan_result = None
        self.scan_worker = None
        self.github_library_worker = None
        self.temp_dirs = []
        self.is_processing = False
        
        # Analysis persistence
        self.analysis_cache_dir = Path("analysis_cache")
        self.analysis_cache_dir.mkdir(exist_ok=True)
        self.token_file = Path("config/github_token.txt")
        self.token_file.parent.mkdir(exist_ok=True)
        
        # Load existing library
        self.library_file = Path("project_library.json")
        self.load_library()
        
        self.setup_ui()
        self.setup_menu()
        self.setup_styles()
        
        # Load saved token on startup
        self.load_github_token()

    def setup_styles(self):
        """Setup modern styling for the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #495057;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
            QPushButton#startButton {
                background-color: #28a745;
                font-size: 16px;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton#startButton:hover {
                background-color: #218838;
            }
            QPushButton#startButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton#stopButton {
                background-color: #dc3545;
                font-size: 14px;
                padding: 12px 25px;
            }
            QPushButton#stopButton:hover {
                background-color: #c82333;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
            QTextEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
            QProgressBar {
                border: 2px solid #ced4da;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 4px;
            }
            QTabWidget::pane {
                border: 2px solid #ced4da;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
            QTreeWidget {
                border: 2px solid #ced4da;
                border-radius: 6px;
                background-color: white;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)

    def setup_ui(self):
        """Setup the main UI components."""
        # Create main widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Left panel - Configuration and controls (responsive width)
        left_panel = self.create_configuration_panel()
        left_panel.setMinimumWidth(500)
        left_panel.setMaximumWidth(800)
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Results and progress (takes remaining space)
        right_panel = self.create_results_panel()
        main_layout.addWidget(right_panel, 2)

    def create_configuration_panel(self):
        """Create the left panel with configuration options."""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        
        # Title - More compact
        title = QtWidgets.QLabel("🚀 Project Scanner")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #007bff; margin: 10px;")
        layout.addWidget(title)
        
        # Create scrollable configuration area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        
        # Configuration content widget
        config_widget = QtWidgets.QWidget()
        config_layout = QtWidgets.QVBoxLayout(config_widget)
        
        # Configuration sections
        config_layout.addWidget(self.create_scan_configuration())
        config_layout.addWidget(self.create_github_configuration())
        config_layout.addWidget(self.create_processing_controls())
        
        config_layout.addStretch()
        
        # Add configuration to scroll area
        scroll_area.setWidget(config_widget)
        layout.addWidget(scroll_area)
        
        return panel

    def create_scan_configuration(self):
        """Create scan configuration section."""
        group = QtWidgets.QGroupBox("📁 Project Scanning")
        layout = QtWidgets.QVBoxLayout(group)
        
        # Directory selection
        layout.addWidget(QtWidgets.QLabel("Project Directory:"))
        self.dir_path_edit = QtWidgets.QLineEdit()
        self.dir_path_edit.setPlaceholderText("Select a directory to scan...")
        layout.addWidget(self.dir_path_edit)
        
        dir_btn_layout = QtWidgets.QHBoxLayout()
        self.browse_btn = QtWidgets.QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_directory)
        self.scan_dir_btn = QtWidgets.QPushButton("Scan Directory")
        self.scan_dir_btn.clicked.connect(self.scan_directory)
        dir_btn_layout.addWidget(self.browse_btn)
        dir_btn_layout.addWidget(self.scan_dir_btn)
        layout.addLayout(dir_btn_layout)
        
        # GitHub repository scanning
        layout.addWidget(QtWidgets.QLabel("GitHub Repository URL:"))
        self.github_url_edit = QtWidgets.QLineEdit()
        self.github_url_edit.setPlaceholderText("https://github.com/username/repository")
        layout.addWidget(self.github_url_edit)
        
        self.scan_github_btn = QtWidgets.QPushButton("Scan GitHub Repository")
        self.scan_github_btn.clicked.connect(self.scan_github_repository)
        layout.addWidget(self.scan_github_btn)
        
        return group

    def create_github_configuration(self):
        """Create GitHub library configuration section."""
        group = QtWidgets.QGroupBox("🔗 GitHub Library Scanning")
        layout = QtWidgets.QVBoxLayout(group)
        
        # Create scrollable area for better responsiveness
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(400)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        
        # Main content widget
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        
        # GitHub Token Section - Collapsible
        token_group = QtWidgets.QGroupBox("🔐 GitHub Authentication")
        token_group.setCheckable(True)
        token_group.setChecked(True)
        token_layout = QtWidgets.QVBoxLayout(token_group)
        
        # Token input with better layout
        token_input_layout = QtWidgets.QHBoxLayout()
        token_input_layout.addWidget(QtWidgets.QLabel("Token:"))
        self.github_token_edit = QtWidgets.QLineEdit()
        self.github_token_edit.setPlaceholderText("Enter GitHub token for private repos")
        self.github_token_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        token_input_layout.addWidget(self.github_token_edit)
        token_layout.addLayout(token_input_layout)
        
        # Token management buttons - Compact layout
        token_buttons = QtWidgets.QGridLayout()
        self.save_token_btn = QtWidgets.QPushButton("💾 Save")
        self.save_token_btn.clicked.connect(self.save_github_token)
        self.load_token_btn = QtWidgets.QPushButton("📂 Load")
        self.load_token_btn.clicked.connect(self.load_github_token)
        self.clear_token_btn = QtWidgets.QPushButton("🗑️ Clear")
        self.clear_token_btn.clicked.connect(self.clear_github_token)
        
        token_buttons.addWidget(self.save_token_btn, 0, 0)
        token_buttons.addWidget(self.load_token_btn, 0, 1)
        token_buttons.addWidget(self.clear_token_btn, 0, 2)
        token_layout.addLayout(token_buttons)
        
        # Wizard button - Full width
        self.token_wizard_btn = QtWidgets.QPushButton("🔐 GitHub Token Wizard")
        self.token_wizard_btn.setStyleSheet("background-color: #28a745; font-weight: bold; padding: 8px;")
        self.token_wizard_btn.clicked.connect(self.launch_token_wizard)
        token_layout.addWidget(self.token_wizard_btn)
        
        content_layout.addWidget(token_group)
        
        # Username and Options - Compact layout
        basic_group = QtWidgets.QGroupBox("📋 Basic Settings")
        basic_layout = QtWidgets.QGridLayout(basic_group)
        
        basic_layout.addWidget(QtWidgets.QLabel("Username:"), 0, 0)
        self.github_username_edit = QtWidgets.QLineEdit()
        self.github_username_edit.setPlaceholderText("Enter GitHub username")
        basic_layout.addWidget(self.github_username_edit, 0, 1)
        
        basic_layout.addWidget(QtWidgets.QLabel("Max Repos:"), 1, 0)
        self.max_repos_spin = QtWidgets.QSpinBox()
        self.max_repos_spin.setRange(1, 1000)
        self.max_repos_spin.setValue(50)
        self.max_repos_spin.setSpecialValueText("No Limit")
        basic_layout.addWidget(self.max_repos_spin, 1, 1)
        
        self.force_rescan_cb = QtWidgets.QCheckBox("Force Rescan")
        basic_layout.addWidget(self.force_rescan_cb, 1, 2)
        
        content_layout.addWidget(basic_group)
        
        # Analysis persistence options - Collapsible
        persistence_group = QtWidgets.QGroupBox("💾 Analysis Persistence")
        persistence_group.setCheckable(True)
        persistence_group.setChecked(True)
        persistence_layout = QtWidgets.QVBoxLayout(persistence_group)
        
        self.save_analysis_cb = QtWidgets.QCheckBox("Save analysis results for reuse")
        self.save_analysis_cb.setChecked(True)
        persistence_layout.addWidget(self.save_analysis_cb)
        
        self.update_existing_cb = QtWidgets.QCheckBox("Update existing analysis (incremental)")
        self.update_existing_cb.setChecked(True)
        persistence_layout.addWidget(self.update_existing_cb)
        
        content_layout.addWidget(persistence_group)
        
        # Main scan button
        self.scan_github_library_btn = QtWidgets.QPushButton("🔍 Scan GitHub Library")
        self.scan_github_library_btn.setStyleSheet("background-color: #007bff; font-weight: bold; padding: 10px;")
        self.scan_github_library_btn.clicked.connect(self.scan_github_library)
        content_layout.addWidget(self.scan_github_library_btn)
        
        # Add content to scroll area
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        return group

    def create_processing_controls(self):
        """Create the processing controls section with prominent start button."""
        group = QtWidgets.QGroupBox("⚡ Processing Controls")
        layout = QtWidgets.QVBoxLayout(group)
        
        # Status display
        self.status_label = QtWidgets.QLabel("Ready to process")
        self.status_label.setStyleSheet("font-weight: bold; color: #28a745; padding: 15px; font-size: 14px;")
        layout.addWidget(self.status_label)
        
        # Prominent Start Processing Button
        self.start_processing_btn = QtWidgets.QPushButton("🚀 START PROCESSING")
        self.start_processing_btn.setObjectName("startButton")
        self.start_processing_btn.clicked.connect(self.start_processing)
        self.start_processing_btn.setMinimumHeight(60)
        layout.addWidget(self.start_processing_btn)
        
        # Stop Processing Button
        self.stop_processing_btn = QtWidgets.QPushButton("⏹️ STOP PROCESSING")
        self.stop_processing_btn.setObjectName("stopButton")
        self.stop_processing_btn.clicked.connect(self.stop_processing)
        self.stop_processing_btn.setEnabled(False)
        self.stop_processing_btn.setMinimumHeight(50)
        layout.addWidget(self.stop_processing_btn)
        
        # Progress section
        layout.addWidget(QtWidgets.QLabel("Progress:"))
        self.progress_text = QtWidgets.QTextEdit()
        self.progress_text.setMaximumHeight(200)
        self.progress_text.setReadOnly(True)
        layout.addWidget(self.progress_text)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return group

    def create_results_panel(self):
        """Create the right panel with results and library."""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        
        # Title
        title = QtWidgets.QLabel("📊 Results & Analysis")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #007bff; margin: 15px;")
        layout.addWidget(title)
        
        # Tab widget for different views
        self.tabs = QtWidgets.QTabWidget()
        
        # Current scan results tab
        self.current_scan_tab = QtWidgets.QWidget()
        current_scan_layout = QtWidgets.QVBoxLayout(self.current_scan_tab)
        
        self.current_scan_tree = QtWidgets.QTreeWidget()
        self.current_scan_tree.setHeaderHidden(True)
        current_scan_layout.addWidget(self.current_scan_tree)
        
        self.tabs.addTab(self.current_scan_tab, "📊 Current Scan")
        
        # Library tab
        self.library_tab = QtWidgets.QWidget()
        library_layout = QtWidgets.QVBoxLayout(self.library_tab)
        
        # Library controls
        library_controls = QtWidgets.QHBoxLayout()
        self.library_tree = QtWidgets.QTreeWidget()
        self.library_tree.setHeaderLabels(["Project", "Files", "Classes", "Functions"])
        self.library_tree.itemClicked.connect(self.on_library_item_clicked)
        library_layout.addWidget(self.library_tree)
        
        library_btn_layout = QtWidgets.QVBoxLayout()
        self.view_library_item_btn = QtWidgets.QPushButton("View Selected")
        self.view_library_item_btn.clicked.connect(self.view_library_item)
        self.delete_library_item_btn = QtWidgets.QPushButton("Delete Selected")
        self.delete_library_item_btn.clicked.connect(self.delete_library_item)
        library_btn_layout.addWidget(self.view_library_item_btn)
        library_btn_layout.addWidget(self.delete_library_item_btn)
        library_btn_layout.addStretch()
        library_layout.addLayout(library_btn_layout)
        
        self.tabs.addTab(self.library_tab, "📚 Project Library")
        
        # GitHub Library tab
        self.github_library_tab = QtWidgets.QWidget()
        github_library_layout = QtWidgets.QVBoxLayout(self.github_library_tab)
        
        self.github_library_tree = QtWidgets.QTreeWidget()
        self.github_library_tree.setHeaderLabels(["Repository", "Language", "Files", "Stars"])
        self.github_library_tree.itemClicked.connect(self.on_github_library_item_clicked)
        github_library_layout.addWidget(self.github_library_tree)
        
        github_library_btn_layout = QtWidgets.QVBoxLayout()
        self.view_github_repo_btn = QtWidgets.QPushButton("View Repository")
        self.view_github_repo_btn.clicked.connect(self.view_github_repository)
        self.refresh_github_library_btn = QtWidgets.QPushButton("Refresh Library")
        self.refresh_github_library_btn.clicked.connect(self.refresh_github_library)
        github_library_btn_layout.addWidget(self.view_github_repo_btn)
        github_library_btn_layout.addWidget(self.refresh_github_library_btn)
        github_library_btn_layout.addStretch()
        github_library_layout.addLayout(github_library_btn_layout)
        
        self.tabs.addTab(self.github_library_tab, "🔗 GitHub Library")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        return panel

    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QtWidgets.QAction('Open Directory', self)
        open_action.triggered.connect(self.browse_directory)
        file_menu.addAction(open_action)
        
        save_action = QtWidgets.QAction('Save Current Scan', self)
        save_action.triggered.connect(self.save_current_scan)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Library menu
        library_menu = menubar.addMenu('Library')
        
        export_action = QtWidgets.QAction('Export Library', self)
        export_action.triggered.connect(self.export_library)
        library_menu.addAction(export_action)
        
        import_action = QtWidgets.QAction('Import Library', self)
        import_action.triggered.connect(self.import_library)
        library_menu.addAction(import_action)
        
        # GitHub menu
        github_menu = menubar.addMenu('GitHub')
        
        scan_library_action = QtWidgets.QAction('Scan GitHub Library', self)
        scan_library_action.triggered.connect(self.scan_github_library)
        github_menu.addAction(scan_library_action)

    def start_processing(self):
        """Start the processing workflow."""
        if self.is_processing:
            QtWidgets.QMessageBox.warning(self, "Warning", "Processing is already in progress.")
            return
        
        # Check if we have a valid configuration
        directory = self.dir_path_edit.text().strip()
        github_url = self.github_url_edit.text().strip()
        github_username = self.github_username_edit.text().strip()
        
        if not directory and not github_url and not github_username:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please configure at least one scanning option.")
            return
        
        # Start processing based on configuration
        self.is_processing = True
        self.update_processing_controls()
        
        if directory:
            self.process_directory(directory)
        elif github_url:
            self.process_github_repository(github_url)
        elif github_username:
            self.process_github_library(github_username)

    def stop_processing(self):
        """Stop the current processing."""
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.terminate()
            self.scan_worker.wait()
        
        if self.github_library_worker and self.github_library_worker.isRunning():
            self.github_library_worker.terminate()
            self.github_library_worker.wait()
        
        self.is_processing = False
        self.update_processing_controls()
        self.status_label.setText("Processing stopped")
        self.status_bar.showMessage("Processing stopped")

    def update_processing_controls(self):
        """Update the processing control buttons."""
        if self.is_processing:
            self.start_processing_btn.setEnabled(False)
            self.stop_processing_btn.setEnabled(True)
            self.status_label.setText("Processing in progress...")
            self.status_label.setStyleSheet("font-weight: bold; color: #dc3545; padding: 15px; font-size: 14px;")
        else:
            self.start_processing_btn.setEnabled(True)
            self.stop_processing_btn.setEnabled(False)
            self.status_label.setText("Ready to process")
            self.status_label.setStyleSheet("font-weight: bold; color: #28a745; padding: 15px; font-size: 14px;")

    def process_directory(self, directory):
        """Process a local directory."""
        project_path = Path(directory)
        if not project_path.exists():
            QtWidgets.QMessageBox.error(self, "Error", "Selected directory does not exist.")
            self.is_processing = False
            self.update_processing_controls()
            return
        
        self.start_scan(project_path)

    def process_github_repository(self, repo_url):
        """Process a GitHub repository."""
        if not repo_url.startswith(('http://', 'https://')):
            repo_url = f"https://github.com/{repo_url}"
        
        try:
            # Create temporary directory for cloning
            temp_dir = Path(tempfile.mkdtemp())
            self.temp_dirs.append(temp_dir)
            
            self.progress_text.append(f"Cloning repository: {repo_url}")
            clone_path = self.clone_repository(repo_url, temp_dir)
            
            self.progress_text.append(f"Repository cloned to: {clone_path}")
            self.start_scan(clone_path)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to clone repository: {str(e)}")
            self.is_processing = False
            self.update_processing_controls()

    def process_github_library(self, username, force_rescan=False, max_repos=None):
        """Process a GitHub library."""
        # Clear progress
        self.progress_text.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Get GitHub token
        token = self.github_token_edit.text().strip()
        
        # Create and start GitHub library worker
        self.github_library_worker = GitHubLibraryWorker(
            username, 
            "github_library", 
            force_rescan, 
            max_repos,
            token
        )
        self.github_library_worker.progress.connect(self.update_progress)
        self.github_library_worker.finished.connect(self.github_library_finished)
        self.github_library_worker.error.connect(self.scan_error)
        self.github_library_worker.start()

    def display_cached_analysis(self, username: str, cached_results: Dict):
        """Display cached analysis results."""
        self.update_progress(f"Loading cached analysis for {username}...")
        
        # Display the cached results
        self.display_github_library_results(cached_results)
        
        # Switch to GitHub library tab
        self.tabs.setCurrentIndex(2)
        
        self.status_bar.showMessage(f"Cached analysis loaded for {username}")
        QtWidgets.QMessageBox.information(
            self, "Cached Analysis Loaded",
            f"Successfully loaded cached analysis for {username} with {len(cached_results.get('repositories', []))} repositories."
        )

    def clone_repository(self, repo_url: str, temp_dir: Path) -> Path:
        """Clone a GitHub repository to a temporary directory."""
        try:
            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            
            clone_path = temp_dir / repo_name
            
            # Clone the repository
            subprocess.run([
                'git', 'clone', repo_url, str(clone_path)
            ], check=True, capture_output=True)
            
            return clone_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to clone repository: {e.stderr.decode()}")
        except Exception as e:
            raise Exception(f"Error cloning repository: {str(e)}")

    def browse_directory(self):
        """Open directory browser dialog."""
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Project Directory", ""
        )
        if directory:
            self.dir_path_edit.setText(directory)

    def scan_directory(self):
        """Scan the selected directory."""
        directory = self.dir_path_edit.text().strip()
        if not directory:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a directory to scan.")
            return
        
        self.process_directory(directory)

    def scan_github_repository(self):
        """Scan a GitHub repository."""
        repo_url = self.github_url_edit.text().strip()
        if not repo_url:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a GitHub repository URL.")
            return
        
        self.process_github_repository(repo_url)

    def scan_github_library(self):
        """Scan all repositories from a GitHub user."""
        username = self.github_username_edit.text().strip()
        if not username:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a GitHub username.")
            return
        
        # Get options
        force_rescan = self.force_rescan_cb.isChecked()
        max_repos = self.max_repos_spin.value() if self.max_repos_spin.value() > 0 else None
        
        # Check for cached analysis
        cached_results = self.load_analysis_results(username)
        if cached_results and not force_rescan:
            reply = QtWidgets.QMessageBox.question(
                self, "Cached Analysis Found",
                f"Found cached analysis for {username}. Use cached results or perform new scan?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                self.display_cached_analysis(username, cached_results)
                return
        
        self.process_github_library(username, force_rescan, max_repos)

    def start_scan(self, project_path: Path):
        """Start scanning a project."""
        if self.scan_worker and self.scan_worker.isRunning():
            QtWidgets.QMessageBox.warning(self, "Warning", "A scan is already in progress.")
            return
        
        # Clear progress
        self.progress_text.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Create and start scan worker
        self.scan_worker = ScanWorker(project_path)
        self.scan_worker.progress.connect(self.update_progress)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.error.connect(self.scan_error)
        self.scan_worker.start()

    def update_progress(self, message: str):
        """Update progress display."""
        self.progress_text.append(message)
        self.status_bar.showMessage(message)

    def scan_finished(self, result: Dict):
        """Handle scan completion."""
        self.current_scan_result = result
        
        # Re-enable processing
        self.is_processing = False
        self.update_processing_controls()
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Display results
        self.display_scan_results(result)
        
        # Switch to current scan tab
        self.tabs.setCurrentIndex(0)
        
        self.status_bar.showMessage("Scan completed successfully!")

    def github_library_finished(self, result: Dict):
        """Handle GitHub library scan completion."""
        # Re-enable processing
        self.is_processing = False
        self.update_processing_controls()
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Save analysis results if enabled
        username = self.github_username_edit.text().strip()
        if username:
            self.save_analysis_results(username, result)
        
        # Display GitHub library results
        self.display_github_library_results(result)
        
        # Switch to GitHub library tab
        self.tabs.setCurrentIndex(2)
        
        self.status_bar.showMessage("GitHub library scan completed successfully!")

    def scan_error(self, error_message: str):
        """Handle scan errors."""
        QtWidgets.QMessageBox.critical(self, "Scan Error", error_message)
        
        # Re-enable processing
        self.is_processing = False
        self.update_processing_controls()
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        self.status_bar.showMessage("Scan failed!")

    def display_scan_results(self, result: Dict):
        """Display scan results in the tree widget."""
        self.current_scan_tree.clear()
        
        # Create root item
        root = QtWidgets.QTreeWidgetItem([f"Project: {Path(result['project_path']).name}"])
        self.current_scan_tree.addTopLevelItem(root)
        
        # Add analysis data
        if result['analysis_data']:
            analysis_item = QtWidgets.QTreeWidgetItem(["Analysis Data"])
            root.addChild(analysis_item)
            self.populate_tree_item(analysis_item, result['analysis_data'])
        
        # Add context data
        if result['context_data']:
            context_item = QtWidgets.QTreeWidgetItem(["ChatGPT Context"])
            root.addChild(context_item)
            self.populate_tree_item(context_item, result['context_data'])
        
        root.setExpanded(True)

    def display_github_library_results(self, result: Dict):
        """Display GitHub library results."""
        self.github_library_tree.clear()
        
        library_data = result.get('library_data', {})
        
        for repo_id, repo_info in library_data.items():
            item = QtWidgets.QTreeWidgetItem([
                repo_info.get('repo_name', repo_id),
                repo_info.get('language', 'Unknown'),
                str(repo_info.get('file_count', 0)),
                str(repo_info.get('stars', 0))
            ])
            item.setData(0, QtCore.Qt.UserRole, repo_info)
            self.github_library_tree.addTopLevelItem(item)

    def populate_tree_item(self, parent: QtWidgets.QTreeWidgetItem, data):
        """Recursively populate tree widget items."""
        if isinstance(data, dict):
            for key, value in data.items():
                item = QtWidgets.QTreeWidgetItem([str(key)])
                parent.addChild(item)
                self.populate_tree_item(item, value)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                item = QtWidgets.QTreeWidgetItem([f"[{i}]"])
                parent.addChild(item)
                self.populate_tree_item(item, value)
        else:
            item = QtWidgets.QTreeWidgetItem([str(data)])
            parent.addChild(item)

    def load_library(self):
        """Load the project library from file."""
        if self.library_file.exists():
            try:
                with self.library_file.open('r', encoding='utf-8') as f:
                    self.library_data = json.load(f)
            except Exception as e:
                print(f"Error loading library: {e}")
                self.library_data = {}

    def save_library(self):
        """Save the project library to file."""
        try:
            with self.library_file.open('w', encoding='utf-8') as f:
                json.dump(self.library_data, f, indent=4)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save library: {str(e)}")

    def update_library_display(self):
        """Update the library tree display."""
        self.library_tree.clear()
        
        for project_name, data in self.library_data.items():
            analysis_data = data.get('analysis_data', {})
            
            # Count files, classes, and functions
            file_count = len(analysis_data)
            class_count = sum(1 for file_data in analysis_data.values() 
                            if 'classes' in file_data and file_data['classes'])
            function_count = sum(1 for file_data in analysis_data.values() 
                               if 'functions' in file_data and file_data['functions'])
            
            item = QtWidgets.QTreeWidgetItem([
                project_name,
                str(file_count),
                str(class_count),
                str(function_count)
            ])
            self.library_tree.addTopLevelItem(item)

    def on_library_item_clicked(self, item: QtWidgets.QTreeWidgetItem, column: int):
        """Handle library item selection."""
        project_name = item.text(0)
        if project_name in self.library_data:
            self.current_scan_result = self.library_data[project_name]
            self.display_scan_results(self.current_scan_result)
            self.tabs.setCurrentIndex(0)

    def on_github_library_item_clicked(self, item: QtWidgets.QTreeWidgetItem, column: int):
        """Handle GitHub library item selection."""
        repo_info = item.data(0, QtCore.Qt.UserRole)
        if repo_info:
            # Display repository information
            QtWidgets.QMessageBox.information(
                self, 
                f"Repository: {repo_info.get('repo_name', 'Unknown')}",
                f"URL: {repo_info.get('repo_url', 'Unknown')}\n"
                f"Language: {repo_info.get('language', 'Unknown')}\n"
                f"Stars: {repo_info.get('stars', 0)}\n"
                f"Files: {repo_info.get('file_count', 0)}\n"
                f"Description: {repo_info.get('description', 'No description')}"
            )

    def view_library_item(self):
        """View the selected library item."""
        current_item = self.library_tree.currentItem()
        if current_item:
            self.on_library_item_clicked(current_item, 0)

    def view_github_repository(self):
        """View the selected GitHub repository."""
        current_item = self.github_library_tree.currentItem()
        if current_item:
            self.on_github_library_item_clicked(current_item, 0)

    def refresh_github_library(self):
        """Refresh the GitHub library display."""
        # This would reload the GitHub library data
        pass

    def delete_library_item(self):
        """Delete the selected library item."""
        current_item = self.library_tree.currentItem()
        if not current_item:
            return
        
        project_name = current_item.text(0)
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete '{project_name}' from the library?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            if project_name in self.library_data:
                del self.library_data[project_name]
                self.save_library()
                self.update_library_display()

    def export_library(self):
        """Export the library to a file."""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Library", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.library_data, f, indent=4)
                QtWidgets.QMessageBox.information(self, "Success", "Library exported successfully!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to export library: {str(e)}")

    def import_library(self):
        """Import a library from a file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import Library", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_data = json.load(f)
                
                # Merge with existing library
                self.library_data.update(imported_data)
                self.save_library()
                self.update_library_display()
                
                QtWidgets.QMessageBox.information(self, "Success", "Library imported successfully!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to import library: {str(e)}")

    def save_current_scan(self):
        """Save current scan to a file."""
        if not self.current_scan_result:
            QtWidgets.QMessageBox.warning(self, "Warning", "No scan result to save.")
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Scan Result", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_scan_result, f, indent=4)
                QtWidgets.QMessageBox.information(self, "Success", "Scan result saved successfully!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save scan result: {str(e)}")

    # GitHub Token Management Methods
    def save_github_token(self):
        """Save GitHub token to secure file."""
        token = self.github_token_edit.text().strip()
        if not token:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a GitHub token first.")
            return
        
        try:
            with open(self.token_file, 'w', encoding='utf-8') as f:
                f.write(token)
            QtWidgets.QMessageBox.information(self, "Success", "GitHub token saved successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save token: {str(e)}")

    def load_github_token(self):
        """Load GitHub token from secure file."""
        try:
            if self.token_file.exists():
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
                    self.github_token_edit.setText(token)
        except Exception as e:
            print(f"Warning: Could not load GitHub token: {e}")

    def clear_github_token(self):
        """Clear GitHub token from UI and file."""
        self.github_token_edit.clear()
        try:
            if self.token_file.exists():
                self.token_file.unlink()
            QtWidgets.QMessageBox.information(self, "Success", "GitHub token cleared successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to clear token: {str(e)}")

    # Analysis Persistence Methods
    def get_analysis_cache_path(self, username: str) -> Path:
        """Get cache path for analysis results."""
        return self.analysis_cache_dir / f"{username}_analysis.json"

    def save_analysis_results(self, username: str, results: Dict):
        """Save analysis results to cache."""
        if not self.save_analysis_cb.isChecked():
            return
        
        try:
            cache_file = self.get_analysis_cache_path(username)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            self.update_progress(f"Analysis results saved to cache: {cache_file}")
        except Exception as e:
            self.update_progress(f"Warning: Could not save analysis results: {e}")

    def load_analysis_results(self, username: str) -> Optional[Dict]:
        """Load analysis results from cache."""
        try:
            cache_file = self.get_analysis_cache_path(username)
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.update_progress(f"Warning: Could not load cached analysis: {e}")
        return None

    def update_analysis_results(self, username: str, new_results: Dict):
        """Update existing analysis results incrementally."""
        if not self.update_existing_cb.isChecked():
            return
        
        try:
            existing_results = self.load_analysis_results(username) or {}
            
            # Merge new results with existing
            for key, value in new_results.items():
                if key in existing_results and isinstance(existing_results[key], dict) and isinstance(value, dict):
                    existing_results[key].update(value)
                else:
                    existing_results[key] = value
            
            self.save_analysis_results(username, existing_results)
            self.update_progress(f"Analysis results updated for {username}")
        except Exception as e:
            self.update_progress(f"Warning: Could not update analysis results: {e}")

    def launch_token_wizard(self):
        """Launch the GitHub token wizard as a popup dialog."""
        try:
            from wizards.github_token_wizard import GitHubTokenWizard
            
            # Create wizard as a dialog with main window as parent
            wizard = GitHubTokenWizard(self)
            wizard.finished.connect(self.on_wizard_finished)
            
            # Show as modal dialog (popup within the main application)
            wizard.exec_()
            
        except ImportError as e:
            QtWidgets.QMessageBox.critical(
                self, "Error",
                f"Could not launch token wizard: {str(e)}\n\n"
                "Make sure the wizard module is available."
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error",
                f"Error launching token wizard: {str(e)}"
            )

    def on_wizard_finished(self, result):
        """Handle wizard completion."""
        if result == QtWidgets.QWizard.Accepted:
            # Load the token that was saved by the wizard
            self.load_github_token()
            
            # Also load from the new config format
            config_file = Path("config/github_config.json")
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # Set the username and token
                    if 'username' in config:
                        self.github_username_edit.setText(config['username'])
                    if 'token' in config:
                        self.github_token_edit.setText(config['token'])
                    
                    QtWidgets.QMessageBox.information(
                        self, "Setup Complete",
                        "✅ GitHub token wizard completed successfully!\n\n"
                        "Your token and username have been loaded into the GUI.\n"
                        "You can now scan your private repositories."
                    )
                except Exception as e:
                    QtWidgets.QMessageBox.warning(
                        self, "Warning",
                        f"Token wizard completed but could not load configuration: {str(e)}"
                    )

    def closeEvent(self, event):
        """Handle application close event."""
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
        
        # Stop any running scan
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.terminate()
            self.scan_worker.wait()
        
        if self.github_library_worker and self.github_library_worker.isRunning():
            self.github_library_worker.terminate()
            self.github_library_worker.wait()
        
        event.accept()


def main():
    """Main function to run the GUI."""
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = ProjectScannerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
