#!/usr/bin/env python3
"""
OOP Structure Checker for Agent Policy Enforcement
Enforces class-based programming and Single Responsibility Principle.
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class OOPChecker:
    """Enforces OOP principles for agent-generated code."""
    
    def __init__(self):
        self.violations = []
        self.stats = {
            'total_files': 0,
            'files_with_classes': 0,
            'files_without_classes': 0,
            'total_classes': 0,
            'total_functions': 0,
            'standalone_functions': 0
        }
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze OOP structure of a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            file_stats = {
                'classes': [],
                'standalone_functions': [],
                'has_classes': False,
                'violations': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    file_stats['has_classes'] = True
                    class_info = self.analyze_class(node)
                    file_stats['classes'].append(class_info)
                    
                    # Check for SRP violations
                    if class_info['responsibilities'] > 3:
                        file_stats['violations'].append({
                            'type': 'srp_violation',
                            'class': node.name,
                            'responsibilities': class_info['responsibilities'],
                            'line': node.lineno,
                            'message': f"Class '{node.name}' has {class_info['responsibilities']} responsibilities (max: 3)"
                        })
                    
                    # Check for large classes
                    if class_info['methods'] > 10:
                        file_stats['violations'].append({
                            'type': 'large_class',
                            'class': node.name,
                            'methods': class_info['methods'],
                            'line': node.lineno,
                            'message': f"Class '{node.name}' has {class_info['methods']} methods (max: 10)"
                        })
                
                elif isinstance(node, ast.FunctionDef):
                    # Check if function is not inside a class
                    if not self.is_inside_class(node, tree):
                        file_stats['standalone_functions'].append({
                            'name': node.name,
                            'line': node.lineno
                        })
            
            # Check for standalone functions (should be in classes)
            if file_stats['standalone_functions'] and not file_stats['has_classes']:
                for func in file_stats['standalone_functions']:
                    file_stats['violations'].append({
                        'type': 'standalone_function',
                        'function': func['name'],
                        'line': func['line'],
                        'message': f"Function '{func['name']}' should be in a class"
                    })
            
            return file_stats
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {'classes': [], 'standalone_functions': [], 'has_classes': False, 'violations': []}
    
    def analyze_class(self, class_node: ast.ClassDef) -> Dict:
        """Analyze a class for OOP principles."""
        responsibilities = 0
        methods = []
        
        # Count methods and analyze responsibilities
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
                
                # Simple responsibility detection based on method names
                method_name = item.name.lower()
                if any(keyword in method_name for keyword in ['get', 'set', 'validate', 'parse']):
                    responsibilities += 1
                elif any(keyword in method_name for keyword in ['save', 'load', 'store', 'retrieve']):
                    responsibilities += 1
                elif any(keyword in method_name for keyword in ['format', 'display', 'render', 'show']):
                    responsibilities += 1
                elif any(keyword in method_name for keyword in ['process', 'handle', 'execute', 'run']):
                    responsibilities += 1
                elif any(keyword in method_name for keyword in ['connect', 'send', 'receive', 'network']):
                    responsibilities += 1
                else:
                    responsibilities += 1
        
        return {
            'name': class_node.name,
            'methods': len(methods),
            'method_names': methods,
            'responsibilities': responsibilities,
            'line': class_node.lineno
        }
    
    def is_inside_class(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is defined inside a class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == func_node.name:
                        return True
        return False
    
    def check_directory(self, directory: Path) -> List[Dict]:
        """Check all Python files in directory."""
        all_violations = []
        
        for file_path in directory.rglob("*.py"):
            # Skip test files and virtual environments
            if any(part in str(file_path) for part in ['test', 'tests', '__pycache__', 'venv', '.venv']):
                continue
            
            file_stats = self.analyze_file(file_path)
            
            if file_stats['has_classes']:
                self.stats['files_with_classes'] += 1
            else:
                self.stats['files_without_classes'] += 1
            
            self.stats['total_files'] += 1
            self.stats['total_classes'] += len(file_stats['classes'])
            self.stats['standalone_functions'] += len(file_stats['standalone_functions'])
            
            # Add violations with file context
            for violation in file_stats['violations']:
                violation['file'] = str(file_path)
                all_violations.append(violation)
        
        return all_violations
    
    def run(self, paths: List[str]) -> int:
        """Run OOP check on specified paths."""
        all_violations = []
        
        for path_str in paths:
            path = Path(path_str)
            if path.is_file():
                file_stats = self.analyze_file(path)
                all_violations.extend(file_stats['violations'])
            elif path.is_dir():
                all_violations.extend(self.check_directory(path))
        
        # Report violations
        if all_violations:
            print("❌ OOP STRUCTURE VIOLATIONS DETECTED:")
            print("=" * 60)
            
            # Group violations by type
            srp_violations = [v for v in all_violations if v['type'] == 'srp_violation']
            large_classes = [v for v in all_violations if v['type'] == 'large_class']
            standalone_funcs = [v for v in all_violations if v['type'] == 'standalone_function']
            
            if srp_violations:
                print("🔧 SRP VIOLATIONS:")
                for violation in srp_violations:
                    print(f"   📁 {violation['file']}:{violation['line']}")
                    print(f"   {violation['message']}")
                    print()
            
            if large_classes:
                print("🔧 LARGE CLASSES:")
                for violation in large_classes:
                    print(f"   📁 {violation['file']}:{violation['line']}")
                    print(f"   {violation['message']}")
                    print()
            
            if standalone_funcs:
                print("🔧 STANDALONE FUNCTIONS:")
                for violation in standalone_funcs:
                    print(f"   📁 {violation['file']}:{violation['line']}")
                    print(f"   {violation['message']}")
                    print()
            
            print("🔧 RECOMMENDATIONS:")
            print("- Ensure all code is class-based")
            print("- Follow Single Responsibility Principle")
            print("- Keep classes focused and small")
            print("- Group related functions into classes")
            print("- Use composition over inheritance")
            
            return 1
        
        # Print statistics
        print("✅ OOP Structure Analysis Complete!")
        print(f"📊 Statistics:")
        print(f"   Total files: {self.stats['total_files']}")
        print(f"   Files with classes: {self.stats['files_with_classes']}")
        print(f"   Files without classes: {self.stats['files_without_classes']}")
        print(f"   Total classes: {self.stats['total_classes']}")
        print(f"   Standalone functions: {self.stats['standalone_functions']}")
        
        if self.stats['files_without_classes'] > 0:
            print(f"⚠️  Warning: {self.stats['files_without_classes']} files don't use classes")
            return 1
        
        return 0


def main():
    """Main entry point for OOP checker."""
    parser = argparse.ArgumentParser(description="Check OOP structure")
    parser.add_argument("paths", nargs="+", help="Files or directories to check")
    
    args = parser.parse_args()
    
    checker = OOPChecker()
    exit_code = checker.run(args.paths)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 