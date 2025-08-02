#!/usr/bin/env python3
"""
GitHub Repository Duplicate Analyzer
Identifies specific duplicates and provides consolidation recommendations.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import argparse


class DuplicateAnalyzer:
    """Analyzes GitHub repositories for duplicates and provides consolidation strategy."""
    
    def __init__(self, data_dir: str = "github_library_enhanced"):
        self.data_dir = Path(data_dir)
        self.repositories = {}
        self.duplicate_groups = []
        self.consolidation_recommendations = []
        self.similarity_threshold = 0.5  # Lowered threshold to catch more potential duplicates
        
    def load_repository_data(self) -> bool:
        """Load repository data from enhanced library."""
        try:
            # Load enhanced library summary
            summary_file = self.data_dir / "enhanced_library_summary.json"
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
                
                # Build repository data from summary
                for repo in summary_data.get('repositories', []):
                    repo_id = repo['id']
                    self.repositories[repo_id] = {
                        'name': repo['name'],
                        'language': repo['language'],
                        'private': repo['private'],
                        'files_scanned': repo['files_scanned'],
                        'description': '',  # Will be filled from individual files
                        'topics': [],
                        'content_analysis': {}
                    }
                
                print(f"✅ Loaded {len(self.repositories)} repositories from summary")
                
                # Try to load individual repository data
                self.load_individual_repo_data()
                
                return True
            
            print("❌ No enhanced library summary found")
            return False
            
        except Exception as e:
            print(f"❌ Error loading repository data: {e}")
            return False
    
    def load_individual_repo_data(self):
        """Load individual repository data files."""
        repo_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
        
        for repo_dir in repo_dirs:
            repo_id = repo_dir.name
            
            # Try to load project analysis
            analysis_files = list(repo_dir.glob("*_analysis.json"))
            if analysis_files:
                try:
                    with open(analysis_files[0], 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                    
                    if repo_id in self.repositories:
                        # Extract content analysis
                        self.repositories[repo_id]['content_analysis'] = {
                            'total_files': len(analysis_data),
                            'file_types': self.analyze_file_types(analysis_data),
                            'summary': self.generate_content_summary(analysis_data)
                        }
                except Exception as e:
                    print(f"⚠️  Could not load analysis for {repo_id}: {e}")
            
            # Try to load ChatGPT context for description
            context_files = list(repo_dir.glob("*_context*.json"))
            if context_files:
                try:
                    with open(context_files[0], 'r', encoding='utf-8') as f:
                        context_data = json.load(f)
                    
                    if repo_id in self.repositories:
                        # Extract description from context
                        description = self.extract_description_from_context(context_data)
                        if description:
                            self.repositories[repo_id]['description'] = description
                except Exception as e:
                    print(f"⚠️  Could not load context for {repo_id}: {e}")
    
    def analyze_file_types(self, analysis_data: Dict) -> Dict:
        """Analyze file types from analysis data."""
        file_types = Counter()
        for file_path, file_data in analysis_data.items():
            if 'language' in file_data:
                ext = file_data['language']
                if ext:
                    file_types[ext] += 1
        return dict(file_types)
    
    def generate_content_summary(self, analysis_data: Dict) -> str:
        """Generate content summary from analysis data."""
        summary_parts = []
        
        # Count functions and classes
        total_functions = 0
        total_classes = 0
        languages = Counter()
        
        for file_path, file_data in analysis_data.items():
            if 'language' in file_data and file_data['language']:
                languages[file_data['language']] += 1
            
            if 'functions' in file_data:
                total_functions += len(file_data['functions'])
            
            if 'classes' in file_data:
                total_classes += len(file_data['classes'])
        
        if languages:
            summary_parts.append(f"Primary language: {languages.most_common(1)[0][0]}")
        
        if total_functions > 0:
            summary_parts.append(f"{total_functions} functions")
        
        if total_classes > 0:
            summary_parts.append(f"{total_classes} classes")
        
        return ", ".join(summary_parts)
    
    def extract_description_from_context(self, context_data: Dict) -> str:
        """Extract description from ChatGPT context data."""
        # Look for description in various possible locations
        if isinstance(context_data, dict):
            # Try common keys
            for key in ['description', 'summary', 'overview', 'project_description']:
                if key in context_data and context_data[key]:
                    return str(context_data[key])
            
            # Look in nested structures
            for value in context_data.values():
                if isinstance(value, dict):
                    desc = self.extract_description_from_context(value)
                    if desc:
                        return desc
        
        return ""
    
    def extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        if not text:
            return set()
        
        # Remove common words and extract meaningful terms
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Clean and tokenize
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filter meaningful words
        keywords = set()
        for word in words:
            if (len(word) > 2 and 
                word not in common_words and 
                not word.isdigit()):
                keywords.add(word)
        
        return keywords
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        if not text1 or not text2:
            return 0.0
        
        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def analyze_repository_content(self, repo_data: Dict) -> Dict:
        """Analyze repository content for duplicate detection."""
        analysis = {
            'name': repo_data.get('name', ''),
            'description': repo_data.get('description', ''),
            'topics': repo_data.get('topics', []),
            'language': repo_data.get('language', ''),
            'keywords': set(),
            'content_summary': '',
            'file_types': Counter(),
            'total_files': 0
        }
        
        # Extract keywords from name and description
        name_keywords = self.extract_keywords(repo_data.get('name', ''))
        desc_keywords = self.extract_keywords(repo_data.get('description', ''))
        analysis['keywords'] = name_keywords | desc_keywords
        
        # Analyze topics
        if repo_data.get('topics'):
            analysis['keywords'].update(repo_data['topics'])
        
        # Analyze content if available
        if 'content_analysis' in repo_data:
            content = repo_data['content_analysis']
            analysis['content_summary'] = content.get('summary', '')
            analysis['file_types'] = Counter(content.get('file_types', {}))
            analysis['total_files'] = content.get('total_files', 0)
        
        return analysis
    
    def find_duplicate_groups(self) -> List[List[str]]:
        """Find groups of duplicate repositories."""
        repo_analyses = {}
        
        # Analyze all repositories
        for repo_id, repo_data in self.repositories.items():
            repo_analyses[repo_id] = self.analyze_repository_content(repo_data)
        
        # Find duplicate groups
        duplicate_groups = []
        processed = set()
        
        for repo_id1, analysis1 in repo_analyses.items():
            if repo_id1 in processed:
                continue
            
            current_group = [repo_id1]
            processed.add(repo_id1)
            
            for repo_id2, analysis2 in repo_analyses.items():
                if repo_id2 in processed:
                    continue
                
                # Check for duplicates
                if self.is_duplicate(analysis1, analysis2):
                    current_group.append(repo_id2)
                    processed.add(repo_id2)
            
            if len(current_group) > 1:
                duplicate_groups.append(current_group)
        
        return duplicate_groups
    
    def is_duplicate(self, analysis1: Dict, analysis2: Dict) -> bool:
        """Determine if two repositories are duplicates."""
        # Check name similarity
        name_similarity = self.calculate_similarity(
            analysis1['name'], analysis2['name']
        )
        
        # Check description similarity
        desc_similarity = self.calculate_similarity(
            analysis1['description'], analysis2['description']
        )
        
        # Check keyword overlap
        keyword_overlap = len(analysis1['keywords'] & analysis2['keywords'])
        total_keywords = len(analysis1['keywords'] | analysis2['keywords'])
        keyword_similarity = keyword_overlap / total_keywords if total_keywords > 0 else 0
        
        # Check language match
        language_match = analysis1['language'] == analysis2['language'] and analysis1['language']
        
        # Check content similarity
        content_similarity = self.calculate_similarity(
            analysis1['content_summary'], analysis2['content_summary']
        )
        
        # Determine if duplicate based on multiple factors
        duplicate_score = 0
        factors = []
        
        # Lowered thresholds for more sensitive detection
        if name_similarity > 0.6:  # Lowered from 0.8
            duplicate_score += 0.3
            factors.append(f"Name similarity: {name_similarity:.2f}")
        
        if desc_similarity > 0.5:  # Lowered from 0.7
            duplicate_score += 0.25
            factors.append(f"Description similarity: {desc_similarity:.2f}")
        
        if keyword_similarity > 0.3:  # Lowered from 0.5
            duplicate_score += 0.2
            factors.append(f"Keyword overlap: {keyword_similarity:.2f}")
        
        if language_match:
            duplicate_score += 0.15
            factors.append("Same language")
        
        if content_similarity > 0.4:  # Lowered from 0.6
            duplicate_score += 0.1
            factors.append(f"Content similarity: {content_similarity:.2f}")
        
        # Special case: trading-related projects
        trading_keywords = {'trading', 'stock', 'portfolio', 'invest', 'robot', 'plug'}
        if (trading_keywords & analysis1['keywords'] and 
            trading_keywords & analysis2['keywords']):
            duplicate_score += 0.2
            factors.append("Trading-related projects")
        
        # Special case: ML/AI projects
        ml_keywords = {'ml', 'machine', 'learning', 'ai', 'model', 'neural'}
        if (ml_keywords & analysis1['keywords'] and 
            ml_keywords & analysis2['keywords']):
            duplicate_score += 0.15
            factors.append("ML/AI projects")
        
        return duplicate_score > 0.4  # Lowered threshold from 0.6
    
    def analyze_duplicate_patterns(self) -> Dict:
        """Analyze patterns in duplicate groups."""
        patterns = {
            'trading_bots': [],
            'ml_projects': [],
            'automation_tools': [],
            'web_apps': [],
            'personal_projects': [],
            'other': []
        }
        
        for group in self.duplicate_groups:
            group_keywords = set()
            for repo_id in group:
                repo_data = self.repositories[repo_id]
                analysis = self.analyze_repository_content(repo_data)
                group_keywords.update(analysis['keywords'])
            
            # Categorize based on keywords
            if any(kw in group_keywords for kw in ['trading', 'stock', 'portfolio', 'invest', 'robot', 'plug']):
                patterns['trading_bots'].append(group)
            elif any(kw in group_keywords for kw in ['ml', 'machine', 'learning', 'ai', 'model', 'neural']):
                patterns['ml_projects'].append(group)
            elif any(kw in group_keywords for kw in ['automation', 'bot', 'script', 'tool']):
                patterns['automation_tools'].append(group)
            elif any(kw in group_keywords for kw in ['web', 'website', 'app', 'ui']):
                patterns['web_apps'].append(group)
            elif any(kw in group_keywords for kw in ['personal', 'resume', 'practice']):
                patterns['personal_projects'].append(group)
            else:
                patterns['other'].append(group)
        
        return patterns
    
    def generate_consolidation_recommendations(self) -> List[Dict]:
        """Generate specific consolidation recommendations."""
        recommendations = []
        
        for group in self.duplicate_groups:
            # Analyze the group
            group_analysis = self.analyze_group(group)
            
            # Generate recommendation
            recommendation = {
                'group': group,
                'analysis': group_analysis,
                'consolidation_strategy': self.determine_consolidation_strategy(group_analysis),
                'priority': self.calculate_priority(group_analysis),
                'estimated_effort': self.estimate_effort(group_analysis)
            }
            
            recommendations.append(recommendation)
        
        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return recommendations
    
    def analyze_group(self, group: List[str]) -> Dict:
        """Analyze a duplicate group."""
        analyses = []
        total_files = 0
        languages = Counter()
        topics = Counter()
        
        for repo_id in group:
            repo_data = self.repositories[repo_id]
            analysis = self.analyze_repository_content(repo_data)
            analyses.append(analysis)
            
            total_files += analysis['total_files']
            if analysis['language']:
                languages[analysis['language']] += 1
            topics.update(analysis['topics'])
        
        return {
            'repositories': group,
            'analyses': analyses,
            'total_files': total_files,
            'languages': dict(languages),
            'topics': dict(topics),
            'size': len(group)
        }
    
    def determine_consolidation_strategy(self, group_analysis: Dict) -> str:
        """Determine the best consolidation strategy for a group."""
        size = group_analysis['size']
        total_files = group_analysis['total_files']
        
        if size == 2 and total_files < 50:
            return "Merge into single repository"
        elif size > 2 and total_files < 100:
            return "Consolidate into unified project"
        elif total_files > 100:
            return "Create modular architecture"
        else:
            return "Archive redundant repositories"
    
    def calculate_priority(self, group_analysis: Dict) -> float:
        """Calculate consolidation priority score."""
        size = group_analysis['size']
        total_files = group_analysis['total_files']
        
        # Higher priority for larger groups and more files
        priority = (size * 0.4) + (min(total_files / 100, 1.0) * 0.6)
        
        return priority
    
    def estimate_effort(self, group_analysis: Dict) -> str:
        """Estimate effort required for consolidation."""
        total_files = group_analysis['total_files']
        size = group_analysis['size']
        
        if total_files < 20 and size <= 2:
            return "Low (1-2 hours)"
        elif total_files < 50 and size <= 3:
            return "Medium (4-8 hours)"
        elif total_files < 100:
            return "High (1-2 days)"
        else:
            return "Very High (3-5 days)"
    
    def generate_detailed_report(self) -> str:
        """Generate a detailed duplicate analysis report."""
        report = []
        report.append("# GitHub Repository Duplicate Analysis Report")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append(f"- Total repositories analyzed: {len(self.repositories)}")
        report.append(f"- Duplicate groups found: {len(self.duplicate_groups)}")
        report.append(f"- Repositories with duplicates: {sum(len(g) for g in self.duplicate_groups)}")
        report.append("")
        
        # Duplicate patterns
        patterns = self.analyze_duplicate_patterns()
        report.append("## Duplicate Patterns by Category")
        report.append("")
        
        for category, groups in patterns.items():
            if groups:
                report.append(f"### {category.replace('_', ' ').title()}")
                report.append(f"- Groups: {len(groups)}")
                report.append(f"- Total repositories: {sum(len(g) for g in groups)}")
                report.append("")
        
        # Detailed recommendations
        recommendations = self.generate_consolidation_recommendations()
        report.append("## Consolidation Recommendations")
        report.append("")
        
        for i, rec in enumerate(recommendations, 1):
            report.append(f"### Recommendation {i}")
            report.append(f"**Repositories:** {', '.join(rec['group'])}")
            report.append(f"**Strategy:** {rec['consolidation_strategy']}")
            report.append(f"**Priority:** {rec['priority']:.2f}")
            report.append(f"**Effort:** {rec['estimated_effort']}")
            report.append("")
            
            # Add analysis details
            analysis = rec['analysis']
            report.append("**Analysis:**")
            report.append(f"- Total files: {analysis['total_files']}")
            report.append(f"- Languages: {', '.join(analysis['languages'].keys())}")
            report.append(f"- Common topics: {', '.join(list(analysis['topics'].keys())[:5])}")
            report.append("")
        
        # Action plan
        report.append("## Recommended Action Plan")
        report.append("")
        
        high_priority = [r for r in recommendations if r['priority'] > 0.7]
        medium_priority = [r for r in recommendations if 0.4 <= r['priority'] <= 0.7]
        low_priority = [r for r in recommendations if r['priority'] < 0.4]
        
        report.append("### Phase 1: High Priority Consolidations")
        for rec in high_priority[:3]:
            report.append(f"- {rec['consolidation_strategy']}: {', '.join(rec['group'])}")
        report.append("")
        
        report.append("### Phase 2: Medium Priority Consolidations")
        for rec in medium_priority[:5]:
            report.append(f"- {rec['consolidation_strategy']}: {', '.join(rec['group'])}")
        report.append("")
        
        report.append("### Phase 3: Low Priority Cleanup")
        for rec in low_priority:
            report.append(f"- Archive: {', '.join(rec['group'])}")
        report.append("")
        
        return "\n".join(report)
    
    def save_analysis_results(self, output_file: str = "duplicate_analysis_results.json"):
        """Save analysis results to JSON file."""
        # Convert sets to lists for JSON serialization
        recommendations = self.generate_consolidation_recommendations()
        for rec in recommendations:
            if 'analyses' in rec['analysis']:
                for analysis in rec['analysis']['analyses']:
                    if 'keywords' in analysis:
                        analysis['keywords'] = list(analysis['keywords'])
        
        results = {
            'duplicate_groups': self.duplicate_groups,
            'consolidation_recommendations': recommendations,
            'patterns': self.analyze_duplicate_patterns(),
            'summary': {
                'total_repositories': len(self.repositories),
                'duplicate_groups': len(self.duplicate_groups),
                'repositories_with_duplicates': sum(len(g) for g in self.duplicate_groups)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analysis results saved to {output_file}")
    
    def run(self) -> bool:
        """Run the complete duplicate analysis."""
        print("🔍 Starting GitHub Repository Duplicate Analysis")
        print("=" * 60)
        
        # Load repository data
        if not self.load_repository_data():
            return False
        
        # Find duplicate groups
        print("📊 Analyzing repositories for duplicates...")
        self.duplicate_groups = self.find_duplicate_groups()
        
        if not self.duplicate_groups:
            print("✅ No duplicates found!")
            return True
        
        print(f"🔍 Found {len(self.duplicate_groups)} duplicate groups")
        
        # Generate recommendations
        print("📋 Generating consolidation recommendations...")
        recommendations = self.generate_consolidation_recommendations()
        
        # Print summary
        print("\n📊 DUPLICATE ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total repositories: {len(self.repositories)}")
        print(f"Duplicate groups: {len(self.duplicate_groups)}")
        print(f"Repositories with duplicates: {sum(len(g) for g in self.duplicate_groups)}")
        
        # Print top recommendations
        print("\n🏆 TOP CONSOLIDATION RECOMMENDATIONS")
        print("=" * 60)
        
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"\n{i}. {rec['consolidation_strategy']}")
            print(f"   Repositories: {', '.join(rec['group'])}")
            print(f"   Priority: {rec['priority']:.2f}")
            print(f"   Effort: {rec['estimated_effort']}")
        
        # Generate detailed report
        report = self.generate_detailed_report()
        with open("duplicate_analysis_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save results
        self.save_analysis_results()
        
        print(f"\n✅ Analysis complete! Check duplicate_analysis_report.md for details.")
        return True


def main():
    """Main entry point for duplicate analysis."""
    parser = argparse.ArgumentParser(description="Analyze GitHub repositories for duplicates")
    parser.add_argument("--data-dir", default="github_library_enhanced",
                        help="Directory containing repository data")
    parser.add_argument("--output", default="duplicate_analysis_results.json",
                        help="Output file for analysis results")
    
    args = parser.parse_args()
    
    analyzer = DuplicateAnalyzer(args.data_dir)
    success = analyzer.run()
    
    if success:
        print("✅ Duplicate analysis completed successfully!")
        return 0
    else:
        print("❌ Duplicate analysis failed!")
        return 1


if __name__ == "__main__":
    main() 