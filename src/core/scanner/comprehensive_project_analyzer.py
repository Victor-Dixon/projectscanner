#!/usr/bin/env python3
"""
Comprehensive Project Analyzer
Provides deep, meaningful analysis of projects using existing data and enhanced algorithms.
"""

import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict, Counter
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveProjectAnalyzer:
    """Comprehensive project analysis engine that captures project essence."""
    
    def __init__(self, data_dir: str = "github_library_enhanced"):
        self.data_dir = Path(data_dir)
        self.analysis_results = {}
        
    def analyze_all_projects(self) -> Dict:
        """Analyze all projects in the library with comprehensive analysis."""
        logger.info(f"🔍 Starting comprehensive analysis of projects in {self.data_dir}")
        
        # Load existing data
        summary_file = self.data_dir / "enhanced_library_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            # Analyze each repository
            for repo in summary_data.get('repositories', []):
                repo_id = repo['id']
                self.analyze_single_project(repo_id, repo)
        
        # Generate comprehensive summary
        comprehensive_summary = self.generate_comprehensive_summary()
        
        # Save results
        self.save_comprehensive_analysis(comprehensive_summary)
        
        return comprehensive_summary
    
    def analyze_single_project(self, repo_id: str, repo_data: Dict) -> Dict:
        """Analyze a single project comprehensively."""
        logger.info(f"📊 Analyzing {repo_id}")
        
        analysis = {
            'project_id': repo_id,
            'basic_info': repo_data,
            'deep_analysis': {},
            'business_analysis': {},
            'technical_analysis': {},
            'essence_summary': {}
        }
        
        # Get detailed analysis files
        repo_dir = self.data_dir / repo_id
        if repo_dir.exists():
            # Load existing analysis files
            analysis_files = list(repo_dir.glob("*_analysis.json"))
            context_files = list(repo_dir.glob("*_context*.json"))
            
            # Deep analysis
            analysis['deep_analysis'] = self.perform_deep_analysis(repo_dir, analysis_files, context_files)
            
            # Business analysis
            analysis['business_analysis'] = self.analyze_business_aspects(repo_data, analysis['deep_analysis'])
            
            # Technical analysis
            analysis['technical_analysis'] = self.analyze_technical_aspects(analysis['deep_analysis'])
            
            # Generate essence summary
            analysis['essence_summary'] = self.generate_project_essence(analysis)
        
        self.analysis_results[repo_id] = analysis
        return analysis
    
    def perform_deep_analysis(self, repo_dir: Path, analysis_files: List[Path], context_files: List[Path]) -> Dict:
        """Perform deep analysis using existing data."""
        deep_analysis = {
            'code_structure': {},
            'functionality': {},
            'dependencies': {},
            'patterns': {},
            'content_analysis': {}
        }
        
        # Analyze code structure from existing analysis files
        for analysis_file in analysis_files:
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    file_analysis = json.load(f)
                
                deep_analysis['code_structure'] = self.analyze_code_structure(file_analysis)
                deep_analysis['functionality'] = self.analyze_functionality(file_analysis)
                deep_analysis['patterns'] = self.analyze_code_patterns(file_analysis)
                
            except Exception as e:
                logger.debug(f"Could not analyze {analysis_file}: {e}")
        
        # Analyze context files for additional insights
        for context_file in context_files:
            try:
                with open(context_file, 'r', encoding='utf-8') as f:
                    context_data = json.load(f)
                
                deep_analysis['content_analysis'] = self.analyze_content_context(context_data)
                
            except Exception as e:
                logger.debug(f"Could not analyze context {context_file}: {e}")
        
        return deep_analysis
    
    def analyze_code_structure(self, file_analysis: Dict) -> Dict:
        """Analyze code structure from file analysis."""
        structure = {
            'total_files': len(file_analysis),
            'file_types': Counter(),
            'functions': [],
            'classes': [],
            'complexity_distribution': {},
            'language_breakdown': Counter()
        }
        
        total_functions = 0
        total_classes = 0
        complexity_scores = []
        
        for file_path, file_data in file_analysis.items():
            # File type analysis
            ext = file_data.get('language', 'unknown')
            structure['file_types'][ext] += 1
            
            # Function analysis
            functions = file_data.get('functions', [])
            total_functions += len(functions)
            structure['functions'].extend(functions)
            
            # Class analysis
            classes = file_data.get('classes', {})
            total_classes += len(classes)
            structure['classes'].extend(list(classes.keys()))
            
            # Complexity analysis
            complexity = file_data.get('complexity', 0)
            complexity_scores.append(complexity)
        
        # Complexity distribution
        if complexity_scores:
            structure['complexity_distribution'] = {
                'average': sum(complexity_scores) / len(complexity_scores),
                'max': max(complexity_scores),
                'min': min(complexity_scores),
                'high_complexity_files': len([c for c in complexity_scores if c > 10])
            }
        
        structure['total_functions'] = total_functions
        structure['total_classes'] = total_classes
        
        return structure
    
    def analyze_functionality(self, file_analysis: Dict) -> Dict:
        """Analyze functionality from code analysis."""
        functionality = {
            'primary_functions': [],
            'api_endpoints': [],
            'data_operations': [],
            'business_logic': [],
            'utility_functions': []
        }
        
        for file_path, file_data in file_analysis.items():
            functions = file_data.get('functions', [])
            
            for func_name in functions:
                func_lower = func_name.lower()
                
                # Categorize functions
                if any(keyword in func_lower for keyword in ['api', 'route', 'endpoint', 'get', 'post']):
                    functionality['api_endpoints'].append(func_name)
                elif any(keyword in func_lower for keyword in ['process', 'analyze', 'calculate', 'compute']):
                    functionality['data_operations'].append(func_name)
                elif any(keyword in func_lower for keyword in ['validate', 'check', 'verify', 'business']):
                    functionality['business_logic'].append(func_name)
                elif any(keyword in func_lower for keyword in ['util', 'helper', 'format', 'parse']):
                    functionality['utility_functions'].append(func_name)
                else:
                    functionality['primary_functions'].append(func_name)
        
        return functionality
    
    def analyze_code_patterns(self, file_analysis: Dict) -> Dict:
        """Analyze code patterns and architectural decisions."""
        patterns = {
            'design_patterns': [],
            'architectural_style': 'unknown',
            'code_organization': {},
            'testing_patterns': [],
            'documentation_patterns': []
        }
        
        # Analyze file organization
        file_types = Counter()
        for file_path, file_data in file_analysis.items():
            ext = file_data.get('language', '')
            file_types[ext] += 1
        
        patterns['code_organization'] = dict(file_types)
        
        # Detect architectural patterns
        total_files = len(file_analysis)
        python_files = sum(1 for f in file_analysis.values() if f.get('language') == '.py')
        
        if python_files > 0:
            # Analyze class patterns
            total_classes = sum(len(f.get('classes', {})) for f in file_analysis.values())
            
            if total_classes > 0:
                patterns['architectural_style'] = 'Object-Oriented'
                patterns['design_patterns'].append('Class-based architecture')
            else:
                patterns['architectural_style'] = 'Functional/Procedural'
                patterns['design_patterns'].append('Function-based architecture')
        
        # Detect testing patterns
        test_files = [f for f in file_analysis.keys() if 'test' in f.lower()]
        if test_files:
            patterns['testing_patterns'].append('Unit testing')
        
        return patterns
    
    def analyze_content_context(self, context_data: Dict) -> Dict:
        """Analyze content context for additional insights."""
        content_analysis = {
            'project_description': '',
            'key_features': [],
            'technologies': [],
            'use_cases': [],
            'target_audience': ''
        }
        
        # Extract information from context data
        if isinstance(context_data, dict):
            # Look for project description
            for key in ['description', 'summary', 'overview', 'project_description']:
                if key in context_data and context_data[key]:
                    content_analysis['project_description'] = str(context_data[key])
                    break
            
            # Extract key features
            if 'features' in context_data:
                features = context_data['features']
                if isinstance(features, list):
                    content_analysis['key_features'] = features
                elif isinstance(features, str):
                    content_analysis['key_features'] = [features]
            
            # Extract technologies
            if 'technologies' in context_data:
                techs = context_data['technologies']
                if isinstance(techs, list):
                    content_analysis['technologies'] = techs
                elif isinstance(techs, str):
                    content_analysis['technologies'] = [techs]
        
        return content_analysis
    
    def analyze_business_aspects(self, repo_data: Dict, deep_analysis: Dict) -> Dict:
        """Analyze business aspects of the project."""
        business_analysis = {
            'business_domain': '',
            'value_proposition': '',
            'target_users': '',
            'monetization_potential': 'unknown',
            'market_fit': 'unknown',
            'competitive_advantages': [],
            'business_metrics': {}
        }
        
        # Analyze from repository data
        name = repo_data.get('name', '').lower()
        description = repo_data.get('description', '').lower()
        
        # Detect business domain
        domain_keywords = {
            'trading': ['trading', 'stock', 'portfolio', 'investment', 'finance', 'market'],
            'web_app': ['web', 'app', 'api', 'server', 'website'],
            'automation': ['bot', 'automation', 'script', 'workflow'],
            'data_analysis': ['data', 'analysis', 'analytics', 'reporting'],
            'ai_ml': ['ai', 'machine learning', 'neural', 'model', 'prediction']
        }
        
        combined_text = f"{name} {description}"
        for domain, keywords in domain_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                business_analysis['business_domain'] = domain
                break
        
        # Analyze functionality for business value
        if 'functionality' in deep_analysis:
            functionality = deep_analysis['functionality']
            
            # Assess monetization potential
            if functionality.get('api_endpoints'):
                business_analysis['monetization_potential'] = 'high'
                business_analysis['competitive_advantages'].append('API capabilities')
            
            if functionality.get('data_operations'):
                business_analysis['monetization_potential'] = 'medium'
                business_analysis['competitive_advantages'].append('Data processing capabilities')
        
        # Analyze from content context
        if 'content_analysis' in deep_analysis:
            content = deep_analysis['content_analysis']
            if content.get('project_description'):
                business_analysis['value_proposition'] = content['project_description']
            
            if content.get('key_features'):
                business_analysis['competitive_advantages'].extend(content['key_features'])
        
        return business_analysis
    
    def analyze_technical_aspects(self, deep_analysis: Dict) -> Dict:
        """Analyze technical aspects of the project."""
        technical_analysis = {
            'technology_stack': [],
            'architecture_quality': 'unknown',
            'code_quality': 'unknown',
            'maintainability': 'unknown',
            'scalability': 'unknown',
            'security_considerations': [],
            'performance_indicators': {},
            'technical_debt': []
        }
        
        # Analyze code structure
        if 'code_structure' in deep_analysis:
            structure = deep_analysis['code_structure']
            
            # Assess code quality
            total_files = structure.get('total_files', 0)
            total_functions = structure.get('total_functions', 0)
            total_classes = structure.get('total_classes', 0)
            
            if total_files > 0:
                functions_per_file = total_functions / total_files
                classes_per_file = total_classes / total_files
                
                if functions_per_file > 10:
                    technical_analysis['code_quality'] = 'needs_refactoring'
                    technical_analysis['technical_debt'].append('High function density per file')
                elif functions_per_file > 5:
                    technical_analysis['code_quality'] = 'moderate'
                else:
                    technical_analysis['code_quality'] = 'good'
                
                if classes_per_file > 0:
                    technical_analysis['architecture_quality'] = 'object_oriented'
                else:
                    technical_analysis['architecture_quality'] = 'functional'
            
            # Analyze complexity
            complexity = structure.get('complexity_distribution', {})
            if complexity.get('high_complexity_files', 0) > 0:
                technical_analysis['technical_debt'].append('High complexity files detected')
                technical_analysis['maintainability'] = 'needs_improvement'
            else:
                technical_analysis['maintainability'] = 'good'
        
        # Analyze patterns
        if 'patterns' in deep_analysis:
            patterns = deep_analysis['patterns']
            
            if patterns.get('testing_patterns'):
                technical_analysis['code_quality'] = 'good'
            else:
                technical_analysis['technical_debt'].append('No testing detected')
        
        return technical_analysis
    
    def generate_project_essence(self, analysis: Dict) -> Dict:
        """Generate comprehensive project essence summary."""
        essence = {
            'summary': '',
            'primary_purpose': '',
            'key_technologies': [],
            'target_users': '',
            'business_value': '',
            'technical_complexity': '',
            'deployment_type': '',
            'integration_points': [],
            'data_handling': '',
            'security_considerations': '',
            'maintenance_status': '',
            'recommendations': []
        }
        
        # Extract from business analysis
        if 'business_analysis' in analysis:
            business = analysis['business_analysis']
            essence['primary_purpose'] = business.get('business_domain', 'Unknown')
            essence['business_value'] = business.get('value_proposition', 'Not specified')
            essence['target_users'] = business.get('target_users', 'General users')
        
        # Extract from technical analysis
        if 'technical_analysis' in analysis:
            technical = analysis['technical_analysis']
            essence['technical_complexity'] = technical.get('code_quality', 'unknown')
            essence['maintenance_status'] = technical.get('maintainability', 'unknown')
            
            # Generate recommendations
            if technical.get('technical_debt'):
                essence['recommendations'].extend(technical['technical_debt'])
        
        # Extract from deep analysis
        if 'deep_analysis' in analysis:
            deep = analysis['deep_analysis']
            
            # Technologies from content analysis
            if 'content_analysis' in deep:
                content = deep['content_analysis']
                essence['key_technologies'] = content.get('technologies', [])
            
            # Functionality summary
            if 'functionality' in deep:
                functionality = deep['functionality']
                if functionality.get('api_endpoints'):
                    essence['deployment_type'] = 'Web API'
                elif functionality.get('data_operations'):
                    essence['deployment_type'] = 'Data Processing'
                else:
                    essence['deployment_type'] = 'Application'
        
        # Generate comprehensive summary
        summary_parts = []
        
        if essence['primary_purpose']:
            summary_parts.append(f"This is a {essence['primary_purpose']} project")
        
        if essence['deployment_type']:
            summary_parts.append(f"deployed as {essence['deployment_type']}")
        
        if essence['key_technologies']:
            summary_parts.append(f"using {', '.join(essence['key_technologies'][:3])}")
        
        if essence['technical_complexity']:
            summary_parts.append(f"({essence['technical_complexity']} code quality)")
        
        essence['summary'] = ' '.join(summary_parts) if summary_parts else 'Project analysis complete'
        
        return essence
    
    def generate_comprehensive_summary(self) -> Dict:
        """Generate comprehensive summary of all projects."""
        summary = {
            'total_projects': len(self.analysis_results),
            'analysis_timestamp': datetime.now().isoformat(),
            'project_categories': {},
            'technology_distribution': {},
            'quality_distribution': {},
            'business_domains': {},
            'recommendations': [],
            'detailed_analyses': self.analysis_results
        }
        
        # Analyze all projects
        categories = Counter()
        technologies = Counter()
        quality_levels = Counter()
        business_domains = Counter()
        
        for repo_id, analysis in self.analysis_results.items():
            # Project categories
            if 'essence_summary' in analysis:
                essence = analysis['essence_summary']
                primary_purpose = essence.get('primary_purpose', 'Unknown')
                categories[primary_purpose] += 1
                
                # Technologies
                techs = essence.get('key_technologies', [])
                for tech in techs:
                    technologies[tech] += 1
                
                # Quality levels
                quality = essence.get('technical_complexity', 'unknown')
                quality_levels[quality] += 1
            
            # Business domains
            if 'business_analysis' in analysis:
                business = analysis['business_analysis']
                domain = business.get('business_domain', 'Unknown')
                business_domains[domain] += 1
        
        summary['project_categories'] = dict(categories)
        summary['technology_distribution'] = dict(technologies.most_common(20))
        summary['quality_distribution'] = dict(quality_levels)
        summary['business_domains'] = dict(business_domains)
        
        # Generate portfolio recommendations
        summary['recommendations'] = self.generate_portfolio_recommendations()
        
        return summary
    
    def generate_portfolio_recommendations(self) -> List[str]:
        """Generate portfolio-level recommendations."""
        recommendations = []
        
        # Analyze portfolio composition
        total_projects = len(self.analysis_results)
        
        if total_projects > 50:
            recommendations.append("Consider consolidating similar projects to reduce maintenance overhead")
        
        # Analyze quality distribution
        quality_distribution = {}
        for analysis in self.analysis_results.values():
            if 'essence_summary' in analysis:
                quality = analysis['essence_summary'].get('technical_complexity', 'unknown')
                quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
        
        low_quality_count = quality_distribution.get('needs_refactoring', 0)
        if low_quality_count > total_projects * 0.3:
            recommendations.append("Focus on code quality improvements across the portfolio")
        
        # Analyze business domain concentration
        domain_distribution = {}
        for analysis in self.analysis_results.values():
            if 'business_analysis' in analysis:
                domain = analysis['business_analysis'].get('business_domain', 'Unknown')
                domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        if len(domain_distribution) < 3:
            recommendations.append("Consider diversifying into new business domains")
        
        return recommendations
    
    def save_comprehensive_analysis(self, summary: Dict):
        """Save comprehensive analysis results."""
        output_file = self.data_dir / "comprehensive_analysis_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Comprehensive analysis saved to {output_file}")
        
        # Print summary
        print(f"\n📊 COMPREHENSIVE ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total projects analyzed: {summary['total_projects']}")
        print(f"Project categories: {len(summary['project_categories'])}")
        print(f"Top technologies: {', '.join(list(summary['technology_distribution'].keys())[:5])}")
        print(f"Business domains: {dict(summary['business_domains'])}")
        print(f"Quality distribution: {dict(summary['quality_distribution'])}")
        
        if summary['recommendations']:
            print(f"\n💡 PORTFOLIO RECOMMENDATIONS:")
            for rec in summary['recommendations']:
                print(f"  • {rec}")


def main():
    """Main entry point for comprehensive project analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Project Analyzer")
    parser.add_argument("--data-dir", default="github_library_enhanced",
                        help="Directory containing project data")
    
    args = parser.parse_args()
    
    analyzer = ComprehensiveProjectAnalyzer(args.data_dir)
    summary = analyzer.analyze_all_projects()
    
    print(f"\n✅ Comprehensive analysis complete!")


if __name__ == "__main__":
    main() 