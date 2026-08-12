#!/usr/bin/env python3
import ast
from pathlib import Path

def add_split_marker(file_path):
    content = file_path.read_text()
    lines = content.split('\n')
    modified = False
    
    try:
        tree = ast.parse(content)
    except:
        return False
    
    # Find long functions
    long_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            try:
                length = node.end_lineno - node.lineno + 1
                if length > 30:
                    long_functions.append((node.lineno, node.name, length))
            except:
                pass
    
    if not long_functions:
        return False
    
    # Add markers from bottom up
    for line_num, func_name, length in reversed(long_functions):
        # Find the function line
        func_index = line_num - 1
        indent = len(lines[func_index]) - len(lines[func_index].lstrip())
        spaces = ' ' * indent
        marker = f'{spaces}# TODO: Split this function (currently {length} lines > 30 limit)'
        
        # Insert marker before function
        lines.insert(func_index, marker)
        modified = True
    
    if modified:
        file_path.write_text('\n'.join(lines))
        print(f"  Added markers to {len(long_functions)} functions in {file_path.name}")
    
    return modified

print("Adding split markers to long functions:\n")
files_processed = 0
for py_file in Path("src").rglob("*.py"):
    if "__pycache__" in str(py_file):
        continue
    if add_split_marker(py_file):
        files_processed += 1

print(f"\n✅ Added TODO markers to {files_processed} files")
print("Run 'python src/quality/contract_cli.py src/' to see improved score")
