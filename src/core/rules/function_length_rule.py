"""
MODULE: function_length_rule
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES
AGENTIC INSTRUCTIONS
"""

import ast
from typing import List, Dict, Any
from src.core.rules.base_rule import BaseRule


class FunctionLengthRule(BaseRule):
    id = "R005"
    name = "function_too_long"
    description = "Functions should not exceed 30 lines"
    severity = "warning"
    auto_fixable = False
    
    MAX_LINES = 30
    
    # Concept: TODO - Explain the core idea behind check
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 42 lines > 30 limit)
    def check(self, file_path: str, content: str) -> List[Dict[str, Any]]:
    # Concept: TODO - Purpose of check
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        violations = []
        
        # Use AST for accurate line counting
        tree = self.safe_parse_ast(content)
        if not tree:
            return []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get line count (AST provides end_lineno in Python 3.8+)
                try:
                    end_line = node.end_lineno
                except AttributeError:
                    # Fallback: approximate by scanning
                    lines = content.split('\n')
                    end_line = node.lineno
                    for i in range(node.lineno, len(lines)):
                        if lines[i].strip() and not lines[i].startswith(' '):
                            break
                        end_line = i
                
                line_count = end_line - node.lineno + 1
                
                if line_count > self.MAX_LINES:
                    violations.append(self.violation(
                        node.lineno,
                        f"Function '{node.name}' has {line_count} lines (max {self.MAX_LINES})",
                        f"Refactor '{node.name}' into smaller helper functions"
                    ))
                elif line_count > 20:
                    # Warning for approaching limit
                    violations.append(self.violation(
                        node.lineno,
                        f"Function '{node.name}' is getting long ({line_count} lines)",
                        "Consider breaking into smaller functions"
                    ))
        
        return violations
