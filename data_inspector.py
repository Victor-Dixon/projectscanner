#!/usr/bin/env python3
"""
Data Inspector
Inspect the structure of scanned library data
"""

import json
import os

def inspect_library_data(library_path: str = "github_library_enhanced/github_library_enhanced.json"):
    """Inspect the structure of library data."""
    try:
        with open(library_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Library Data Structure Analysis")
        print(f"Total repositories: {len(data)}")
        print("\n" + "="*50)
        
        # Sample first few repositories
        sample_count = 0
        for repo_name, repo_data in data.items():
            if sample_count >= 3:
                break
                
            print(f"\n🔍 Repository: {repo_name}")
            print(f"Type: {type(repo_data)}")
            
            if isinstance(repo_data, dict):
                print(f"Keys: {list(repo_data.keys())}")
                
                if 'files' in repo_data:
                    files = repo_data['files']
                    print(f"Files count: {len(files)}")
                    
                    # Sample first file
                    if files:
                        first_file = list(files.keys())[0]
                        first_file_data = files[first_file]
                        print(f"Sample file: {first_file}")
                        print(f"File data keys: {list(first_file_data.keys())}")
                        
                        # Show sample file data
                        print(f"Sample file data: {first_file_data}")
            
            sample_count += 1
        
        # Overall statistics
        total_files = 0
        total_functions = 0
        total_classes = 0
        
        for repo_name, repo_data in data.items():
            if isinstance(repo_data, dict) and 'files' in repo_data:
                files = repo_data['files']
                total_files += len(files)
                
                for file_path, file_data in files.items():
                    if 'functions' in file_data:
                        total_functions += len(file_data['functions'])
                    if 'classes' in file_data:
                        total_classes += len(file_data['classes'])
        
        print(f"\n" + "="*50)
        print(f"📈 Overall Statistics:")
        print(f"Total files: {total_files}")
        print(f"Total functions: {total_functions}")
        print(f"Total classes: {total_classes}")
        
    except FileNotFoundError:
        print(f"❌ Library file not found: {library_path}")
    except Exception as e:
        print(f"❌ Error reading library: {e}")

if __name__ == "__main__":
    inspect_library_data() 