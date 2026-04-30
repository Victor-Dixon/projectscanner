"""
================================================================================
MODULE: base_rule.py
ARCHITECTURE PATTERN: Abstract Base Class / Strategy Pattern

LEARNING OBJECTIVES & KEY CONCEPTS:
1. Polymorphic interface definition for AST and line-by-line file inspections.
2. Structured enforcement tracking with context metadata.

AGENTIC INSTRUCTIONS:
- Input constraints: Must accept a string file path and string content.
- Output: Standardized list of dictionary violations.
- Error handling: Fail-fast for missing arguments, suppress and log parser errors.
================================================================================
"""

import ast
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class BaseRule(ABC):
    """
    Concept: The Strategy Pattern defines a family of algorithms, encapsulates each 
    one, and makes them interchangeable. This lets the base rule vary independently 
    from the clients that evaluate the codebase.
    """

    id: str = "R000"
    name: str = "base_rule"
    description: str = "Base rule - override this subclass."
    severity: str = "warning"
    auto_fixable: bool = False

    @abstractmethod
    # Concept: TODO - Explain the core idea behind check
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def check(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Execution: Analyzes the file content and produces a list of violation dictionaries.
        """
        pass

    # Concept: TODO - Explain the core idea behind violation
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def violation(
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        self, 
        line: int, 
        message: str, 
        fix_suggestion: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Trade-off: Centralizing the violation data contract adds a minor abstraction 
        layer but ensures uniform output format across all rules for the parser.
        """
        return {
            "rule_id": self.id,
            "rule_name": self.name,
            "severity": self.severity,
            "line": line,
            "message": message,
            "fix_suggestion": fix_suggestion,
        }

    # Concept: TODO - Explain the core idea behind safe_parse_ast
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def safe_parse_ast(self, content: str) -> Optional[ast.AST]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """
        Execution: Safely attempts to parse the file content into an Abstract Syntax Tree.
        Returns None if the code is invalid or cannot be parsed.
        """
        try:
            return ast.parse(content)
        except Exception:
            return None

    # Concept: TODO - Explain the core idea behind get_lines
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def get_lines(self, content: str) -> List[str]:
    # Concept: TODO
    # Trade-off: TODO
    # Execution: TODO
        """
        Execution: Splits content into lines while preserving original line numbers 
        (1-indexed) for accurate reporting.
        """
        return content.splitlines()

