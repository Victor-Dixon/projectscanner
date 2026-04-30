"""
MODULE: contract_engine
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES
AGENTIC INSTRUCTIONS
"""


import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.rules.base_rule import BaseRule


class ContractEngine:
    """
    Concept: Registry Pattern - maintains a collection of rules and orchestrates
    their execution against target files.
    """
    
    # Concept: TODO - Explain the core idea behind __init__
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def __init__(self, rules: Optional[List[BaseRule]] = None):
    # Concept: Orchestrate rule execution
    # Trade-off: Dynamic imports vs static registration
    # Execution: Loop through rules and aggregate violations
        """
        Execution: Initialize with optional custom rule list, otherwise load defaults.
        """
        self.rules = rules or self._load_default_rules()
        self.severity_weights = {"error": 10, "warning": 5, "info": 2}
        
    # Concept: TODO - Explain the core idea behind _load_default_rules
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 38 lines > 30 limit)
    def _load_default_rules(self) -> List[BaseRule]:
    # Concept: Orchestrate rule execution
    # Trade-off: Dynamic imports vs static registration
    # Execution: Loop through rules and aggregate violations
        """
        Trade-off: Dynamic import allows rules to be added without modifying engine.
        """
        rules = []
        
        # Import rule classes directly
        try:
            from src.core.rules.module_header_rule import ModuleHeaderRule
            rules.append(ModuleHeaderRule())
        except ImportError as e:
            print(f"Warning: Could not load ModuleHeaderRule: {e}", file=sys.stderr)
        
        try:
            from src.core.rules.comment_block_rule import CommentBlockRule
            rules.append(CommentBlockRule())
        except ImportError as e:
            print(f"Warning: Could not load CommentBlockRule: {e}", file=sys.stderr)
        
        try:
            from src.core.rules.function_length_rule import FunctionLengthRule
            rules.append(FunctionLengthRule())
        except ImportError as e:
            print(f"Warning: Could not load FunctionLengthRule: {e}", file=sys.stderr)
        
        try:
            from src.core.rules.naming_rule import NamingRule
            rules.append(NamingRule())
        except ImportError as e:
            print(f"Warning: Could not load NamingRule: {e}", file=sys.stderr)
        
        try:
            from src.core.rules.compressed_logic_rule import CompressedLogicRule
            rules.append(CompressedLogicRule())
        except ImportError as e:
            print(f"Warning: Could not load CompressedLogicRule: {e}", file=sys.stderr)
        
        return rules
    
    # Concept: TODO - Explain the core idea behind analyze_file
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 31 lines > 30 limit)
    def analyze_file(self, file_path: Path) -> Tuple[List[Dict[str, Any]], int]:
    # Concept: Orchestrate rule execution
    # Trade-off: Dynamic imports vs static registration
    # Execution: Loop through rules and aggregate violations
        """
        Execution: Analyze a single file, return violations and compliance score.
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return [{
                "rule_id": "R999",
                "rule_name": "file_read_error",
                "severity": "error",
                "line": 0,
                "message": f"Cannot read file: {str(e)}",
                "fix_suggestion": "Check file permissions and encoding"
            }], 0
        
        violations = []
        
        for rule in self.rules:
            try:
                results = rule.check(str(file_path), content)
                violations.extend(results)
            except Exception as e:
                violations.append(rule.violation(
                    0,
                    f"Rule '{rule.name}' execution failed: {str(e)}",
                    "Check rule implementation for errors"
                ))
        
        score = self._calculate_score(violations)
        return violations, score
    
    # Concept: TODO - Explain the core idea behind _calculate_score
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def _calculate_score(self, violations: List[Dict[str, Any]]) -> int:
    # Concept: Orchestrate rule execution
    # Trade-off: Dynamic imports vs static registration
    # Execution: Loop through rules and aggregate violations
        """
        Execution: Score from 0-100, starting at 100 and deducting based on severity.
        """
        if not violations:
            return 100
        
        total_deduction = 0
        for v in violations:
            severity = v.get("severity", "warning")
            total_deduction += self.severity_weights.get(severity, 5)
        
        # Cap at 100 points of deduction
        return max(0, 100 - min(total_deduction, 100))
    
    # Concept: TODO - Explain the core idea behind get_summary
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    def get_summary(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Concept: Orchestrate rule execution
    # Trade-off: Dynamic imports vs static registration
    # Execution: Loop through rules and aggregate violations
        """
        Execution: Aggregate statistics about violations for reporting.
        """
        summary = {
            "total_violations": len(violations),
            "by_severity": {"error": 0, "warning": 0, "info": 0},
            "by_rule": {},
            "auto_fixable_count": 0,
        }
        
        for v in violations:
            # Count by severity
            severity = v.get("severity", "warning")
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # Count by rule
            rule_name = v.get("rule_name", "unknown")
            summary["by_rule"][rule_name] = summary["by_rule"].get(rule_name, 0) + 1
            
            # Count auto-fixable
            if v.get("fix_suggestion"):
                summary["auto_fixable_count"] += 1
        
        return summary
    
    # Concept: TODO - Explain the core idea behind analyze_directory
    # Trade-off: TODO - Document any trade-offs or design decisions
    # Execution: TODO - Describe how this function works at a high level


    # TODO: Split this function (currently 35 lines > 30 limit)
    def analyze_directory(self, directory: Path, pattern: str = "*.py") -> Dict[str, Any]:
    # Concept: Orchestrate rule execution
    # Trade-off: Dynamic imports vs static registration
    # Execution: Loop through rules and aggregate violations
        """
        Execution: Analyze all Python files in a directory tree.
        """
        files_analyzed = 0
        all_violations = []
        total_score = 0
        file_results = []
        
        for file_path in directory.rglob(pattern):
            # Skip common exclusions
            if any(skip in str(file_path) for skip in ["__pycache__", ".git", "venv", "env", ".pytest"]):
                continue
            
            files_analyzed += 1
            violations, score = self.analyze_file(file_path)
            all_violations.extend(violations)
            total_score += score
            
            file_results.append({
                "path": str(file_path.relative_to(directory)),
                "violations": violations,
                "score": score
            })
        
        avg_score = total_score // files_analyzed if files_analyzed else 0
        
        return {
            "scan_time": datetime.now().isoformat(),
            "files_analyzed": files_analyzed,
            "average_score": avg_score,
            "total_violations": len(all_violations),
            "summary": self.get_summary(all_violations),
            "file_results": file_results
        }
