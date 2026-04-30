"""
MODULE: naming_rule
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES
AGENTIC INSTRUCTIONS
"""

import re
from typing import List, Dict, Any
from src.core.rules.base_rule import BaseRule


class NamingRule(BaseRule):
    id = "R003"
    name = "bad_naming"
    description = "Avoid generic function names like 'run', 'process', 'handle'"
    severity = "warning"
    auto_fixable = True
    
    FORBIDDEN_NAMES = {
        "run": "run_validation, run_calculation, run_extraction",
        "process": "process_data, process_request, process_file",
        "handle": "handle_error, handle_event, handle_request",
        "do": "perform_action, compute_result, generate_output",
        "execute": "execute_query, execute_command, execute_plan"
    }
    
    # Concept: TODO - Explain the core idea behind check
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def check(self, file_path: str, content: str) -> List[Dict[str, Any]]:
    # Concept: TODO - Purpose of check
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                # Extract function name
                match = re.search(r'def\s+(\w+)\s*\(', line)
                if match:
                    func_name = match.group(1)
                    
                    if func_name in self.FORBIDDEN_NAMES:
                        suggestions = self.FORBIDDEN_NAMES[func_name]
                        violations.append(self.violation(
                            i + 1,
                            f"Forbidden generic function name: '{func_name}'",
                            f"Rename to something descriptive (e.g., {suggestions})"
                        ))
        
        return violations
