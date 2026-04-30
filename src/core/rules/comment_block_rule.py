"""
MODULE: comment_block_rule
ARCHITECTURE PATTERN: AST-based validation
LEARNING OBJECTIVES: Detect missing function documentation
AGENTIC INSTRUCTIONS: Look for # Concept, # Trade-off, # Execution comments before or after function
"""
import re
from typing import List, Dict, Any
from src.core.rules.base_rule import BaseRule


class CommentBlockRule(BaseRule):
    id = "R004"
    name = "missing_comment_block"
    description = "Functions should have # Concept, # Trade-off, # Execution comments"
    severity = "warning"
    auto_fixable = False
    
    # TODO: Split this function (currently 61 lines > 30 limit)
    def check(self, file_path: str, content: str) -> List[Dict[str, Any]]:
    # Concept: TODO - Purpose of check
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Look for function definitions
            if line.strip().startswith('def '):
                # Extract function name
                match = re.search(r'def\s+(\w+)\s*\(', line)
                if not match:
                    continue
                func_name = match.group(1)
                
                # Skip magic methods
                if func_name.startswith('__') and func_name.endswith('__'):
                    continue
                
                # Check 5 lines BEFORE and 10 lines AFTER for required comments
                found_concept = False
                found_tradeoff = False
                found_execution = False
                
                # Check before (5 lines up)
                for j in range(max(0, i-5), i):
                    line_lower = lines[j].lower()
                    if 'concept' in line_lower and '#' in lines[j]:
                        found_concept = True
                    if ('trade-off' in line_lower or 'tradeoff' in line_lower) and '#' in lines[j]:
                        found_tradeoff = True
                    if 'execution' in line_lower and '#' in lines[j]:
                        found_execution = True
                
                # Check after (10 lines down)
                for j in range(i + 1, min(i + 15, len(lines))):
                    line_lower = lines[j].lower()
                    if 'concept' in line_lower and '#' in lines[j]:
                        found_concept = True
                    if ('trade-off' in line_lower or 'tradeoff' in line_lower) and '#' in lines[j]:
                        found_tradeoff = True
                    if 'execution' in line_lower and '#' in lines[j]:
                        found_execution = True
                
                missing = []
                if not found_concept:
                    missing.append("# Concept")
                if not found_tradeoff:
                    missing.append("# Trade-off")
                if not found_execution:
                    missing.append("# Execution")
                
                if missing:
                    violations.append(self.violation(
                        i + 1,
                        f"Function '{func_name}' missing: {', '.join(missing)}",
                        f"Add {missing[0]} explaining the design decision"
                    ))
        
        return violations
