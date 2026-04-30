"""
MODULE: module_header_rule
ARCHITECTURE PATTERN: Pattern matching
LEARNING OBJECTIVES: Enforce module documentation standards
AGENTIC INSTRUCTIONS: Check for required sections in module docstring
"""
import re
from typing import List, Dict, Any
from src.core.rules.base_rule import BaseRule


class ModuleHeaderRule(BaseRule):
    id = "R002"
    name = "module_header_missing"
    description = "Module must have docstring with required sections"
    severity = "error"
    auto_fixable = True
    
    REQUIRED_SECTIONS = ["MODULE:", "ARCHITECTURE PATTERN:", "LEARNING OBJECTIVES", "AGENTIC INSTRUCTIONS"]
    
    # Concept: TODO - Explain the purpose of check
    # Trade-off: TODO - Document design decisions
    # Execution: TODO - Describe the implementation approach


    # TODO: Split this function (currently 44 lines > 30 limit)
    def check(self, file_path: str, content: str) -> List[Dict[str, Any]]:
    # Concept: TODO - Purpose of check
    # Trade-off: TODO - Design decisions
    # Execution: TODO - Implementation approach
        if not content.strip():
            return []
        
        lines = content.split('\n')
        
        # Find docstring
        docstring_lines = []
        in_docstring = False
        docstring_start = -1
        
        for i, line in enumerate(lines[:30]):  # Check first 30 lines
            if not in_docstring and (line.strip().startswith('"""') or line.strip().startswith("'''")):
                in_docstring = True
                docstring_start = i
                continue
            if in_docstring:
                if line.strip().endswith('"""') or line.strip().endswith("'''"):
                    break
                docstring_lines.append(line)
        
        if not docstring_lines:
            return [self.violation(
                1,
                "Missing module header docstring",
                "Add: '''\\nMODULE: \\nARCHITECTURE PATTERN: \\nLEARNING OBJECTIVES\\nAGENTIC INSTRUCTIONS\\n'''"
            )]
        
        docstring_content = ' '.join(docstring_lines).upper()
        violations = []
        
        for section in self.REQUIRED_SECTIONS:
            section_upper = section.upper()
            if section_upper not in docstring_content and section not in docstring_content:
                violations.append(self.violation(
                    docstring_start + 1,
                    f"Missing header section: '{section}'",
                    f"Add '{section}' to module docstring"
                ))
        
        return violations
