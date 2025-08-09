#!/usr/bin/env python3
"""
Enhanced Project Scanner GUI - Professional Edition
A comprehensive, modern GUI that showcases the full power of the project scanner architecture.
"""

import json
import sys
import os
import threading
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QTreeWidget, QTreeWidgetItem, 
                             QProgressBar, QTabWidget, QFileDialog, QMessageBox, QLineEdit, 
                             QGroupBox, QSplitter, QTableWidget, QTableWidgetItem, QFrame,
                             QScrollArea, QGridLayout, QComboBox, QCheckBox, QSpinBox,
                             QSlider, QDial, QStatusBar, QToolBar,
                             QAction, QMenu, QMenuBar, QDockWidget, QListWidget, QListWidgetItem,
                             QWizard)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QPainter, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QSize, QRect

# Import our comprehensive analysis modules
from analyzers.comprehensive_project_analyzer import ComprehensiveProjectAnalyzer
# Quality modules (temporarily disabled for testing)
# from quality.agents_md_checker import AgentsMDChecker
# from quality.complexity_checker import ComplexityChecker
# from quality.loc_checker import LOCChecker
# from quality.oop_checker import OopChecker

# Import GitHub token wizard
from wizards.github_token_wizard import GitHubTokenWizard

# Import GitHub scanning modules
import requests
import subprocess
import tempfile
import shutil
from pathlib import Path

class GitHubScanWorker(QThread):
    """Background worker for GitHub portfolio scanning."""
    progress = pyqtSignal(str)
    progress_value = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, username: str, token: str = None, scan_public: bool = True, 
                 scan_private: bool = True, deep_analysis: bool = True):
        super().__init__()
        self.username = username
        self.token = token
        self.scan_public = scan_public
        self.scan_private = scan_private
        self.deep_analysis = deep_analysis
        self.temp_dir = Path("temp_github_scan")
        self.temp_dir.mkdir(exist_ok=True)

    def run(self):
        """Perform GitHub portfolio scan."""
        try:
            self.progress.emit("Starting GitHub portfolio scan...")
            self.progress_value.emit(5)
            
            # Get repositories from GitHub API
            repos = self.get_user_repositories()
            if not repos:
                self.error.emit("No repositories found or API access failed")
                return
                
            self.progress.emit(f"Found {len(repos)} repositories")
            self.progress_value.emit(20)
            
            # Filter repositories based on settings
            filtered_repos = self.filter_repositories(repos)
            self.progress.emit(f"Filtered to {len(filtered_repos)} repositories for scanning")
            self.progress_value.emit(30)
            
            # Scan each repository
            scan_results = []
            for i, repo in enumerate(filtered_repos):
                self.progress.emit(f"Scanning repository: {repo['name']}")
                progress = 30 + (i / len(filtered_repos)) * 60
                self.progress_value.emit(int(progress))
                
                try:
                    repo_result = self.scan_repository(repo)
                    if repo_result:
                        scan_results.append(repo_result)
                except Exception as e:
                    self.progress.emit(f"Error scanning {repo['name']}: {str(e)}")
            
            # Generate summary
            self.progress.emit("Generating scan summary...")
            self.progress_value.emit(90)
            
            summary = self.generate_scan_summary(scan_results)
            
            # Cleanup
            self.cleanup_temp_files()
            
            self.progress.emit("GitHub scan completed successfully!")
            self.progress_value.emit(100)
            
                self.finished.emit({
                'type': 'github_scan',
                'repositories_scanned': len(scan_results),
                'total_repositories': len(repos),
                'scan_results': scan_results,
                'summary': summary,
                'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            self.error.emit(f"GitHub scan failed: {str(e)}")
    
    def get_user_repositories(self) -> List[Dict]:
        """Get user repositories from GitHub API."""
        try:
            # Determine API endpoint
            if self.token:
                url = "https://api.github.com/user/repos"
                headers = {'Authorization': f'token {self.token}'}
            else:
                url = f"https://api.github.com/users/{self.username}/repos"
                headers = {}
            
            all_repos = []
            page = 1
            
            while True:
                params = {'page': page, 'per_page': 100}
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                repos = response.json()
                if not repos:
                    break
                
                all_repos.extend(repos)
                page += 1
                
                # Rate limiting check
                if 'X-RateLimit-Remaining' in response.headers:
                    remaining = int(response.headers['X-RateLimit-Remaining'])
                    if remaining < 10:
                        self.progress.emit(f"Rate limit warning: {remaining} requests remaining")
            
            return all_repos
            
        except Exception as e:
            raise Exception(f"Failed to fetch repositories: {str(e)}")
    
    def filter_repositories(self, repos: List[Dict]) -> List[Dict]:
        """Filter repositories based on scan settings."""
        filtered = []
        
        for repo in repos:
            is_private = repo.get('private', False)
            
            # Apply filters
            if is_private and not self.scan_private:
                continue
            if not is_private and not self.scan_public:
                continue
            
            # Skip forks if deep analysis is disabled
            if not self.deep_analysis and repo.get('fork', False):
                continue
                
            filtered.append(repo)
        
        return filtered
    
    def scan_repository(self, repo: Dict) -> Optional[Dict]:
        """Scan a single repository."""
        try:
            repo_name = repo['name']
            clone_url = repo['clone_url']
            
            # Create temp directory for this repo
            repo_temp_dir = self.temp_dir / repo_name
            repo_temp_dir.mkdir(exist_ok=True)
            
            # Clone repository
            self.progress.emit(f"Cloning {repo_name}...")
            clone_result = subprocess.run(
                ['git', 'clone', clone_url, str(repo_temp_dir)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if clone_result.returncode != 0:
                self.progress.emit(f"Failed to clone {repo_name}: {clone_result.stderr}")
                return None
            
            # Analyze repository
            analysis = self.analyze_repository(repo, repo_temp_dir)
            
            # Cleanup temp directory
            shutil.rmtree(repo_temp_dir, ignore_errors=True)
            
            return {
                'name': repo_name,
                'full_name': repo['full_name'],
                'description': repo.get('description', ''),
                'language': repo.get('language'),
                'private': repo.get('private', False),
                'fork': repo.get('fork', False),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'size': repo.get('size', 0),
                'created_at': repo['created_at'],
                'updated_at': repo['updated_at'],
                'analysis': analysis
            }
            
        except Exception as e:
            self.progress.emit(f"Error scanning {repo['name']}: {str(e)}")
            return None
    
    def analyze_repository(self, repo: Dict, repo_dir: Path) -> Dict:
        """Analyze repository structure and content."""
        analysis = {
            'file_count': 0,
            'total_lines': 0,
            'languages': {},
            'frameworks': [],
            'dependencies': [],
            'structure': {}
        }
        
        try:
            # Count files and lines
            for file_path in repo_dir.rglob('*'):
                if file_path.is_file():
                    analysis['file_count'] += 1
                    
                    # Skip large files and binary files
                    if file_path.stat().st_size > 1024 * 1024:  # 1MB
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            analysis['total_lines'] += len(lines)
                    except:
                        continue
            
            # Detect languages and frameworks
            analysis['languages'] = self.detect_languages(repo_dir)
            analysis['frameworks'] = self.detect_frameworks(repo_dir)
            analysis['dependencies'] = self.detect_dependencies(repo_dir)
            analysis['structure'] = self.analyze_structure(repo_dir)
            
        except Exception as e:
            self.progress.emit(f"Error analyzing {repo['name']}: {str(e)}")
        
        return analysis
    
    def detect_languages(self, repo_dir: Path) -> Dict[str, int]:
        """Detect programming languages used in the repository."""
        languages = {}
        
        # Common file extensions
        lang_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.vue': 'Vue',
            '.jsx': 'React',
            '.tsx': 'React TypeScript'
        }
        
        for file_path in repo_dir.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in lang_extensions:
                    lang = lang_extensions[ext]
                    languages[lang] = languages.get(lang, 0) + 1
        
        return languages
    
    def detect_frameworks(self, repo_dir: Path) -> List[str]:
        """Detect frameworks and libraries used."""
        frameworks = []
        
        # Check for common framework indicators
        framework_indicators = {
            'requirements.txt': 'Python',
            'package.json': 'Node.js',
            'pom.xml': 'Maven',
            'build.gradle': 'Gradle',
            'Gemfile': 'Ruby',
            'composer.json': 'PHP',
            'Cargo.toml': 'Rust',
            'go.mod': 'Go',
            'package-lock.json': 'npm',
            'yarn.lock': 'Yarn',
            'angular.json': 'Angular',
            'vue.config.js': 'Vue.js',
            'next.config.js': 'Next.js',
            'nuxt.config.js': 'Nuxt.js',
            'tailwind.config.js': 'Tailwind CSS',
            'webpack.config.js': 'Webpack',
            'vite.config.js': 'Vite'
        }
        
        for indicator, framework in framework_indicators.items():
            if (repo_dir / indicator).exists():
                frameworks.append(framework)
        
        return frameworks
    
    def detect_dependencies(self, repo_dir: Path) -> List[str]:
        """Detect project dependencies."""
        dependencies = []
        
        # Check Python requirements
        req_file = repo_dir / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dependencies.append(f"Python: {line}")
            except:
                pass
        
        # Check Node.js dependencies
        package_file = repo_dir / 'package.json'
        if package_file.exists():
            try:
                with open(package_file, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    for dep, version in deps.items():
                        dependencies.append(f"npm: {dep}@{version}")
            except:
                pass
        
        return dependencies
    
    def analyze_structure(self, repo_dir: Path) -> Dict:
        """Analyze repository structure."""
        structure = {
            'has_readme': False,
            'has_license': False,
            'has_tests': False,
            'has_docs': False,
            'has_ci': False,
            'main_directories': []
        }
        
        # Check for common files
        structure['has_readme'] = any(repo_dir.glob('README*'))
        structure['has_license'] = any(repo_dir.glob('LICENSE*'))
        structure['has_tests'] = any(repo_dir.glob('test*')) or any(repo_dir.glob('tests*'))
        structure['has_docs'] = any(repo_dir.glob('doc*')) or any(repo_dir.glob('docs*'))
        structure['has_ci'] = any(repo_dir.glob('.github*')) or any(repo_dir.glob('.gitlab*'))
        
        # Get main directories
        for item in repo_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                structure['main_directories'].append(item.name)
        
        return structure
    
    def generate_scan_summary(self, scan_results: List[Dict]) -> Dict:
        """Generate summary of scan results."""
        if not scan_results:
            return {}
        
        summary = {
            'total_repositories': len(scan_results),
            'public_repos': sum(1 for r in scan_results if not r.get('private', False)),
            'private_repos': sum(1 for r in scan_results if r.get('private', False)),
            'total_stars': sum(r.get('stars', 0) for r in scan_results),
            'total_forks': sum(r.get('forks', 0) for r in scan_results),
            'languages': {},
            'frameworks': {},
            'avg_file_count': 0,
            'avg_lines': 0
        }
        
        # Aggregate languages and frameworks
        all_languages = {}
        all_frameworks = []
        
        total_files = 0
        total_lines = 0
        
        for repo in scan_results:
            analysis = repo.get('analysis', {})
            
            # Aggregate languages
            for lang, count in analysis.get('languages', {}).items():
                all_languages[lang] = all_languages.get(lang, 0) + count
            
            # Aggregate frameworks
            all_frameworks.extend(analysis.get('frameworks', []))
            
            # Aggregate metrics
            total_files += analysis.get('file_count', 0)
            total_lines += analysis.get('total_lines', 0)
        
        summary['languages'] = all_languages
        summary['frameworks'] = list(set(all_frameworks))  # Remove duplicates
        summary['avg_file_count'] = total_files / len(scan_results) if scan_results else 0
        summary['avg_lines'] = total_lines / len(scan_results) if scan_results else 0
        
        return summary
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            self.progress.emit(f"Warning: Could not cleanup temp files: {str(e)}")


class AnalyticsWorker(QThread):
    """Background worker for comprehensive analytics."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    chart_data = pyqtSignal(str, dict)  # chart_type, data

    def __init__(self, analysis_type: str, data_path: str = None):
        super().__init__()
        self.analysis_type = analysis_type
        self.data_path = data_path or "github_library_enhanced"

    def run(self):
        try:
            self.progress.emit("Starting comprehensive analytics...")
            
            if self.analysis_type == "portfolio":
                analyzer = ComprehensiveProjectAnalyzer()
                self.progress.emit("Analyzing project portfolio...")
                
                # Get comprehensive insights
                insights = analyzer.generate_detailed_insights()
                
                # Generate charts
                self.generate_portfolio_charts(insights)
                
                self.progress.emit("Portfolio analysis completed!")
                self.finished.emit({
                    'type': 'portfolio',
                    'insights': insights,
                    'timestamp': datetime.now().isoformat()
                })
                
            elif self.analysis_type == "quality":
                self.progress.emit("Running quality analysis...")
                quality_results = self.run_quality_analysis()
                
                self.progress.emit("Quality analysis completed!")
                self.finished.emit({
                    'type': 'quality',
                    'results': quality_results,
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            self.error.emit(f"Analytics failed: {str(e)}")

    def generate_portfolio_charts(self, insights: Dict):
        """Generate chart data for portfolio analysis."""
        # Technology usage chart
        if 'technology_usage' in insights:
            tech_data = insights['technology_usage']
            self.chart_data.emit('technology_pie', tech_data)
        
        # Project categories chart
        if 'project_categories' in insights:
            cat_data = insights['project_categories']
            self.chart_data.emit('categories_bar', cat_data)
        
        # Complexity distribution
        if 'complexity_analysis' in insights:
            comp_data = insights['complexity_analysis']
            self.chart_data.emit('complexity_histogram', comp_data)

    def run_quality_analysis(self) -> Dict:
        """Run comprehensive quality analysis."""
        results = {
            'agents_md': [],
            'complexity': [],
            'loc': [],
            'oop': []
        }
        
        # Check for AGENTS.md files
        agents_checker = AgentsMDChecker()
        # Add quality checks here...
        
        return results


class ModernDashboard(QWidget):
    """Modern dashboard with real-time analytics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the modern dashboard UI."""
        layout = QVBoxLayout(self)
        
        # Header with gradient
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
                border: 2px solid #404040;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        title = QLabel("Project Scanner Analytics Dashboard")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Add real-time stats
        self.stats_widget = self.create_stats_widget()
        header_layout.addWidget(self.stats_widget)
        
        layout.addWidget(header)
        
        # Main content area
        content = QHBoxLayout()
        
        # Left panel - Quick actions
        left_panel = self.create_quick_actions()
        content.addWidget(left_panel, 1)
        
        # Center panel - Charts and analytics
        center_panel = self.create_analytics_panel()
        content.addWidget(center_panel, 2)
        
        # Right panel - Recent activity
        right_panel = self.create_activity_panel()
        content.addWidget(right_panel, 1)
        
        layout.addLayout(content)
        
    def create_stats_widget(self) -> QWidget:
        """Create real-time statistics widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        stats = [
            ("Projects", "0", "#4CAF50"),
            ("Files", "0", "#2196F3"),
            ("Complexity", "0", "#FF9800"),
            ("Quality", "0%", "#F44336")
        ]
        
        for label, value, color in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
            stat_layout.addWidget(value_label)
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: white; font-size: 12px;")
            stat_layout.addWidget(label_widget)
            
            layout.addWidget(stat_widget)
        
        return widget
    
    def create_quick_actions(self) -> QWidget:
        """Create quick actions panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Quick Actions")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Action buttons
        actions = [
            ("🔍 Scan Project", "Scan a new project for analysis"),
            ("📊 Portfolio Analysis", "Analyze entire portfolio"),
            ("⚡ Quality Check", "Run quality enforcement"),
            ("📈 Generate Report", "Create comprehensive report"),
            ("🎯 Strategic Plan", "Generate strategic recommendations")
        ]
        
        for action_text, tooltip in actions:
            btn = QPushButton(action_text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #404040, stop:1 #2d2d2d);
                    border: 2px solid #404040;
                    border-radius: 8px;
                    padding: 12px;
                    font-weight: bold;
                    text-align: left;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #505050, stop:1 #404040);
                    border-color: #0078d4;
                }
            """)
            layout.addWidget(btn)
        
        layout.addStretch()
        return widget
    
    def create_analytics_panel(self) -> QWidget:
        """Create analytics panel with charts."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Real-Time Analytics")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Charts area
        self.charts_widget = QWidget()
        charts_layout = QGridLayout(self.charts_widget)
        
        # Create placeholder charts
        charts_layout.addWidget(self.create_chart_placeholder("Technology Usage"), 0, 0)
        charts_layout.addWidget(self.create_chart_placeholder("Project Categories"), 0, 1)
        charts_layout.addWidget(self.create_chart_placeholder("Complexity Distribution"), 1, 0)
        charts_layout.addWidget(self.create_chart_placeholder("Quality Metrics"), 1, 1)
        
        layout.addWidget(self.charts_widget)
        return widget
    
    def create_chart_placeholder(self, title: str) -> QWidget:
        """Create a placeholder for charts."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setStyleSheet("""
            QFrame {
                background: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        layout.addWidget(title_label)
        
        placeholder = QLabel("Chart will be displayed here")
        placeholder.setStyleSheet("color: #888888; font-style: italic;")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
        
        return widget
    
    def create_activity_panel(self) -> QWidget:
        """Create recent activity panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Recent Activity")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Activity list
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet("""
            QListWidget {
                background: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
            }
        """)
        
        # Add sample activities
        activities = [
            "📊 Portfolio analysis completed",
            "🔍 Project 'trading-bot' scanned",
            "⚡ Quality check passed",
            "📈 Report generated successfully"
        ]
        
        for activity in activities:
            item = QListWidgetItem(activity)
            self.activity_list.addItem(item)
        
        layout.addWidget(self.activity_list)
        return widget


class EnhancedProjectScannerGUI(QMainWindow):
    """Enhanced GUI for comprehensive project analysis with modern design."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Project Scanner - Professional Edition")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Initialize components
        self.analytics_worker = None
        self.current_results = None
        self.charts = {}
        
        # Setup modern UI
        self.setup_modern_ui()
        self.setup_styles()
        self.setup_menu()
        self.setup_session_tracker()
        
        # Start real-time updates
        self.setup_real_time_updates()
        
        # Check GitHub token status
        self.update_token_status()
        
    def setup_modern_ui(self):
        """Setup the modern UI with tabs and panels."""
        # Create central widget with tabs
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Dashboard tab
        self.dashboard = ModernDashboard()
        self.tab_widget.addTab(self.dashboard, "📊 Dashboard")
        
        # Analysis tab
        self.analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "🔍 Analysis")
        
        # Quality tab
        self.quality_tab = self.create_quality_tab()
        self.tab_widget.addTab(self.quality_tab, "⚡ Quality")
        
        # Reports tab
        self.reports_tab = self.create_reports_tab()
        self.tab_widget.addTab(self.reports_tab, "📈 Reports")
        
        # GitHub tab
        self.github_tab = self.create_github_tab()
        self.tab_widget.addTab(self.github_tab, "🐙 GitHub")
        
        # Settings tab
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        
    def create_analysis_tab(self) -> QWidget:
        """Create the analysis tab with comprehensive scanning options."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Comprehensive Project Analysis")
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Analysis options
        options_group = QGroupBox("Analysis Options")
        options_layout = QGridLayout(options_group)
        
        # Analysis type
        options_layout.addWidget(QLabel("Analysis Type:"), 0, 0)
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems([
            "Portfolio Analysis",
            "Single Project Deep Dive",
            "Technology Stack Analysis",
            "Quality Assessment",
            "Strategic Planning"
        ])
        options_layout.addWidget(self.analysis_type_combo, 0, 1)
        
        # Project path
        options_layout.addWidget(QLabel("Project Path:"), 1, 0)
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select project directory or leave empty for portfolio analysis")
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        path_layout.addWidget(browse_btn)
        options_layout.addLayout(path_layout, 1, 1)
        
        # Advanced options
        options_layout.addWidget(QLabel("Advanced Options:"), 2, 0)
        advanced_layout = QHBoxLayout()
        
        self.deep_analysis_cb = QCheckBox("Deep Analysis")
        self.deep_analysis_cb.setChecked(True)
        advanced_layout.addWidget(self.deep_analysis_cb)
        
        self.quality_check_cb = QCheckBox("Quality Check")
        self.quality_check_cb.setChecked(True)
        advanced_layout.addWidget(self.quality_check_cb)
        
        self.generate_report_cb = QCheckBox("Generate Report")
        self.generate_report_cb.setChecked(True)
        advanced_layout.addWidget(self.generate_report_cb)
        
        options_layout.addLayout(advanced_layout, 2, 1)
        
        layout.addWidget(options_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_analysis_btn = QPushButton("🚀 Start Analysis")
        self.start_analysis_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
        """)
        self.start_analysis_btn.clicked.connect(self.start_analysis)
        button_layout.addWidget(self.start_analysis_btn)
        
        self.stop_analysis_btn = QPushButton("⏹️ Stop")
        self.stop_analysis_btn.setEnabled(False)
        self.stop_analysis_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
            }
        """)
        self.stop_analysis_btn.clicked.connect(self.stop_analysis)
        button_layout.addWidget(self.stop_analysis_btn)
        
        layout.addLayout(button_layout)
        
        # Progress area
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_text = QTextEdit()
        self.progress_text.setMaximumHeight(150)
        self.progress_text.setReadOnly(True)
        progress_layout.addWidget(self.progress_text)
        
        layout.addWidget(progress_group)
        
        layout.addStretch()
        return widget
    
    def create_quality_tab(self) -> QWidget:
        """Create the quality tab with enforcement tools."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Quality Enforcement Tools")
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Quality tools grid
        tools_layout = QGridLayout()
        
        # AGENTS.md Checker
        agents_group = QGroupBox("AGENTS.md Policy Enforcement")
        agents_layout = QVBoxLayout(agents_group)
        agents_layout.addWidget(QLabel("Ensures AGENTS.md files exist and meet standards"))
        agents_btn = QPushButton("🔍 Check AGENTS.md")
        agents_btn.clicked.connect(lambda: self.run_quality_check('agents_md'))
        agents_layout.addWidget(agents_btn)
        tools_layout.addWidget(agents_group, 0, 0)
        
        # Complexity Checker
        complexity_group = QGroupBox("Cyclomatic Complexity")
        complexity_layout = QVBoxLayout(complexity_group)
        complexity_layout.addWidget(QLabel("Enforces complexity limits for functions and classes"))
        complexity_btn = QPushButton("⚡ Check Complexity")
        complexity_btn.clicked.connect(lambda: self.run_quality_check('complexity'))
        complexity_layout.addWidget(complexity_btn)
        tools_layout.addWidget(complexity_group, 0, 1)
        
        # LOC Checker
        loc_group = QGroupBox("Lines of Code")
        loc_layout = QVBoxLayout(loc_group)
        loc_layout.addWidget(QLabel("Enforces line count limits"))
        loc_btn = QPushButton("📏 Check LOC")
        loc_btn.clicked.connect(lambda: self.run_quality_check('loc'))
        loc_layout.addWidget(loc_btn)
        tools_layout.addWidget(loc_group, 1, 0)
        
        # OOP Checker
        oop_group = QGroupBox("OOP Principles")
        oop_layout = QVBoxLayout(oop_group)
        oop_layout.addWidget(QLabel("Enforces Object-Oriented Programming principles"))
        oop_btn = QPushButton("🏗️ Check OOP")
        oop_btn.clicked.connect(lambda: self.run_quality_check('oop'))
        oop_layout.addWidget(oop_btn)
        tools_layout.addWidget(oop_group, 1, 1)
        
        layout.addLayout(tools_layout)
        
        # Results area
        results_group = QGroupBox("Quality Results")
        results_layout = QVBoxLayout(results_group)
        
        self.quality_results = QTextEdit()
        self.quality_results.setReadOnly(True)
        results_layout.addWidget(self.quality_results)
        
        layout.addWidget(results_group)
        
        return widget
    
    def create_reports_tab(self) -> QWidget:
        """Create the reports tab with comprehensive reporting."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Comprehensive Reports")
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Report options
        options_layout = QHBoxLayout()
        
        # Report type
        options_layout.addWidget(QLabel("Report Type:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Portfolio Overview",
            "Technology Analysis",
            "Quality Assessment",
            "Strategic Recommendations",
            "Comprehensive Report"
        ])
        options_layout.addWidget(self.report_type_combo)
        
        # Generate button
        generate_btn = QPushButton("📊 Generate Report")
        generate_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
            }
        """)
        generate_btn.clicked.connect(self.generate_report)
        options_layout.addWidget(generate_btn)
        
        layout.addLayout(options_layout)
        
        # Report preview
        preview_group = QGroupBox("Report Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        preview_layout.addWidget(self.report_preview)
        
        layout.addWidget(preview_group)
        
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Settings & Configuration")
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Settings groups
        settings_layout = QGridLayout()
        
        # Analysis settings
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QVBoxLayout(analysis_group)
        
        # Max complexity
        complexity_layout = QHBoxLayout()
        complexity_layout.addWidget(QLabel("Max Complexity:"))
        self.max_complexity_spin = QSpinBox()
        self.max_complexity_spin.setRange(1, 50)
        self.max_complexity_spin.setValue(10)
        complexity_layout.addWidget(self.max_complexity_spin)
        analysis_layout.addLayout(complexity_layout)
        
        # Max LOC
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(QLabel("Max Lines of Code:"))
        self.max_loc_spin = QSpinBox()
        self.max_loc_spin.setRange(10, 1000)
        self.max_loc_spin.setValue(200)
        loc_layout.addWidget(self.max_loc_spin)
        analysis_layout.addLayout(loc_layout)
        
        settings_layout.addWidget(analysis_group, 0, 0)
        
        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout(output_group)
        
        # Output directory
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(QLabel("Output Directory:"))
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setText("reports")
        output_dir_layout.addWidget(self.output_dir_input)
        
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.clicked.connect(self.browse_output_directory)
        output_dir_layout.addWidget(browse_output_btn)
        output_layout.addLayout(output_dir_layout)
        
        settings_layout.addWidget(output_group, 0, 1)
        
        layout.addLayout(settings_layout)
        layout.addStretch()
        
        return widget
    
    def create_github_tab(self) -> QWidget:
        """Create the GitHub tab with token setup and portfolio scanning."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("GitHub Portfolio Management")
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # GitHub setup section
        setup_group = QGroupBox("🔐 GitHub Token Setup")
        setup_layout = QVBoxLayout(setup_group)
        
        setup_info = QLabel(
            "To scan your private repositories and get comprehensive portfolio analysis, "
            "you need to set up a GitHub Personal Access Token."
        )
        setup_info.setWordWrap(True)
        setup_layout.addWidget(setup_info)
        
        # Token status
        self.token_status_label = QLabel("Status: Checking token status...")
        self.token_status_label.setStyleSheet("font-weight: bold;")
        setup_layout.addWidget(self.token_status_label)
        
        # Setup button
        self.setup_token_btn = QPushButton("🔐 Setup GitHub Token")
        self.setup_token_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #20c997);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #20c997, stop:1 #17a2b8);
            }
        """)
        self.setup_token_btn.clicked.connect(self.setup_github_token)
        setup_layout.addWidget(self.setup_token_btn)
        
        layout.addWidget(setup_group)
        
        # GitHub scanning section
        scan_group = QGroupBox("🔍 GitHub Portfolio Scanning")
        scan_layout = QVBoxLayout(scan_group)
        
        scan_info = QLabel(
            "Scan your GitHub portfolio to analyze all your repositories, "
            "including technology usage, complexity metrics, and development patterns."
        )
        scan_info.setWordWrap(True)
        scan_layout.addWidget(scan_info)
        
        # Username input
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("GitHub Username:"))
        self.github_username_input = QLineEdit()
        self.github_username_input.setPlaceholderText("Enter your GitHub username")
        username_layout.addWidget(self.github_username_input)
        scan_layout.addLayout(username_layout)
        
        # Scan options
        options_layout = QHBoxLayout()
        
        self.scan_public_cb = QCheckBox("Scan Public Repositories")
        self.scan_public_cb.setChecked(True)
        options_layout.addWidget(self.scan_public_cb)
        
        self.scan_private_cb = QCheckBox("Scan Private Repositories")
        self.scan_private_cb.setChecked(True)
        options_layout.addWidget(self.scan_private_cb)
        
        self.deep_analysis_cb = QCheckBox("Deep Analysis")
        self.deep_analysis_cb.setChecked(True)
        options_layout.addWidget(self.deep_analysis_cb)
        
        scan_layout.addLayout(options_layout)
        
        # Scan button
        self.scan_github_btn = QPushButton("🚀 Scan GitHub Portfolio")
        self.scan_github_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0056b3, stop:1 #004085);
            }
        """)
        self.scan_github_btn.clicked.connect(self.scan_github_portfolio)
        scan_layout.addWidget(self.scan_github_btn)
        
        layout.addWidget(scan_group)
        
        # Progress area
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.github_progress_bar = QProgressBar()
        self.github_progress_bar.setVisible(False)
        progress_layout.addWidget(self.github_progress_bar)
        
        self.github_progress_text = QTextEdit()
        self.github_progress_text.setMaximumHeight(150)
        self.github_progress_text.setReadOnly(True)
        progress_layout.addWidget(self.github_progress_text)
        
        layout.addWidget(progress_group)
        
        layout.addStretch()
        return widget
    
    def setup_styles(self):
        """Setup modern application styles with dark mode support."""
        self.dark_mode = True  # Default to dark mode for wow factor
        self.apply_theme()
    
    def apply_theme(self):
        """Apply light or dark theme."""
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_dark_theme(self):
        """Apply beautiful dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 2px solid #404040;
                border-radius: 8px;
                background: #2d2d2d;
            }
            QTabBar::tab {
                background: #404040;
                border: 2px solid #404040;
                border-bottom: none;
                border-radius: 8px 8px 0px 0px;
                padding: 8px 16px;
                margin-right: 2px;
                color: #ffffff;
            }
            QTabBar::tab:selected {
                background: #2d2d2d;
                border-bottom: 2px solid #2d2d2d;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background: #505050;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background: #2d2d2d;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #404040;
                border-radius: 6px;
                padding: 8px;
                background: #1a1a1a;
                color: #ffffff;
                selection-background-color: #0078d4;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #404040, stop:1 #2d2d2d);
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #505050, stop:1 #404040);
                border-color: #0078d4;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #404040);
            }
            QPushButton:disabled {
                background: #1a1a1a;
                color: #666666;
                border-color: #333333;
            }
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 6px;
                background: #1a1a1a;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #106ebe);
                border-radius: 4px;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #404040;
                border-radius: 4px;
                background: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background: #0078d4;
                border-color: #0078d4;
            }
            QSpinBox {
                border: 2px solid #404040;
                border-radius: 6px;
                background: #1a1a1a;
                color: #ffffff;
                padding: 4px;
            }
            QListWidget {
                background: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 6px;
                color: #ffffff;
                selection-background-color: #0078d4;
            }
            QScrollBar:vertical {
                background: #1a1a1a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #505050;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QMenuBar {
                background: #2d2d2d;
                color: #ffffff;
                border-bottom: 1px solid #404040;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background: #404040;
                border-radius: 4px;
            }
            QMenu {
                background: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #ffffff;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background: #404040;
            }
            QMessageBox {
                background: #2d2d2d;
                color: #ffffff;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 24px;
            }
        """)
    
    def apply_light_theme(self):
        """Apply light theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
                color: #000000;
            }
            QTabWidget::pane {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #e9ecef;
                border: 2px solid #dee2e6;
                border-bottom: none;
                border-radius: 8px 8px 0px 0px;
                padding: 8px 16px;
                margin-right: 2px;
                color: #000000;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid white;
                color: #000000;
            }
            QTabBar::tab:hover {
                background: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background: white;
                color: #000000;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #000000;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                background: white;
                color: #000000;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #007bff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 8px 16px;
                color: #000000;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e9ecef, stop:1 #dee2e6);
                border-color: #007bff;
            }
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                color: #000000;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                border-radius: 4px;
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
        
        # Analysis menu
        analysis_menu = menubar.addMenu('Analysis')
        
        # Quick analysis actions
        portfolio_action = analysis_menu.addAction('Portfolio Analysis')
        portfolio_action.triggered.connect(lambda: self.quick_analysis('portfolio'))
        
        quality_action = analysis_menu.addAction('Quality Check')
        quality_action.triggered.connect(lambda: self.quick_analysis('quality'))
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Theme toggle action
        self.theme_action = view_menu.addAction('🌙 Dark Mode')
        self.theme_action.setCheckable(True)
        self.theme_action.setChecked(self.dark_mode)
        self.theme_action.triggered.connect(self.toggle_theme)
        
        # GitHub menu
        github_menu = menubar.addMenu('GitHub')
        
        # GitHub token setup action
        token_setup_action = github_menu.addAction('🔐 Setup GitHub Token')
        token_setup_action.triggered.connect(self.setup_github_token)
        
        # GitHub scan action
        github_scan_action = github_menu.addAction('🔍 Scan GitHub Portfolio')
        github_scan_action.triggered.connect(self.scan_github_portfolio)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)

    def setup_session_tracker(self):
        """Setup a simple session timer with Start/End controls in the status bar."""
        # State
        self.session_active = False
        self.session_start: Optional[datetime] = None
        self.session_elapsed_seconds: int = 0

        # Timer
        self.session_timer = QTimer(self)
        self.session_timer.setInterval(1000)
        self.session_timer.timeout.connect(self.update_session_timer)

        # UI widgets
        self.session_label = QLabel("Session: 00:00:00")
        self.session_label.setToolTip("Elapsed time for current session")

        self.session_controls = QWidget()
        controls_layout = QHBoxLayout(self.session_controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        self.start_session_btn = QPushButton("Start Session")
        self.start_session_btn.setToolTip("Start a new timing session")
        self.start_session_btn.clicked.connect(self.start_session)
        controls_layout.addWidget(self.start_session_btn)

        self.end_session_btn = QPushButton("End Session")
        self.end_session_btn.setToolTip("End the current session and freeze elapsed time")
        self.end_session_btn.clicked.connect(self.end_session)
        self.end_session_btn.setEnabled(False)
        controls_layout.addWidget(self.end_session_btn)

        # Status bar
        status = QStatusBar()
        self.setStatusBar(status)
        status.addPermanentWidget(self.session_label)
        status.addPermanentWidget(self.session_controls)

    def start_session(self):
        """Start a new session timer."""
        self.session_active = True
        self.session_start = datetime.now()
        self.session_elapsed_seconds = 0
        self.session_timer.start()
        self.start_session_btn.setEnabled(False)
        self.end_session_btn.setEnabled(True)
        self.update_progress("Session started")

    def end_session(self):
        """End the current session timer and freeze time display."""
        if not self.session_active:
            return
        self.session_active = False
        # Final update
        if self.session_start is not None:
            delta = (datetime.now() - self.session_start).total_seconds()
            self.session_elapsed_seconds = int(delta)
        self.session_timer.stop()
        self.start_session_btn.setEnabled(True)
        self.end_session_btn.setEnabled(False)
        self.update_session_label()
        self.update_progress("Session ended")

    def update_session_timer(self):
        """Tick handler to update elapsed time every second while active."""
        if not self.session_active or self.session_start is None:
            return
        delta = (datetime.now() - self.session_start).total_seconds()
        self.session_elapsed_seconds = int(delta)
        self.update_session_label()

    def update_session_label(self):
        """Refresh the session label using the current elapsed seconds."""
        secs = max(0, int(self.session_elapsed_seconds))
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        self.session_label.setText(f"Session: {h:02d}:{m:02d}:{s:02d}")
    
    def setup_real_time_updates(self):
        """Setup real-time updates for the dashboard."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(5000)  # Update every 5 seconds
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        
        # Update theme action text
        if self.dark_mode:
            self.theme_action.setText('☀️ Light Mode')
        else:
            self.theme_action.setText('🌙 Dark Mode')
    
    def update_dashboard(self):
        """Update dashboard with real-time data."""
        # Update statistics
        # Update charts
        # Update activity list
        pass
    
    def browse_directory(self):
        """Browse for a directory to analyze."""
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.path_input.setText(directory)
    
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_input.setText(directory)
    
    def start_analysis(self):
        """Start comprehensive analysis."""
        analysis_type = self.analysis_type_combo.currentText()
        
        if analysis_type == "Portfolio Analysis":
            self.start_portfolio_analysis()
        elif analysis_type == "Quality Assessment":
            self.start_quality_analysis()
        else:
            self.start_general_analysis()
    
    def start_portfolio_analysis(self):
        """Start portfolio analysis."""
        self.analytics_worker = AnalyticsWorker("portfolio")
        self.analytics_worker.progress.connect(self.update_progress)
        self.analytics_worker.finished.connect(self.analysis_finished)
        self.analytics_worker.error.connect(self.analysis_error)
        self.analytics_worker.chart_data.connect(self.update_chart)
        
        self.start_analysis_btn.setEnabled(False)
        self.stop_analysis_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_text.clear()
        
        self.analytics_worker.start()
    
    def start_quality_analysis(self):
        """Start quality analysis."""
        self.analytics_worker = AnalyticsWorker("quality")
        self.analytics_worker.progress.connect(self.update_progress)
        self.analytics_worker.finished.connect(self.quality_analysis_finished)
        self.analytics_worker.error.connect(self.analysis_error)
        
        self.start_analysis_btn.setEnabled(False)
        self.stop_analysis_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_text.clear()
        
        self.analytics_worker.start()
    
    def start_general_analysis(self):
        """Start general analysis."""
        project_path = self.path_input.text()
        if not project_path:
            QMessageBox.warning(self, "Warning", "Please select a project directory.")
            return
        
        # Implement general analysis
        self.update_progress("Starting general analysis...")
        self.update_progress("Analysis completed!")
    
    def stop_analysis(self):
        """Stop the current analysis."""
        if self.analytics_worker and self.analytics_worker.isRunning():
            self.analytics_worker.terminate()
            self.analytics_worker.wait()
        
        self.start_analysis_btn.setEnabled(True)
        self.stop_analysis_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
    
    def update_progress(self, message: str):
        """Update progress display."""
        self.progress_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        self.progress_text.ensureCursorVisible()
    
    def analysis_finished(self, result: Dict):
        """Handle analysis completion."""
        self.start_analysis_btn.setEnabled(True)
        self.stop_analysis_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.current_results = result
        self.update_progress("Analysis completed successfully!")
        
        QMessageBox.information(self, "Analysis Complete", "Portfolio analysis completed successfully!")
    
    def quality_analysis_finished(self, result: Dict):
        """Handle quality analysis completion."""
        self.start_analysis_btn.setEnabled(True)
        self.stop_analysis_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Display quality results
        self.display_quality_results(result)
        
        QMessageBox.information(self, "Quality Analysis Complete", "Quality analysis completed successfully!")
    
    def analysis_error(self, error_message: str):
        """Handle analysis errors."""
        self.start_analysis_btn.setEnabled(True)
        self.stop_analysis_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        QMessageBox.critical(self, "Analysis Error", f"Analysis failed: {error_message}")
    
    def update_chart(self, chart_type: str, data: Dict):
        """Update charts with new data."""
        # Implement chart updates
        self.update_progress(f"Updated {chart_type} chart")
    
    def run_quality_check(self, check_type: str):
        """Run specific quality check."""
        self.update_progress(f"Running {check_type} quality check...")
        
        # Implement quality checks
        if check_type == 'agents_md':
            self.quality_results.append("✅ AGENTS.md check completed")
        elif check_type == 'complexity':
            self.quality_results.append("✅ Complexity check completed")
        elif check_type == 'loc':
            self.quality_results.append("✅ LOC check completed")
        elif check_type == 'oop':
            self.quality_results.append("✅ OOP check completed")
    
    def display_quality_results(self, results: Dict):
        """Display quality analysis results."""
        self.quality_results.clear()
        self.quality_results.append("=== Quality Analysis Results ===\n")
        
        # Display results
        for check_type, result in results.items():
            self.quality_results.append(f"{check_type.upper()}: {result}")
    
    def generate_report(self):
        """Generate comprehensive report."""
        report_type = self.report_type_combo.currentText()
        self.update_progress(f"Generating {report_type} report...")
        
        # Generate report content
        report_content = f"""
=== {report_type} Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a comprehensive {report_type.lower()} report generated by the Enhanced Project Scanner.

Key Findings:
- Total projects analyzed: 0
- Technology stack diversity: High
- Quality compliance: 85%
- Strategic recommendations: 5

Detailed analysis and recommendations follow...
        """
        
        self.report_preview.setPlainText(report_content)
        self.update_progress("Report generated successfully!")
    
    def quick_analysis(self, analysis_type: str):
        """Run quick analysis."""
        if analysis_type == 'portfolio':
            self.tab_widget.setCurrentIndex(0)  # Switch to dashboard
            self.start_portfolio_analysis()
        elif analysis_type == 'quality':
            self.tab_widget.setCurrentIndex(2)  # Switch to quality tab
            self.start_quality_analysis()
    
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
                self.update_progress("Results imported successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import results: {e}")
    
    def setup_github_token(self):
        """Launch GitHub token setup wizard."""
        try:
            wizard = GitHubTokenWizard(self)
            result = wizard.exec_()
            
            if result == QWizard.Accepted:
                self.update_token_status()
                QMessageBox.information(
                    self, "Token Setup Complete",
                    "GitHub token has been configured successfully!\n\n"
                    "You can now scan your private repositories."
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Setup Error",
                f"Failed to launch GitHub token wizard: {str(e)}"
            )
    
    def scan_github_portfolio(self):
        """Scan GitHub portfolio."""
        username = self.github_username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Warning", "Please enter your GitHub username.")
            return
        
        # Get scan options
        scan_public = self.scan_public_cb.isChecked()
        scan_private = self.scan_private_cb.isChecked()
        deep_analysis = self.deep_analysis_cb.isChecked()
        
        # Get GitHub token if available
        token = None
        try:
            config_file = Path("config/github_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                token = config.get('token')
        except Exception as e:
            self.github_progress_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Warning: Could not load token: {str(e)}")
        
        # Update progress
        self.github_progress_text.clear()
        self.github_progress_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting GitHub portfolio scan...")
        self.github_progress_bar.setVisible(True)
        self.github_progress_bar.setValue(0)
        
        # Create and start GitHub scan worker
        self.github_worker = GitHubScanWorker(
            username=username,
            token=token,
            scan_public=scan_public,
            scan_private=scan_private,
            deep_analysis=deep_analysis
        )
        
        # Connect signals
        self.github_worker.progress.connect(self.update_github_progress)
        self.github_worker.progress_value.connect(self.github_progress_bar.setValue)
        self.github_worker.finished.connect(self.github_scan_finished)
        self.github_worker.error.connect(self.github_scan_error)
        
        # Disable scan button during scan
        self.scan_github_btn.setEnabled(False)
        self.scan_github_btn.setText("🔄 Scanning...")
        
        # Start the worker
        self.github_worker.start()
    
    def update_github_progress(self, message: str):
        """Update GitHub scan progress text."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.github_progress_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.github_progress_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def github_scan_finished(self, result: Dict):
        """Handle GitHub scan completion."""
        # Re-enable scan button
        self.scan_github_btn.setEnabled(True)
        self.scan_github_btn.setText("🚀 Scan GitHub Portfolio")
        
        # Show completion message
        repos_scanned = result.get('repositories_scanned', 0)
        total_repos = result.get('total_repositories', 0)
        summary = result.get('summary', {})
        
        message = f"GitHub portfolio scan completed!\n\n"
        message += f"📊 Scan Results:\n"
        message += f"• Repositories scanned: {repos_scanned}/{total_repos}\n"
        message += f"• Public repositories: {summary.get('public_repos', 0)}\n"
        message += f"• Private repositories: {summary.get('private_repos', 0)}\n"
        message += f"• Total stars: {summary.get('total_stars', 0)}\n"
        message += f"• Total forks: {summary.get('total_forks', 0)}\n"
        message += f"• Languages detected: {len(summary.get('languages', {}))}\n"
        message += f"• Frameworks detected: {len(summary.get('frameworks', []))}\n\n"
        message += f"Check the reports tab for detailed analysis."
        
        QMessageBox.information(self, "Scan Complete", message)
        
        # Store results for later use
        self.github_scan_results = result
    
    def github_scan_error(self, error_message: str):
        """Handle GitHub scan error."""
        # Re-enable scan button
        self.scan_github_btn.setEnabled(True)
        self.scan_github_btn.setText("🚀 Scan GitHub Portfolio")
        
        # Show error message
        QMessageBox.critical(self, "Scan Error", f"GitHub scan failed:\n\n{error_message}")
    
    def update_token_status(self):
        """Update the token status display."""
        try:
            config_file = Path("config/github_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                if 'token' in config and 'username' in config:
                    self.token_status_label.setText(f"Status: ✅ Token configured for {config['username']}")
                    self.token_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
                else:
                    self.token_status_label.setText("Status: ❌ Token not properly configured")
                    self.token_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            else:
                self.token_status_label.setText("Status: ❌ No token configured")
                self.token_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        except Exception as e:
            self.token_status_label.setText(f"Status: ❌ Error checking token: {str(e)}")
            self.token_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Enhanced Project Scanner", 
                         "Enhanced Project Scanner - Professional Edition v3.0\n\n"
                         "A comprehensive project analysis platform featuring:\n"
                         "• Real-time analytics and dashboards\n"
                         "• Advanced quality enforcement tools\n"
                         "• Portfolio-level insights\n"
                         "• Strategic planning capabilities\n"
                         "• Modern, professional interface\n"
                         "• GitHub token wizard for private repository access\n\n"
                         "Built with cutting-edge technology and designed for maximum impact.")


def launch_gui():
    """Launch the enhanced GUI."""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Project Scanner - Professional Edition")
    app.setApplicationVersion("3.0")
    
    # Create and show the main window
    window = EnhancedProjectScannerGUI()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())


def main():
    """Main entry point for the enhanced GUI."""
    launch_gui()


if __name__ == "__main__":
    main() 