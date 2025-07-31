#!/usr/bin/env python3
"""
Interactive Skill Tree Viewer
Displays skill analysis results in a user-friendly GUI
"""

import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QTextEdit, QLabel, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import sys

class SkillTreeViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.skill_data = self.load_skill_data()
        self.init_ui()
        
    def load_skill_data(self):
        """Load skill analysis data."""
        data = {}
        try:
            # Load enhanced skill tree report
            with open('skill_analysis/enhanced_skill_tree_report.json', 'r', encoding='utf-8') as f:
                data['skill_tree'] = json.load(f)
        except FileNotFoundError:
            data['skill_tree'] = {}
        
        try:
            # Load knowledge base report
            with open('skill_analysis/enhanced_knowledge_base_report.json', 'r', encoding='utf-8') as f:
                data['knowledge_base'] = json.load(f)
        except FileNotFoundError:
            data['knowledge_base'] = {}
        
        return data
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🌳 Developer Skill Tree Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QHBoxLayout(central_widget)
        
        # Create splitter for left and right panels
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Skill Tree
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Skill Tree Title
        title_label = QLabel("🎯 Your Skill Tree")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)
        
        # Create skill tree widget
        self.skill_tree = QTreeWidget()
        self.skill_tree.setHeaderLabel("Skill Categories")
        self.skill_tree.setFont(QFont("Arial", 10))
        left_layout.addWidget(self.skill_tree)
        
        # Populate skill tree
        self.populate_skill_tree()
        
        # Right panel - Details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Details title
        details_title = QLabel("📊 Skill Details")
        details_title.setFont(QFont("Arial", 16, QFont.Bold))
        details_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(details_title)
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        right_layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.create_overview_tab()
        self.create_technologies_tab()
        self.create_projects_tab()
        self.create_insights_tab()
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        # Connect tree selection
        self.skill_tree.itemClicked.connect(self.on_skill_selected)
    
    def populate_skill_tree(self):
        """Populate the skill tree with data."""
        skill_tree_data = self.skill_data.get('skill_tree', {})
        
        # Core Technologies
        core_tech_item = QTreeWidgetItem(self.skill_tree, ["🔧 Core Technologies"])
        if 'core_technologies' in skill_tree_data:
            for tech_type, techs in skill_tree_data['core_technologies'].items():
                tech_item = QTreeWidgetItem(core_tech_item, [f"📁 {tech_type.title()}"])
                if isinstance(techs, dict):
                    for tech, count in techs.items():
                        if count > 0:
                            QTreeWidgetItem(tech_item, [f"{tech}: {count}"])
        
        # Expertise Areas
        expertise_item = QTreeWidgetItem(self.skill_tree, ["🎯 Expertise Areas"])
        if 'expertise_areas' in skill_tree_data:
            for area, count in skill_tree_data['expertise_areas'].items():
                if count > 0:
                    QTreeWidgetItem(expertise_item, [f"{area.replace('_', ' ').title()}: {count} projects"])
        
        # Code Quality
        quality_item = QTreeWidgetItem(self.skill_tree, ["📈 Code Quality"])
        if 'code_quality' in skill_tree_data:
            quality_data = skill_tree_data['code_quality']
            QTreeWidgetItem(quality_item, [f"Average Complexity: {quality_data.get('avg_complexity', 0):.2f}"])
            QTreeWidgetItem(quality_item, [f"Max Complexity: {quality_data.get('max_complexity', 0)}"])
            QTreeWidgetItem(quality_item, [f"High Complexity Files: {quality_data.get('high_complexity_count', 0)}"])
        
        # Development Practices
        practices_item = QTreeWidgetItem(self.skill_tree, ["🛠️ Development Practices"])
        if 'development_practices' in skill_tree_data:
            for practice, count in skill_tree_data['development_practices'].items():
                if count > 0:
                    QTreeWidgetItem(practices_item, [f"{practice.replace('_', ' ').title()}: {count} projects"])
        
        # Project Evolution
        evolution_item = QTreeWidgetItem(self.skill_tree, ["🚀 Project Evolution"])
        if 'project_evolution' in skill_tree_data:
            evolution_data = skill_tree_data['project_evolution']
            QTreeWidgetItem(evolution_item, [f"Total Projects: {evolution_data.get('total_projects', 0)}"])
            QTreeWidgetItem(evolution_item, [f"Technology Diversity: {evolution_data.get('technology_diversity', 0)}"])
        
        # Expand all items
        self.skill_tree.expandAll()
    
    def create_overview_tab(self):
        """Create the overview tab."""
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)
        
        # Overview text
        overview_text = QTextEdit()
        overview_text.setReadOnly(True)
        overview_text.setFont(QFont("Arial", 11))
        
        # Generate overview content
        skill_tree_data = self.skill_data.get('skill_tree', {})
        content = self.generate_overview_content(skill_tree_data)
        overview_text.setPlainText(content)
        
        layout.addWidget(overview_text)
        self.tab_widget.addTab(overview_widget, "📋 Overview")
    
    def create_technologies_tab(self):
        """Create the technologies tab."""
        tech_widget = QWidget()
        layout = QVBoxLayout(tech_widget)
        
        tech_text = QTextEdit()
        tech_text.setReadOnly(True)
        tech_text.setFont(QFont("Arial", 11))
        
        # Generate technologies content
        skill_tree_data = self.skill_data.get('skill_tree', {})
        content = self.generate_technologies_content(skill_tree_data)
        tech_text.setPlainText(content)
        
        layout.addWidget(tech_text)
        self.tab_widget.addTab(tech_widget, "🔧 Technologies")
    
    def create_projects_tab(self):
        """Create the projects tab."""
        projects_widget = QWidget()
        layout = QVBoxLayout(projects_widget)
        
        projects_text = QTextEdit()
        projects_text.setReadOnly(True)
        projects_text.setFont(QFont("Arial", 11))
        
        # Generate projects content
        knowledge_base = self.skill_data.get('knowledge_base', {})
        content = self.generate_projects_content(knowledge_base)
        projects_text.setPlainText(content)
        
        layout.addWidget(projects_text)
        self.tab_widget.addTab(projects_widget, "📁 Projects")
    
    def create_insights_tab(self):
        """Create the insights tab."""
        insights_widget = QWidget()
        layout = QVBoxLayout(insights_widget)
        
        insights_text = QTextEdit()
        insights_text.setReadOnly(True)
        insights_text.setFont(QFont("Arial", 11))
        
        # Generate insights content
        skill_tree_data = self.skill_data.get('skill_tree', {})
        knowledge_base = self.skill_data.get('knowledge_base', {})
        content = self.generate_insights_content(skill_tree_data, knowledge_base)
        insights_text.setPlainText(content)
        
        layout.addWidget(insights_text)
        self.tab_widget.addTab(insights_widget, "💡 Insights")
    
    def generate_overview_content(self, skill_tree_data):
        """Generate overview content."""
        content = "🚀 DEVELOPER SKILL ANALYSIS OVERVIEW\n"
        content += "=" * 50 + "\n\n"
        
        # Project Summary
        evolution = skill_tree_data.get('project_evolution', {})
        total_projects = evolution.get('total_projects', 0)
        content += f"📊 TOTAL PROJECTS: {total_projects}\n\n"
        
        # Expertise Areas
        expertise = skill_tree_data.get('expertise_areas', {})
        content += "🎯 EXPERTISE AREAS:\n"
        for area, count in expertise.items():
            if count > 0:
                content += f"  • {area.replace('_', ' ').title()}: {count} projects\n"
        content += "\n"
        
        # Code Quality
        quality = skill_tree_data.get('code_quality', {})
        content += "📈 CODE QUALITY METRICS:\n"
        content += f"  • Average Complexity: {quality.get('avg_complexity', 0):.2f}\n"
        content += f"  • Max Complexity: {quality.get('max_complexity', 0)}\n"
        content += f"  • High Complexity Files: {quality.get('high_complexity_count', 0)}\n"
        content += f"  • Total Files Analyzed: {quality.get('total_files', 0)}\n\n"
        
        # Development Practices
        practices = skill_tree_data.get('development_practices', {})
        content += "🛠️ DEVELOPMENT PRACTICES:\n"
        for practice, count in practices.items():
            if count > 0:
                content += f"  • {practice.replace('_', ' ').title()}: {count} projects\n"
        
        return content
    
    def generate_technologies_content(self, skill_tree_data):
        """Generate technologies content."""
        content = "🔧 TECHNOLOGY STACK ANALYSIS\n"
        content += "=" * 40 + "\n\n"
        
        # Core Technologies
        core_tech = skill_tree_data.get('core_technologies', {})
        content += "📁 FILE TYPES:\n"
        file_types = core_tech.get('file_types', {})
        for file_type, count in file_types.items():
            if count > 0:
                content += f"  • {file_type}: {count} files\n"
        content += "\n"
        
        # Languages
        languages = core_tech.get('languages', {})
        content += "💻 PROGRAMMING LANGUAGES:\n"
        for lang, count in languages.items():
            if count > 0:
                content += f"  • {lang}: {count} files\n"
        content += "\n"
        
        # Technology Diversity
        evolution = skill_tree_data.get('project_evolution', {})
        diversity = evolution.get('technology_diversity', 0)
        content += f"🌐 TECHNOLOGY DIVERSITY: {diversity} different technologies\n"
        
        return content
    
    def generate_projects_content(self, knowledge_base):
        """Generate projects content."""
        content = "📁 PROJECT ANALYSIS\n"
        content += "=" * 30 + "\n\n"
        
        # Project Categories
        project_patterns = knowledge_base.get('project_patterns', {})
        categories = project_patterns.get('project_categories', {})
        
        content += "🎯 PROJECT CATEGORIES:\n"
        for category, projects in categories.items():
            if projects:
                content += f"  • {category.replace('_', ' ').title()}: {len(projects)} projects\n"
        content += "\n"
        
        # Most Complex Projects
        most_complex = project_patterns.get('most_complex_projects', [])
        if most_complex:
            content += "🏆 MOST COMPLEX PROJECTS:\n"
            for i, project in enumerate(most_complex[:5], 1):
                content += f"  {i}. {project['repo']} (Complexity: {project['avg_complexity']:.2f})\n"
            content += "\n"
        
        # Largest Projects
        largest = project_patterns.get('largest_projects', [])
        if largest:
            content += "📦 LARGEST PROJECTS:\n"
            for i, project in enumerate(largest[:5], 1):
                content += f"  {i}. {project['repo']} ({project['file_count']} files)\n"
        
        return content
    
    def generate_insights_content(self, skill_tree_data, knowledge_base):
        """Generate insights content."""
        content = "💡 DEVELOPMENT INSIGHTS\n"
        content += "=" * 30 + "\n\n"
        
        # Skill Strengths
        expertise = skill_tree_data.get('expertise_areas', {})
        content += "💪 STRENGTHS:\n"
        strengths = [(area, count) for area, count in expertise.items() if count > 0]
        strengths.sort(key=lambda x: x[1], reverse=True)
        
        for area, count in strengths[:3]:
            content += f"  • {area.replace('_', ' ').title()}: {count} projects\n"
        content += "\n"
        
        # Growth Areas
        content += "🌱 GROWTH OPPORTUNITIES:\n"
        weak_areas = [(area, count) for area, count in expertise.items() if count == 0]
        for area, count in weak_areas[:3]:
            content += f"  • {area.replace('_', ' ').title()}: No projects yet\n"
        content += "\n"
        
        # Recommendations
        content += "🎯 RECOMMENDATIONS:\n"
        content += "  • Focus on your strongest technology areas\n"
        content += "  • Build on successful project patterns\n"
        content += "  • Explore new technologies outside your comfort zone\n"
        content += "  • Increase code quality and testing practices\n"
        content += "  • Document your knowledge for future reference\n"
        
        return content
    
    def on_skill_selected(self, item, column):
        """Handle skill tree item selection."""
        # This could be expanded to show detailed information for selected items
        pass

def main():
    """Main function to run the skill tree viewer."""
    app = QApplication(sys.argv)
    viewer = SkillTreeViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 