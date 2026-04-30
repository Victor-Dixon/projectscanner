"""
MODULE: compressed_logic_rule
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES
AGENTIC INSTRUCTIONS
"""

from typing import List, Dict, Any
from src.core.rules.base_rule import BaseRule


class CompressedLogicRule(BaseRule):
    id = "R006"
    name = "compressed_logic"
    description = "Detect overly complex nested expressions and long lambdas"
    severity = "info"
    auto_fixable = False
    
    # Concept: TODO - Explain the core idea behind check
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 39 lines > 30 limit)
    def check(self, file_path: str, content: str) -> List[Dict[str, Any]]:
    # Concept: TODO - Purpose of check
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # Check for deeply nested parentheses (compressed logic)
            if line.count('(') > 3 and line.count(')') > 3:
                # Check if it's not just a tuple or simple expression
                if 'if' in line or 'for' in line or 'lambda' in line:
                    violations.append(self.violation(
                        i + 1,
                        "Deeply nested expression detected",
                        "Break into multiple lines with intermediate variables"
                    ))
            
            # Check for overly complex lambda
            if 'lambda' in line and len(line) > 100:
                violations.append(self.violation(
                    i + 1,
                    "Complex lambda expression (over 100 chars)",
                    "Replace lambda with a named function definition"
                ))
            
            # Check for multiple statements on one line
            if ';' in line and not line.strip().startswith('#'):
                violations.append(self.violation(
                    i + 1,
                    "Multiple statements on one line",
                    "Split into separate lines for clarity"
                ))
        
        return violations
