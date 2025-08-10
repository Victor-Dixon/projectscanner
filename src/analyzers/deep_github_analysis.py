#!/usr/bin/env python3
"""
Deep GitHub Library Analysis - Extract detailed insights about code patterns, architecture, and development evolution.
"""

import json
import sys
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import statistics

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def deep_analyze_github_library():
    """Perform deep analysis of the GitHub library."""
    library_file = Path("github_library_enhanced/github_library_enhanced.json")
    
    if not library_file.exists():
        print("❌ GitHub library file not found. Run the scanner first.")
        return
    
    print("🔬 Deep GitHub Library Analysis")
    print("=" * 60)
    
    # Load the library data
    with library_file.open('r', encoding='utf-8') as f:
        library_data = json.load(f)
    
    # Perform deep analysis
    insights = extract_deep_insights(library_data)
    
    # Display comprehensive insights
    display_deep_insights(insights)
    
    return insights


def extract_deep_insights(library_data):
    """Extract deep insights from the library data."""
    insights = {
        'total_repos': len(library_data),
        'total_files': 0,
        'total_classes': 0,
        'total_functions': 0,
        'total_lines': 0,
        'file_counts': [],
        'languages': Counter(),
        'file_types': Counter(),
        'complexity_scores': [],
        'architecture_patterns': defaultdict(int),
        'design_patterns': defaultdict(int),
        'tech_stack': defaultdict(int),
        'development_evolution': defaultdict(int),
        'code_quality_metrics': defaultdict(list),
        'project_categories': defaultdict(int),
        'largest_repos': [],
        'most_complex_repos': [],
        'ai_ml_projects': [],
        'automation_projects': [],
        'gaming_projects': [],
        'financial_projects': [],
        'social_media_projects': [],
        'os_system_projects': [],
        'web_projects': [],
        'api_projects': [],
        'database_projects': [],
        'testing_projects': [],
        'documentation_projects': [],
        'class_analysis': defaultdict(list),
        'function_analysis': defaultdict(list),
        'import_patterns': defaultdict(int),
        'framework_usage': defaultdict(int),
        'library_usage': defaultdict(int),
        'development_tools': defaultdict(int),
        'deployment_patterns': defaultdict(int),
        'security_patterns': defaultdict(int),
        'performance_patterns': defaultdict(int),
        'scalability_patterns': defaultdict(int),
        'maintainability_patterns': defaultdict(int),
        'innovation_patterns': defaultdict(int)
    }
    
    # Keywords for deep categorization
    ai_ml_keywords = ['ai', 'ml', 'machine', 'learning', 'neural', 'lstm', 'gpt', 'automation', 'agent', 'model', 'predict', 'classify', 'regression', 'clustering']
    automation_keywords = ['automation', 'bot', 'script', 'auto', 'workflow', 'scheduler', 'cron', 'task', 'job']
    gaming_keywords = ['game', 'rpg', 'ttrpg', 'tactics', 'swarm', 'troop', 'player', 'score', 'level', 'quest', 'character']
    financial_keywords = ['stock', 'trading', 'portfolio', 'financial', 'market', 'price', 'currency', 'crypto', 'investment']
    social_keywords = ['social', 'media', 'twitter', 'youtube', 'stream', 'post', 'share', 'like', 'comment']
    os_keywords = ['os', 'operating', 'system', 'kernel', 'process', 'thread', 'memory', 'file', 'device']
    web_keywords = ['web', 'http', 'api', 'rest', 'server', 'client', 'frontend', 'backend', 'html', 'css', 'js']
    api_keywords = ['api', 'rest', 'endpoint', 'route', 'controller', 'service', 'microservice']
    db_keywords = ['database', 'sql', 'nosql', 'mongo', 'redis', 'postgres', 'mysql', 'db']
    test_keywords = ['test', 'unit', 'integration', 'pytest', 'unittest', 'mock', 'coverage']
    doc_keywords = ['readme', 'docs', 'documentation', 'guide', 'tutorial', 'wiki']
    
    # Framework and library patterns
    frameworks = {
        'flask': ['flask', 'app.route', 'blueprint'],
        'django': ['django', 'models.py', 'views.py', 'urls.py'],
        'fastapi': ['fastapi', 'uvicorn', 'pydantic'],
        'pyqt': ['pyqt', 'qtwidgets', 'qmainwindow'],
        'tkinter': ['tkinter', 'tk.', 'root.mainloop'],
        'selenium': ['selenium', 'webdriver', 'driver.get'],
        'requests': ['requests', 'get(', 'post('],
        'beautifulsoup': ['beautifulsoup', 'bs4', 'soup.find'],
        'pandas': ['pandas', 'pd.', 'dataframe'],
        'numpy': ['numpy', 'np.', 'array'],
        'matplotlib': ['matplotlib', 'plt.', 'plot'],
        'scikit': ['sklearn', 'scikit', 'model.fit'],
        'tensorflow': ['tensorflow', 'tf.', 'keras'],
        'pytorch': ['torch', 'pytorch', 'nn.'],
        'openai': ['openai', 'gpt', 'chatgpt'],
        'discord': ['discord', 'discord.py', 'bot.run'],
        'telegram': ['telegram', 'telebot', 'bot.send'],
        'sqlalchemy': ['sqlalchemy', 'orm', 'session'],
        'sqlite': ['sqlite', 'sqlite3'],
        'postgres': ['postgres', 'psycopg2'],
        'redis': ['redis', 'redis-py'],
        'celery': ['celery', 'task', 'worker'],
        'asyncio': ['asyncio', 'async', 'await'],
        'threading': ['threading', 'thread', 'lock'],
        'multiprocessing': ['multiprocessing', 'process', 'pool'],
        'logging': ['logging', 'logger', 'log'],
        'config': ['config', 'settings', 'env'],
        'argparse': ['argparse', 'argumentparser'],
        'click': ['click', '@click.command'],
        'typer': ['typer', 'typer.run'],
        'pydantic': ['pydantic', 'basemodel'],
        'dataclasses': ['dataclass', '@dataclass'],
        'enum': ['enum', 'enumclass'],
        'abc': ['abc', 'abstractmethod'],
        'pathlib': ['pathlib', 'path'],
        'shutil': ['shutil', 'copy', 'move'],
        'subprocess': ['subprocess', 'run(', 'popen'],
        'os': ['os.', 'os.path'],
        'sys': ['sys.', 'sys.path'],
        'json': ['json', 'json.loads', 'json.dumps'],
        'yaml': ['yaml', 'yaml.load', 'yaml.dump'],
        'toml': ['toml', 'tomllib'],
        'csv': ['csv', 'csv.reader', 'csv.writer'],
        'pickle': ['pickle', 'pickle.dump', 'pickle.load'],
        'hashlib': ['hashlib', 'md5', 'sha'],
        'cryptography': ['cryptography', 'fernet'],
        'jwt': ['jwt', 'pyjwt'],
        'oauth': ['oauth', 'oauthlib'],
        'jwt': ['jwt', 'pyjwt'],
        'bcrypt': ['bcrypt', 'hashpw'],
        'passlib': ['passlib', 'hash'],
        'pytest': ['pytest', 'test_', 'fixture'],
        'unittest': ['unittest', 'testcase'],
        'mock': ['mock', 'patch', 'magicmock'],
        'coverage': ['coverage', 'coverage.py'],
        'black': ['black', 'format'],
        'flake8': ['flake8', 'lint'],
        'mypy': ['mypy', 'type'],
        'isort': ['isort', 'sort'],
        'pre-commit': ['pre-commit', 'hooks'],
        'docker': ['docker', 'dockerfile', 'docker-compose'],
        'kubernetes': ['kubernetes', 'k8s', 'pod'],
        'aws': ['boto3', 'aws', 's3', 'ec2'],
        'gcp': ['google.cloud', 'gcp', 'gcs'],
        'azure': ['azure', 'microsoft'],
        'heroku': ['heroku', 'procfile'],
        'vercel': ['vercel', 'vercel.json'],
        'netlify': ['netlify', 'netlify.toml'],
        'github': ['github', 'actions', 'workflow'],
        'gitlab': ['gitlab', 'ci', 'cd'],
        'jenkins': ['jenkins', 'pipeline'],
        'travis': ['travis', '.travis.yml'],
        'circleci': ['circleci', 'config.yml'],
        'github_actions': ['github', 'actions', 'workflow'],
        'gitlab_ci': ['gitlab', 'ci', 'cd'],
        'jenkins': ['jenkins', 'pipeline'],
        'travis': ['travis', '.travis.yml'],
        'circleci': ['circleci', 'config.yml']
    }
    
    for repo_id, repo_info in library_data.items():
        repo_name = repo_info.get('repo_name', '').lower()
        description = (repo_info.get('description') or '').lower()
        language = repo_info.get('language', 'Unknown')
        file_count = repo_info.get('file_count', 0)
        stars = repo_info.get('stars', 0)
        created_at = repo_info.get('created_at', '')
        analysis_data = repo_info.get('analysis_data', {})
        
        # Count files and complexity
        insights['total_files'] += file_count
        insights['file_counts'].append(file_count)
        
        # Count languages
        insights['languages'][language] += 1
        
        # Track largest repos
        insights['largest_repos'].append({
            'name': repo_info.get('repo_name', repo_id),
            'files': file_count,
            'stars': stars,
            'language': language,
            'description': repo_info.get('description', ''),
            'url': repo_info.get('repo_url', '')
        })
        
        # Analyze each file in the repository
        total_complexity = 0
        total_classes = 0
        total_functions = 0
        total_lines = 0
        
        for file_path, file_info in analysis_data.items():
            # Count classes and functions
            if 'classes' in file_info:
                total_classes += len(file_info['classes'])
                for class_name, class_info in file_info['classes'].items():
                    insights['class_analysis'][class_name].append({
                        'repo': repo_name,
                        'file': file_path,
                        'methods': len(class_info.get('methods', [])),
                        'maturity': class_info.get('maturity', 'Unknown'),
                        'agent_type': class_info.get('agent_type', 'Unknown')
                    })
            
            if 'functions' in file_info:
                total_functions += len(file_info['functions'])
                for func_name in file_info['functions']:
                    insights['function_analysis'][func_name].append({
                        'repo': repo_name,
                        'file': file_path
                    })
            
            # Track complexity
            complexity = file_info.get('complexity', 0)
            total_complexity += complexity
            insights['complexity_scores'].append(complexity)
            
            # Analyze file types
            file_ext = Path(file_path).suffix.lower()
            insights['file_types'][file_ext] += 1
            
            # Analyze lint issues for code quality
            lint_issues = file_info.get('lint', [])
            insights['code_quality_metrics']['lint_issues'].extend(lint_issues)
            
            # Detect architecture patterns
            if 'classes' in file_info and file_info['classes']:
                insights['architecture_patterns']['object_oriented'] += 1
            if len(file_info.get('functions', [])) > 5:
                insights['architecture_patterns']['functional'] += 1
            if 'routes' in file_info and file_info['routes']:
                insights['architecture_patterns']['web_api'] += 1
            
            # Detect design patterns
            class_names = [name.lower() for name in file_info.get('classes', {}).keys()]
            if any('factory' in name for name in class_names):
                insights['design_patterns']['factory'] += 1
            if any('singleton' in name for name in class_names):
                insights['design_patterns']['singleton'] += 1
            if any('observer' in name for name in class_names):
                insights['design_patterns']['observer'] += 1
            if any('strategy' in name for name in class_names):
                insights['design_patterns']['strategy'] += 1
        
        # Update totals
        insights['total_classes'] += total_classes
        insights['total_functions'] += total_functions
        
        # Categorize projects
        combined_text = f"{repo_name} {description}"
        
        if any(keyword in combined_text for keyword in ai_ml_keywords):
            insights['ai_ml_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['AI/ML'] += 1
            
        if any(keyword in combined_text for keyword in automation_keywords):
            insights['automation_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Automation'] += 1
            
        if any(keyword in combined_text for keyword in gaming_keywords):
            insights['gaming_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Gaming'] += 1
            
        if any(keyword in combined_text for keyword in financial_keywords):
            insights['financial_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Financial'] += 1
            
        if any(keyword in combined_text for keyword in social_keywords):
            insights['social_media_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Social Media'] += 1
            
        if any(keyword in combined_text for keyword in os_keywords):
            insights['os_system_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Operating Systems'] += 1
            
        if any(keyword in combined_text for keyword in web_keywords):
            insights['web_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Web Development'] += 1
            
        if any(keyword in combined_text for keyword in api_keywords):
            insights['api_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['API Development'] += 1
            
        if any(keyword in combined_text for keyword in db_keywords):
            insights['database_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Database'] += 1
            
        if any(keyword in combined_text for keyword in test_keywords):
            insights['testing_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Testing'] += 1
            
        if any(keyword in combined_text for keyword in doc_keywords):
            insights['documentation_projects'].append(repo_info.get('repo_name', repo_id))
            insights['project_categories']['Documentation'] += 1
        
        # Analyze framework and library usage
        for framework, patterns in frameworks.items():
            for pattern in patterns:
                if pattern in combined_text:
                    insights['framework_usage'][framework] += 1
                    break
        
        # Track most complex repos
        if total_complexity > 50:
            insights['most_complex_repos'].append({
                'name': repo_info.get('repo_name', repo_id),
                'complexity': total_complexity,
                'files': file_count,
                'classes': total_classes,
                'functions': total_functions
            })
    
    # Sort largest and most complex repos
    insights['largest_repos'].sort(key=lambda x: x['files'], reverse=True)
    insights['most_complex_repos'].sort(key=lambda x: x['complexity'], reverse=True)
    
    return insights


def display_deep_insights(insights):
    """Display comprehensive deep insights."""
    print(f"🔬 **Deep GitHub Portfolio Analysis**")
    print(f"Total Repositories: {insights['total_repos']}")
    print(f"Total Files Analyzed: {insights['total_files']:,}")
    print(f"Total Classes: {insights['total_classes']:,}")
    print(f"Total Functions: {insights['total_functions']:,}")
    print(f"Average Files per Repo: {insights['total_files'] / insights['total_repos']:.1f}")
    print(f"Average Classes per Repo: {insights['total_classes'] / insights['total_repos']:.1f}")
    print(f"Average Functions per Repo: {insights['total_functions'] / insights['total_repos']:.1f}")
    
    if insights['complexity_scores']:
        avg_complexity = statistics.mean(insights['complexity_scores'])
        print(f"Average Complexity Score: {avg_complexity:.1f}")
    
    print(f"\n🎯 **Technology Stack Analysis**")
    print(f"Primary Languages:")
    for lang, count in insights['languages'].most_common(5):
        print(f"  • {lang}: {count} repos")
    
    print(f"\n📁 **File Type Distribution**")
    for file_type, count in insights['file_types'].most_common(10):
        print(f"  • {file_type}: {count} files")
    
    print(f"\n🏗️ **Architecture Patterns**")
    for pattern, count in sorted(insights['architecture_patterns'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {pattern}: {count} instances")
    
    print(f"\n🎨 **Design Patterns**")
    for pattern, count in sorted(insights['design_patterns'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {pattern}: {count} instances")
    
    print(f"\n🔧 **Framework & Library Usage**")
    for framework, count in sorted(insights['framework_usage'].items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  • {framework}: {count} projects")
    
    print(f"\n📈 **Largest & Most Complex Projects**")
    print(f"Largest by File Count:")
    for i, repo in enumerate(insights['largest_repos'][:5], 1):
        print(f"  {i}. {repo['name']} ({repo['files']} files, {repo['stars']} stars)")
        if repo['description']:
            print(f"     Description: {repo['description'][:100]}...")
    
    print(f"\nMost Complex by Complexity Score:")
    for i, repo in enumerate(insights['most_complex_repos'][:5], 1):
        print(f"  {i}. {repo['name']} (Complexity: {repo['complexity']}, {repo['classes']} classes, {repo['functions']} functions)")
    
    print(f"\n🏗️ **Project Categories**")
    for category, count in sorted(insights['project_categories'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {category}: {count} projects")
    
    print(f"\n🤖 **AI/ML Projects** ({len(insights['ai_ml_projects'])})")
    for project in insights['ai_ml_projects']:
        print(f"  • {project}")
    
    print(f"\n⚙️ **Automation Projects** ({len(insights['automation_projects'])})")
    for project in insights['automation_projects']:
        print(f"  • {project}")
    
    print(f"\n🎮 **Gaming Projects** ({len(insights['gaming_projects'])})")
    for project in insights['gaming_projects']:
        print(f"  • {project}")
    
    print(f"\n💰 **Financial Projects** ({len(insights['financial_projects'])})")
    for project in insights['financial_projects']:
        print(f"  • {project}")
    
    print(f"\n💻 **Operating System Projects** ({len(insights['os_system_projects'])})")
    for project in insights['os_system_projects']:
        print(f"  • {project}")
    
    print(f"\n🌐 **Web Development Projects** ({len(insights['web_projects'])})")
    for project in insights['web_projects']:
        print(f"  • {project}")
    
    print(f"\n🔌 **API Development Projects** ({len(insights['api_projects'])})")
    for project in insights['api_projects']:
        print(f"  • {project}")
    
    print(f"\n🗄️ **Database Projects** ({len(insights['database_projects'])})")
    for project in insights['database_projects']:
        print(f"  • {project}")
    
    print(f"\n🧪 **Testing Projects** ({len(insights['testing_projects'])})")
    for project in insights['testing_projects']:
        print(f"  • {project}")
    
    print(f"\n📚 **Documentation Projects** ({len(insights['documentation_projects'])})")
    for project in insights['documentation_projects']:
        print(f"  • {project}")
    
    print(f"\n💡 **Deep Technical Insights**")
    
    # Code quality analysis
    if insights['code_quality_metrics']['lint_issues']:
        lint_counts = Counter(insights['code_quality_metrics']['lint_issues'])
        print(f"  • Most Common Code Issues:")
        for issue, count in lint_counts.most_common(5):
            print(f"    - {issue}: {count} occurrences")
    
    # Class analysis
    if insights['class_analysis']:
        most_common_classes = sorted(insights['class_analysis'].items(), 
                                   key=lambda x: len(x[1]), reverse=True)[:5]
        print(f"  • Most Common Class Names:")
        for class_name, instances in most_common_classes:
            print(f"    - {class_name}: {len(instances)} instances")
    
    # Function analysis
    if insights['function_analysis']:
        most_common_functions = sorted(insights['function_analysis'].items(), 
                                     key=lambda x: len(x[1]), reverse=True)[:5]
        print(f"  • Most Common Function Names:")
        for func_name, instances in most_common_functions:
            print(f"    - {func_name}: {len(instances)} instances")
    
    # Development patterns
    print(f"  • Architecture Focus:")
    for pattern, count in sorted(insights['architecture_patterns'].items(), key=lambda x: x[1], reverse=True)[:3]:
        percentage = (count / insights['total_repos']) * 100
        print(f"    - {pattern}: {percentage:.1f}% of projects")
    
    # Framework expertise
    print(f"  • Framework Expertise:")
    for framework, count in sorted(insights['framework_usage'].items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (count / insights['total_repos']) * 100
        print(f"    - {framework}: {percentage:.1f}% of projects")
    
    # Project diversity
    category_count = len(insights['project_categories'])
    print(f"  • Project Diversity: {category_count} different categories")
    
    # AI/ML focus
    ai_ml_percentage = (len(insights['ai_ml_projects']) / insights['total_repos']) * 100
    print(f"  • AI/ML Focus: {ai_ml_percentage:.1f}% of projects")
    
    # Complexity analysis
    if insights['complexity_scores']:
        high_complexity = sum(1 for score in insights['complexity_scores'] if score > 50)
        print(f"  • High Complexity Projects (>50): {high_complexity}")
        
        low_complexity = sum(1 for score in insights['complexity_scores'] if score < 10)
        print(f"  • Low Complexity Projects (<10): {low_complexity}")


def generate_deep_report():
    """Generate a comprehensive deep analysis report."""
    insights = deep_analyze_github_library()
    
    # Save insights to file
    report_file = Path("deep_github_insights_report.json")
    with report_file.open('w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2)
    
    print(f"\n📄 **Deep Analysis Report saved to: {report_file}**")


if __name__ == "__main__":
    generate_deep_report() 