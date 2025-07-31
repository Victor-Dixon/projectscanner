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

    def __init__(self, github_username: str, output_dir: str = "github_library", force_rescan: bool = False, max_repos: Optional[int] = None):
        super().__init__()
        self.github_username = github_username
        self.output_dir = output_dir
        self.force_rescan = force_rescan
        self.max_repos = max_repos
        self.library_data = {}
        self.scan_log = {"scanned_repos": [], "failed_repos": [], "last_scan": None}

    def run(self):
        try:
            self.progress.emit(f"Starting GitHub library scan for user: {self.github_username}")
            
            # Import the GitHub library scanner
            from github_library_scanner import GitHubLibraryScanner
            
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
                'summary': summary
            }
            
            self.progress.emit("GitHub library scan completed successfully!")
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(f"GitHub library scan failed: {str(e)}")


class GitHubScanner:
    """Handles GitHub repository cloning and scanning."""
    
    @staticmethod
    def clone_repository(repo_url: str, temp_dir: Path) -> Path:
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


class ProjectScannerGUI(QtWidgets.QMainWindow):
    """Enhanced GUI for ProjectScanner with directory, GitHub, and library scanning capabilities."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProjectScanner - Advanced GUI")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize data structures
        self.library_data = {}
        self.current_scan_result = None
        self.scan_worker = None
        self.github_library_worker = None
        self.temp_dirs = []
        
        # Load existing library
        self.library_file = Path("project_library.json")
        self.load_library()
        
        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        """Setup the main UI components."""
        # Create main widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Left panel - Scanning controls
        left_panel = self.create_scanning_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Results and library
        right_panel = self.create_results_panel()
        main_layout.addWidget(right_panel, 2)

    def create_scanning_panel(self):
        """Create the left panel with scanning controls."""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        
        # Title
        title = QtWidgets.QLabel("Project Scanner")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Directory scanning section
        dir_group = QtWidgets.QGroupBox("Directory Scanning")
        dir_layout = QtWidgets.QVBoxLayout(dir_group)
        
        # Directory selection
        dir_layout.addWidget(QtWidgets.QLabel("Project Directory:"))
        self.dir_path_edit = QtWidgets.QLineEdit()
        self.dir_path_edit.setPlaceholderText("Select a directory to scan...")
        dir_layout.addWidget(self.dir_path_edit)
        
        dir_btn_layout = QtWidgets.QHBoxLayout()
        self.browse_btn = QtWidgets.QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_directory)
        self.scan_dir_btn = QtWidgets.QPushButton("Scan Directory")
        self.scan_dir_btn.clicked.connect(self.scan_directory)
        dir_btn_layout.addWidget(self.browse_btn)
        dir_btn_layout.addWidget(self.scan_dir_btn)
        dir_layout.addLayout(dir_btn_layout)
        
        layout.addWidget(dir_group)
        
        # GitHub repository scanning section
        github_group = QtWidgets.QGroupBox("GitHub Repository Scanning")
        github_layout = QtWidgets.QVBoxLayout(github_group)
        
        github_layout.addWidget(QtWidgets.QLabel("GitHub Repository URL:"))
        self.github_url_edit = QtWidgets.QLineEdit()
        self.github_url_edit.setPlaceholderText("https://github.com/username/repository")
        github_layout.addWidget(self.github_url_edit)
        
        self.scan_github_btn = QtWidgets.QPushButton("Scan GitHub Repository")
        self.scan_github_btn.clicked.connect(self.scan_github_repository)
        github_layout.addWidget(self.scan_github_btn)
        
        layout.addWidget(github_group)
        
        # GitHub Library scanning section
        github_library_group = QtWidgets.QGroupBox("GitHub Library Scanning")
        github_library_layout = QtWidgets.QVBoxLayout(github_library_group)
        
        github_library_layout.addWidget(QtWidgets.QLabel("GitHub Username:"))
        self.github_username_edit = QtWidgets.QLineEdit()
        self.github_username_edit.setPlaceholderText("Enter GitHub username")
        github_library_layout.addWidget(self.github_username_edit)
        
        # Options for library scanning
        options_layout = QtWidgets.QHBoxLayout()
        self.force_rescan_cb = QtWidgets.QCheckBox("Force Rescan")
        self.max_repos_spin = QtWidgets.QSpinBox()
        self.max_repos_spin.setRange(1, 1000)
        self.max_repos_spin.setValue(50)
        self.max_repos_spin.setSpecialValueText("No Limit")
        options_layout.addWidget(QtWidgets.QLabel("Max Repos:"))
        options_layout.addWidget(self.max_repos_spin)
        options_layout.addWidget(self.force_rescan_cb)
        github_library_layout.addLayout(options_layout)
        
        self.scan_github_library_btn = QtWidgets.QPushButton("Scan GitHub Library")
        self.scan_github_library_btn.clicked.connect(self.scan_github_library)
        github_library_layout.addWidget(self.scan_github_library_btn)
        
        layout.addWidget(github_library_group)
        
        # Progress section
        progress_group = QtWidgets.QGroupBox("Scan Progress")
        progress_layout = QtWidgets.QVBoxLayout(progress_group)
        
        self.progress_text = QtWidgets.QTextEdit()
        self.progress_text.setMaximumHeight(150)
        self.progress_text.setReadOnly(True)
        progress_layout.addWidget(self.progress_text)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_group)
        
        # Library management section
        library_group = QtWidgets.QGroupBox("Library Management")
        library_layout = QtWidgets.QVBoxLayout(library_group)
        
        self.save_to_library_btn = QtWidgets.QPushButton("Save Current Scan to Library")
        self.save_to_library_btn.clicked.connect(self.save_to_library)
        self.save_to_library_btn.setEnabled(False)
        library_layout.addWidget(self.save_to_library_btn)
        
        self.export_library_btn = QtWidgets.QPushButton("Export Library")
        self.export_library_btn.clicked.connect(self.export_library)
        library_layout.addWidget(self.export_library_btn)
        
        layout.addWidget(library_group)
        
        layout.addStretch()
        return panel

    def create_results_panel(self):
        """Create the right panel with results and library."""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        
        # Tab widget for different views
        self.tabs = QtWidgets.QTabWidget()
        
        # Current scan results tab
        self.current_scan_tab = QtWidgets.QWidget()
        current_scan_layout = QtWidgets.QVBoxLayout(self.current_scan_tab)
        
        self.current_scan_tree = QtWidgets.QTreeWidget()
        self.current_scan_tree.setHeaderHidden(True)
        current_scan_layout.addWidget(self.current_scan_tree)
        
        self.tabs.addTab(self.current_scan_tab, "Current Scan")
        
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
        
        self.tabs.addTab(self.library_tab, "Project Library")
        
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
        
        self.tabs.addTab(self.github_library_tab, "GitHub Library")
        
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
        
        project_path = Path(directory)
        if not project_path.exists():
            QtWidgets.QMessageBox.error(self, "Error", "Selected directory does not exist.")
            return
        
        self.start_scan(project_path)

    def scan_github_repository(self):
        """Scan a GitHub repository."""
        repo_url = self.github_url_edit.text().strip()
        if not repo_url:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a GitHub repository URL.")
            return
        
        if not repo_url.startswith(('http://', 'https://')):
            repo_url = f"https://github.com/{repo_url}"
        
        try:
            # Create temporary directory for cloning
            temp_dir = Path(tempfile.mkdtemp())
            self.temp_dirs.append(temp_dir)
            
            self.progress_text.append(f"Cloning repository: {repo_url}")
            clone_path = GitHubScanner.clone_repository(repo_url, temp_dir)
            
            self.progress_text.append(f"Repository cloned to: {clone_path}")
            self.start_scan(clone_path)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to clone repository: {str(e)}")

    def scan_github_library(self):
        """Scan all repositories from a GitHub user."""
        username = self.github_username_edit.text().strip()
        if not username:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a GitHub username.")
            return
        
        # Get options
        force_rescan = self.force_rescan_cb.isChecked()
        max_repos = self.max_repos_spin.value() if self.max_repos_spin.value() > 0 else None
        
        # Disable scan buttons
        self.scan_dir_btn.setEnabled(False)
        self.scan_github_btn.setEnabled(False)
        self.scan_github_library_btn.setEnabled(False)
        self.save_to_library_btn.setEnabled(False)
        
        # Clear progress
        self.progress_text.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Create and start GitHub library worker
        self.github_library_worker = GitHubLibraryWorker(
            username, 
            "github_library", 
            force_rescan, 
            max_repos
        )
        self.github_library_worker.progress.connect(self.update_progress)
        self.github_library_worker.finished.connect(self.github_library_finished)
        self.github_library_worker.error.connect(self.scan_error)
        self.github_library_worker.start()

    def start_scan(self, project_path: Path):
        """Start scanning a project."""
        if self.scan_worker and self.scan_worker.isRunning():
            QtWidgets.QMessageBox.warning(self, "Warning", "A scan is already in progress.")
            return
        
        # Disable scan buttons
        self.scan_dir_btn.setEnabled(False)
        self.scan_github_btn.setEnabled(False)
        self.scan_github_library_btn.setEnabled(False)
        self.save_to_library_btn.setEnabled(False)
        
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
        
        # Re-enable buttons
        self.scan_dir_btn.setEnabled(True)
        self.scan_github_btn.setEnabled(True)
        self.scan_github_library_btn.setEnabled(True)
        self.save_to_library_btn.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Display results
        self.display_scan_results(result)
        
        # Switch to current scan tab
        self.tabs.setCurrentIndex(0)
        
        self.status_bar.showMessage("Scan completed successfully!")

    def github_library_finished(self, result: Dict):
        """Handle GitHub library scan completion."""
        # Re-enable buttons
        self.scan_dir_btn.setEnabled(True)
        self.scan_github_btn.setEnabled(True)
        self.scan_github_library_btn.setEnabled(True)
        self.save_to_library_btn.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Display GitHub library results
        self.display_github_library_results(result)
        
        # Switch to GitHub library tab
        self.tabs.setCurrentIndex(2)
        
        self.status_bar.showMessage("GitHub library scan completed successfully!")

    def scan_error(self, error_message: str):
        """Handle scan errors."""
        QtWidgets.QMessageBox.critical(self, "Scan Error", error_message)
        
        # Re-enable buttons
        self.scan_dir_btn.setEnabled(True)
        self.scan_github_btn.setEnabled(True)
        self.scan_github_library_btn.setEnabled(True)
        
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

    def save_to_library(self):
        """Save current scan result to library."""
        if not self.current_scan_result:
            QtWidgets.QMessageBox.warning(self, "Warning", "No scan result to save.")
            return
        
        project_name = Path(self.current_scan_result['project_path']).name
        
        # Generate unique name if project already exists
        base_name = project_name
        counter = 1
        while project_name in self.library_data:
            project_name = f"{base_name}_{counter}"
            counter += 1
        
        self.library_data[project_name] = {
            'project_path': self.current_scan_result['project_path'],
            'scan_date': QtCore.QDateTime.currentDateTime().toString(),
            'analysis_data': self.current_scan_result['analysis_data'],
            'context_data': self.current_scan_result['context_data']
        }
        
        self.save_library()
        self.update_library_display()
        
        QtWidgets.QMessageBox.information(self, "Success", f"Project '{project_name}' saved to library!")

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
