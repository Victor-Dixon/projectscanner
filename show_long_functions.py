#!/usr/bin/env python3
import ast
from pathlib import Path

def find_long_functions(file_path):
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except Exception as e:
        return []
    
    long_funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            try:
                length = node.end_lineno - node.lineno + 1
                if length > 30:
                    long_funcs.append((node.name, node.lineno, length))
            except:
                pass
    return long_funcs

print("📏 Functions exceeding 30 lines:\n")
for py_file in Path(".").rglob("*.py"):
    if "__pycache__" in str(py_file) or "venv" in str(py_file):
        continue
    long_funcs = find_long_functions(py_file)
    if long_funcs:
        try:
            rel_path = py_file.relative_to(Path.cwd())
            print(f"\n{rel_path}:")
            for name, line, length in long_funcs[:3]:
                print(f"  Line {line}: {name} ({length} lines)")
        except:
            print(f"\n{py_file.name}:")
            for name, line, length in long_funcs[:3]:
                print(f"  Line {line}: {name} ({length} lines)")
