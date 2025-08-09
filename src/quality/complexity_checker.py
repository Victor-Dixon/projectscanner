#!/usr/bin/env python3
"""
Cyclomatic Complexity Checker for Agent Policy Enforcement
Enforces complexity limits for functions and classes.
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ComplexityChecker:
    """Enforces cyclomatic complexity limits for agent-generated code."""
    
    def __init__(self, max_complexity: int = 10, class_max_complexity: int = 15):
        self.max_complexity = max_complexity
        self.class_max_complexity = class_max_complexity
        self.violations = []
    
    def calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of an AST node."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.Return):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Compare):
                complexity += len(child.ops) - 1
        
        return complexity
    
    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analyze complexity of all functions and classes in a file."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self.calculate_complexity(node)
                    if complexity > self.max_complexity:
                        violations.append({
                            'type': 'function',
                            'name': node.name,
                            'complexity': complexity,
                            'max_allowed': self.max_complexity,
                            'line': node.lineno,
                            'file': str(file_path)
                        })
                
                elif isinstance(node, ast.ClassDef):
                    # Calculate complexity for the class itself
                    class_complexity = self.calculate_complexity(node)
                    
                    # Calculate complexity for all methods in the class
                    method_complexities = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            method_complexity = self.calculate_complexity(child)
                            method_complexities.append(method_complexity)
                    
                    # Check if any method exceeds limits
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            complexity = self.calculate_complexity(method)
                            if complexity > self.max_complexity:
                                violations.append({
                                    'type': 'method',
                                    'name': f"{node.name}.{method.name}",
                                    'complexity': complexity,
                                    'max_allowed': self.max_complexity,
                                    'line': method.lineno,
                                    'file': str(file_path)
                                })
                    
                    # Check class overall complexity
                    if class_complexity > self.class_max_complexity:
                        violations.append({
                            'type': 'class',
                            'name': node.name,
                            'complexity': class_complexity,
                            'max_allowed': self.class_max_complexity,
                            'line': node.lineno,
                            'file': str(file_path)
                        })
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
        
        return violations
    
    def check_directory(self, directory: Path) -> List[Dict]:
        """Check all Python files in directory."""
        all_violations = []
        
        for file_path in directory.rglob("*.py"):
            # Skip test files and virtual environments
            if any(part in str(file_path) for part in ['test', 'tests', '__pycache__', 'venv', '.venv']):
                continue
            
            violations = self.analyze_file(file_path)
            all_violations.extend(violations)
        
        return all_violations
    
    def run(self, paths: List[str]) -> int:
        """Run complexity check on specified paths."""
        all_violations = []
        
        for path_str in paths:
            path = Path(path_str)
            if path.is_file():
                violations = self.analyze_file(path)
                all_violations.extend(violations)
            elif path.is_dir():
                all_violations.extend(self.check_directory(path))
        
        # Report violations
        if all_violations:
            print("❌ COMPLEXITY VIOLATIONS DETECTED:")
            print("=" * 60)
            
            # Group violations by type
            functions = [v for v in all_violations if v['type'] == 'function']
            methods = [v for v in all_violations if v['type'] == 'method']
            classes = [v for v in all_violations if v['type'] == 'class']
            
            if functions:
                print("🔧 FUNCTIONS:")
                for violation in functions:
                    print(f"   📁 {violation['file']}:{violation['line']}")
                    print(f"   Function: {violation['name']}")
                    print(f"   Complexity: {violation['complexity']} (max: {violation['max_allowed']})")
                    print()
            
            if methods:
                print("🔧 METHODS:")
                for violation in methods:
                    print(f"   📁 {violation['file']}:{violation['line']}")
                    print(f"   Method: {violation['name']}")
                    print(f"   Complexity: {violation['complexity']} (max: {violation['max_allowed']})")
                    print()
            
            if classes:
                print("🔧 CLASSES:")
                for violation in classes:
                    print(f"   📁 {violation['file']}:{violation['line']}")
                    print(f"   Class: {violation['name']}")
                    print(f"   Complexity: {violation['complexity']} (max: {violation['max_allowed']})")
                    print()
            
            print("🔧 RECOMMENDATIONS:")
            print("- Break complex functions into smaller, focused functions")
            print("- Extract conditional logic into separate methods")
            print("- Use early returns to reduce nesting")
            print("- Consider using strategy pattern for complex conditionals")
            print("- Split large classes into smaller, focused classes")
            
            return 1
        
        print("✅ All code meets complexity requirements!")
        return 0


def main():
    """Main entry point for complexity checker."""
    parser = argparse.ArgumentParser(description="Check cyclomatic complexity")
    parser.add_argument("paths", nargs="+", help="Files or directories to check")
    parser.add_argument("--max-complexity", type=int, default=10,
                       help="Maximum complexity for functions/methods")
    parser.add_argument("--class-max-complexity", type=int, default=15,
                       help="Maximum complexity for classes")
    
    args = parser.parse_args()
    
    checker = ComplexityChecker(
        max_complexity=args.max_complexity,
        class_max_complexity=args.class_max_complexity
    )
    exit_code = checker.run(args.paths)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 