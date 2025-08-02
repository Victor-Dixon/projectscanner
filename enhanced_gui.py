#!/usr/bin/env python3
"""
Enhanced Project Scanner GUI
Integrates comprehensive project analysis with a modern GUI interface.
"""

import json
import sys
import os
import threading
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QTreeWidget, QTreeWidgetItem, QProgressBar, QTabWidget, QFileDialog, QMessageBox, QLineEdit, QGroupBox, QSplitter, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont, QIcon, QPixmap

# Import our enhanced analysis modules
from comprehensive_project_analyzer import ComprehensiveProjectAnalyzer
from enhanced_project_scanner import EnhancedProjectScanner
from enhanced_github_scanner import EnhancedGitHubScanner


class EnhancedScanWorker(QThread):
    """Background worker for enhanced project scanning."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    analysis_progress = pyqtSignal(str, int, int)  # message, current, total

    def __init__(self, project_path: Path, scan_type: str = "comprehensive", output_dir: Optional[Path] = None):
        super().__init__()
        self.project_path = project_path
        self.scan_type = scan_type
        self.output_dir = output_dir or project_path
        self.scanner = None

    def run(self):
        try:
            self.progress.emit(f"Starting enhanced scan of {self.project_path}")
            
            if self.scan_type == "comprehensive":
                # Use comprehensive project analyzer
                self.scanner = ComprehensiveProjectAnalyzer(str(self.output_dir))
                self.progress.emit("Loading existing data for comprehensive analysis...")
                
                # Analyze all projects
                result = self.scanner.analyze_all_projects()
                
                self.progress.emit("Comprehensive analysis completed!")
                self.finished.emit({
                    'type': 'comprehensive',
                    'result': result,
                    'project_path': str(self.project_path),
                    'output_dir': str(self.output_dir)
                })
                
            elif self.scan_type == "enhanced":
                # Use enhanced project scanner
                self.scanner = EnhancedProjectScanner(str(self.project_path))
                self.progress.emit("Performing enhanced project analysis...")
                
                result = self.scanner.scan_project()
                
                # Save analysis
                output_file = self.scanner.save_analysis()
                
                self.progress.emit("Enhanced analysis completed!")
                self.finished.emit({
                    'type': 'enhanced',
                    'result': result,
                    'project_path': str(self.project_path),
                    'output_file': output_file
                })
                
        except Exception as e:
            self.error.emit(f"Enhanced scan failed: {str(e)}")


class EnhancedGitHubWorker(QThread):
    """Background worker for enhanced GitHub scanning."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    repo_progress = pyqtSignal(str, int, int)  # repo_name, current, total

    def __init__(self, github_username: str, output_dir: str = "github_library_enhanced", force_rescan: bool = False, max_repos: Optional[int] = None):
        super().__init__()
        self.github_username = github_username
        self.output_dir = output_dir
        self.force_rescan = force_rescan
        self.max_repos = max_repos

    def run(self):
        try:
            self.progress.emit(f"Starting enhanced GitHub scan for user: {self.github_username}")
            
            # Use enhanced GitHub scanner
            scanner = EnhancedGitHubScanner(self.github_username, self.output_dir)
            
            # Custom progress callback
            def progress_callback(message):
                self.progress.emit(message)
            
            # Scan all repositories with enhanced analysis
            scanner.scan_all_repositories(
                force_rescan=self.force_rescan,
                max_repos=self.max_repos
            )
            
            # Load results
            library_file = scanner.library_file
            summary_file = Path(self.output_dir) / "enhanced_library_summary.json"
            
            result = {
                'type': 'enhanced_github',
                'github_username': self.github_username,
                'output_dir': self.output_dir,
                'library_file': str(library_file),
                'summary_file': str(summary_file),
                'library_data': {},
                'summary_data': {}
            }
            
            # Load library data
            if library_file.exists():
                with open(library_file, 'r', encoding='utf-8') as f:
                    result['library_data'] = json.load(f)
            
            # Load summary data
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    result['summary_data'] = json.load(f)
            
            self.progress.emit("Enhanced GitHub scan completed!")
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(f"Enhanced GitHub scan failed: {str(e)}")


class EnhancedProjectScannerGUI(QMainWindow):
    """Enhanced GUI for comprehensive project analysis."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Project Scanner - Comprehensive Analysis")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.scan_worker = None
        self.github_worker = None
        self.current_results = None
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Load existing data
        self.load_existing_data()
    
    def setup_ui(self):
        """Setup the main UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 1000])
        
        # Setup menu
        self.setup_menu()
    
    def create_control_panel(self):
        """Create the control panel with scan options."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Enhanced Project Scanner")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Scan Type Selection
        scan_group = QGroupBox("Scan Type")
        scan_layout = QVBoxLayout(scan_group)
        
        self.scan_type_combo = QtWidgets.QComboBox()
        self.scan_type_combo.addItems([
            "Enhanced Single Project",
            "Comprehensive Portfolio Analysis",
            "Enhanced GitHub Library"
        ])
        scan_layout.addWidget(QLabel("Select Scan Type:"))
        scan_layout.addWidget(self.scan_type_combo)
        
        layout.addWidget(scan_group)
        
        # Project Selection
        project_group = QGroupBox("Project Selection")
        project_layout = QVBoxLayout(project_group)
        
        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select project directory...")
        dir_layout.addWidget(self.dir_input)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_btn)
        
        project_layout.addLayout(dir_layout)
        
        # GitHub username
        github_layout = QHBoxLayout()
        github_layout.addWidget(QLabel("GitHub Username:"))
        self.github_input = QLineEdit()
        self.github_input.setPlaceholderText("Enter GitHub username...")
        github_layout.addWidget(self.github_input)
        
        project_layout.addLayout(github_layout)
        
        layout.addWidget(project_group)
        
        # Scan Configuration
        config_group = QGroupBox("Scan Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Force rescan checkbox
        self.force_rescan_cb = QtWidgets.QCheckBox("Force Rescan")
        config_layout.addWidget(self.force_rescan_cb)
        
        # Max repos input
        max_repos_layout = QHBoxLayout()
        max_repos_layout.addWidget(QLabel("Max Repositories:"))
        self.max_repos_input = QLineEdit()
        self.max_repos_input.setPlaceholderText("Leave empty for all")
        max_repos_layout.addWidget(self.max_repos_input)
        config_layout.addLayout(max_repos_layout)
        
        layout.addWidget(config_group)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Enhanced Scan")
        self.start_btn.clicked.connect(self.start_scan)
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; }")
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 10px; }")
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Progress Text
        self.progress_text = QTextEdit()
        self.progress_text.setMaximumHeight(150)
        self.progress_text.setReadOnly(True)
        layout.addWidget(self.progress_text)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        return panel
    
    def create_results_panel(self):
        """Create the results display panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Results tabs
        self.results_tabs = QTabWidget()
        layout.addWidget(self.results_tabs)
        
        # Summary tab
        self.summary_tab = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_tab)
        self.results_tabs.addTab(self.summary_tab, "Summary")
        
        # Analysis tab
        self.analysis_tab = QWidget()
        self.analysis_layout = QVBoxLayout(self.analysis_tab)
        self.results_tabs.addTab(self.analysis_tab, "Detailed Analysis")
        
        # Projects tab
        self.projects_tab = QWidget()
        self.projects_layout = QVBoxLayout(self.projects_tab)
        self.results_tabs.addTab(self.projects_tab, "Projects")
        
        # Recommendations tab
        self.recommendations_tab = QWidget()
        self.recommendations_layout = QVBoxLayout(self.recommendations_tab)
        self.results_tabs.addTab(self.recommendations_tab, "Recommendations")
        
        return panel
    
    def setup_styles(self):
        """Setup application styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
            QTextEdit {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)
    
    def setup_menu(self):
        """Setup the application menu."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Export action
        export_action = file_menu.addAction('Export Results')
        export_action.triggered.connect(self.export_results)
        
        # Import action
        import_action = file_menu.addAction('Import Results')
        import_action.triggered.connect(self.import_results)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
    
    def browse_directory(self):
        """Browse for a directory to scan."""
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.dir_input.setText(directory)
    
    def start_scan(self):
        """Start the enhanced scan process."""
        scan_type = self.scan_type_combo.currentText()
        
        if scan_type == "Enhanced Single Project":
            self.start_single_project_scan()
        elif scan_type == "Comprehensive Portfolio Analysis":
            self.start_comprehensive_scan()
        elif scan_type == "Enhanced GitHub Library":
            self.start_github_scan()
    
    def start_single_project_scan(self):
        """Start enhanced single project scan."""
        project_path = self.dir_input.text()
        if not project_path:
            QMessageBox.warning(self, "Warning", "Please select a project directory.")
            return
        
        project_path = Path(project_path)
        if not project_path.exists():
            QMessageBox.warning(self, "Warning", "Selected directory does not exist.")
            return
        
        self.scan_worker = EnhancedScanWorker(project_path, "enhanced")
        self.scan_worker.progress.connect(self.update_progress)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.error.connect(self.scan_error)
        
        self.start_scan_worker()
    
    def start_comprehensive_scan(self):
        """Start comprehensive portfolio analysis."""
        data_dir = self.dir_input.text() or "github_library_enhanced"
        data_path = Path(data_dir)
        
        if not data_path.exists():
            QMessageBox.warning(self, "Warning", f"Data directory {data_dir} does not exist.")
            return
        
        self.scan_worker = EnhancedScanWorker(data_path, "comprehensive")
        self.scan_worker.progress.connect(self.update_progress)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.error.connect(self.scan_error)
        
        self.start_scan_worker()
    
    def start_github_scan(self):
        """Start enhanced GitHub library scan."""
        username = self.github_input.text()
        if not username:
            QMessageBox.warning(self, "Warning", "Please enter a GitHub username.")
            return
        
        force_rescan = self.force_rescan_cb.isChecked()
        max_repos = None
        if self.max_repos_input.text():
            try:
                max_repos = int(self.max_repos_input.text())
            except ValueError:
                QMessageBox.warning(self, "Warning", "Max repositories must be a number.")
                return
        
        self.github_worker = EnhancedGitHubWorker(
            username,
            force_rescan=force_rescan,
            max_repos=max_repos
        )
        self.github_worker.progress.connect(self.update_progress)
        self.github_worker.finished.connect(self.github_scan_finished)
        self.github_worker.error.connect(self.scan_error)
        
        self.start_github_worker()
    
    def start_scan_worker(self):
        """Start the scan worker."""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_text.clear()
        
        self.scan_worker.start()
    
    def start_github_worker(self):
        """Start the GitHub scan worker."""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_text.clear()
        
        self.github_worker.start()
    
    def stop_scan(self):
        """Stop the current scan."""
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.terminate()
            self.scan_worker.wait()
        
        if self.github_worker and self.github_worker.isRunning():
            self.github_worker.terminate()
            self.github_worker.wait()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
    
    def update_progress(self, message: str):
        """Update progress display."""
        self.progress_text.append(f"[{QtCore.QTime.currentTime().toString('hh:mm:ss')}] {message}")
        self.progress_text.ensureCursorVisible()
    
    def scan_finished(self, result: Dict):
        """Handle scan completion."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.current_results = result
        self.display_results(result)
        
        QMessageBox.information(self, "Scan Complete", "Enhanced scan completed successfully!")
    
    def github_scan_finished(self, result: Dict):
        """Handle GitHub scan completion."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.current_results = result
        self.display_github_results(result)
        
        QMessageBox.information(self, "GitHub Scan Complete", "Enhanced GitHub scan completed successfully!")
    
    def scan_error(self, error_message: str):
        """Handle scan errors."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        QMessageBox.critical(self, "Scan Error", f"Scan failed: {error_message}")
    
    def display_results(self, result: Dict):
        """Display scan results."""
        # Clear previous results
        for layout in [self.summary_layout, self.analysis_layout, self.projects_layout, self.recommendations_layout]:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        if result['type'] == 'enhanced':
            self.display_enhanced_results(result)
        elif result['type'] == 'comprehensive':
            self.display_comprehensive_results(result)
    
    def display_enhanced_results(self, result: Dict):
        """Display enhanced single project results."""
        analysis = result['result']
        
        # Summary
        if 'project_essence' in analysis:
            essence = analysis['project_essence']
            summary_text = f"""
            <h2>Project Summary</h2>
            <p><strong>Summary:</strong> {essence.get('summary', 'N/A')}</p>
            <p><strong>Primary Purpose:</strong> {essence.get('primary_purpose', 'N/A')}</p>
            <p><strong>Deployment Type:</strong> {essence.get('deployment_type', 'N/A')}</p>
            <p><strong>Technical Complexity:</strong> {essence.get('technical_complexity', 'N/A')}</p>
            <p><strong>Maintenance Status:</strong> {essence.get('maintenance_status', 'N/A')}</p>
            """
            
            summary_label = QLabel(summary_text)
            summary_label.setWordWrap(True)
            self.summary_layout.addWidget(summary_label)
        
        # Analysis
        analysis_text = QTextEdit()
        analysis_text.setPlainText(json.dumps(analysis, indent=2))
        self.analysis_layout.addWidget(analysis_text)
    
    def display_comprehensive_results(self, result: Dict):
        """Display comprehensive analysis results."""
        analysis = result['result']
        
        # Summary
        summary_text = f"""
        <h2>Portfolio Analysis Summary</h2>
        <p><strong>Total Projects:</strong> {analysis.get('total_projects', 0)}</p>
        <p><strong>Project Categories:</strong> {len(analysis.get('project_categories', {}))}</p>
        <p><strong>Business Domains:</strong> {len(analysis.get('business_domains', {}))}</p>
        """
        
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        self.summary_layout.addWidget(summary_label)
        
        # Projects table
        if 'detailed_analyses' in analysis:
            self.create_projects_table(analysis['detailed_analyses'])
        
        # Recommendations
        if 'recommendations' in analysis:
            recommendations_text = QTextEdit()
            recommendations_text.setPlainText("\n".join(analysis['recommendations']))
            self.recommendations_layout.addWidget(recommendations_text)
    
    def display_github_results(self, result: Dict):
        """Display GitHub scan results."""
        # Summary
        summary_text = f"""
        <h2>GitHub Library Analysis</h2>
        <p><strong>Username:</strong> {result.get('github_username', 'N/A')}</p>
        <p><strong>Total Repositories:</strong> {len(result.get('library_data', {}))}</p>
        """
        
        if 'summary_data' in result and result['summary_data']:
            summary = result['summary_data']
            summary_text += f"""
            <p><strong>Top Technologies:</strong> {', '.join(list(summary.get('technology_summary', {}).keys())[:5])}</p>
            <p><strong>Business Domains:</strong> {dict(summary.get('business_domains', {}))}</p>
            """
        
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        self.summary_layout.addWidget(summary_label)
        
        # Library data
        if 'library_data' in result:
            library_text = QTextEdit()
            library_text.setPlainText(json.dumps(result['library_data'], indent=2))
            self.analysis_layout.addWidget(library_text)
    
    def create_projects_table(self, projects: Dict):
        """Create a table showing all projects."""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Project ID', 'Primary Purpose', 'Quality', 'Technologies'])
        
        table.setRowCount(len(projects))
        
        for i, (project_id, project_data) in enumerate(projects.items()):
            essence = project_data.get('essence_summary', {})
            
            table.setItem(i, 0, QTableWidgetItem(project_id))
            table.setItem(i, 1, QTableWidgetItem(essence.get('primary_purpose', 'Unknown')))
            table.setItem(i, 2, QTableWidgetItem(essence.get('technical_complexity', 'unknown')))
            table.setItem(i, 3, QTableWidgetItem(', '.join(essence.get('key_technologies', [])[:3])))
        
        table.resizeColumnsToContents()
        self.projects_layout.addWidget(table)
    
    def load_existing_data(self):
        """Load existing analysis data."""
        # Check for existing comprehensive analysis
        comprehensive_file = Path("github_library_enhanced/comprehensive_analysis_results.json")
        if comprehensive_file.exists():
            try:
                with open(comprehensive_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.current_results = {
                    'type': 'comprehensive',
                    'result': data
                }
                
                self.display_results(self.current_results)
                self.update_progress("Loaded existing comprehensive analysis data")
                
            except Exception as e:
                self.update_progress(f"Error loading existing data: {e}")
    
    def export_results(self):
        """Export current results to file."""
        if not self.current_results:
            QMessageBox.warning(self, "Warning", "No results to export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "enhanced_analysis_results.json", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_results, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Export Complete", f"Results exported to {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export results: {e}")
    
    def import_results(self):
        """Import results from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Results", "", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.current_results = data
                self.display_results(data)
                
                QMessageBox.information(self, "Import Complete", "Results imported successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import results: {e}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Enhanced Project Scanner", 
                         "Enhanced Project Scanner v2.0\n\n"
                         "Comprehensive project analysis with deep insights into:\n"
                         "- Project essence and purpose\n"
                         "- Business domain classification\n"
                         "- Technical quality assessment\n"
                         "- Portfolio-level insights\n"
                         "- Smart consolidation recommendations")


def main():
    """Main entry point for the enhanced GUI."""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Project Scanner")
    app.setApplicationVersion("2.0")
    
    # Create and show the main window
    window = EnhancedProjectScannerGUI()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 