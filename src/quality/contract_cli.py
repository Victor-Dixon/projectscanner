"""
MODULE: contract_cli
ARCHITECTURE PATTERN: 
LEARNING OBJECTIVES: 
AGENTIC INSTRUCTIONS: 
"""

#!/usr/bin/env python3
"""
================================================================================
MODULE: contract_cli.py
ARCHITECTURE PATTERN: Command Line Interface

LEARNING OBJECTIVES:
1. Provide user-friendly contract enforcement interface
2. Support JSON output for automation
3. Generate human-readable reports

AGENTIC INSTRUCTIONS:
- Accept path argument (defaults to current directory)
- Support --json flag for machine-readable output
- Return exit code 0 if compliant (>80), 1 otherwise
================================================================================
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.rules.contract_engine import ContractEngine


# Concept: TODO - Explain the core idea behind colorize
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


def colorize(text: str, color: str) -> str:
# Concept: TODO
# Trade-off: TODO
# Execution: TODO
    """Add terminal color codes"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


# Concept: TODO - Explain the core idea behind format_report
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 51 lines > 30 limit)
def format_report(results: dict, color: bool = True) -> str:
# Concept: TODO
# Trade-off: TODO
# Execution: TODO
    """Generate human-readable report"""
    lines = []
    
    lines.append("=" * 70)
    lines.append(colorize("CONTRACT COMPLIANCE REPORT", 'cyan' if color else "CONTRACT COMPLIANCE REPORT"))
    lines.append("=" * 70)
    lines.append(f"Scan Time: {results['scan_time']}")
    lines.append(f"Files Analyzed: {results['files_analyzed']}")
    lines.append(f"Total Violations: {results['total_violations']}")
    
    # Score with color
    score = results['average_score']
    if score >= 80:
        score_color = 'green'
        grade = "A"
    elif score >= 60:
        score_color = 'yellow'
        grade = "C"
    else:
        score_color = 'red'
        grade = "F"
    
    score_str = f"{score}/100"
    lines.append(f"Average Compliance: {colorize(score_str, score_color) if color else score_str} (Grade: {grade})")
    
    # Summary by severity
    lines.append(f"\n{colorize('VIOLATIONS BY SEVERITY', 'yellow' if color else 'VIOLATIONS BY SEVERITY')}")
    lines.append("-" * 40)
    summary = results['summary']
    for severity, count in summary['by_severity'].items():
        sev_color = 'red' if severity == 'error' else 'yellow' if severity == 'warning' else 'blue'
        sev_str = f"  {severity.upper()}: {count}"
        lines.append(colorize(sev_str, sev_color) if color else sev_str)
    
    # Summary by rule
    if summary['by_rule']:
        lines.append(f"\n{colorize('VIOLATIONS BY RULE', 'yellow' if color else 'VIOLATIONS BY RULE')}")
        lines.append("-" * 40)
        for rule, count in sorted(summary['by_rule'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {rule}: {count}")
    
    # Top offending files (show up to 5)
    files_with_violations = [f for f in results['file_results'] if f['violations']]
    if files_with_violations:
        lines.append(f"\n{colorize('TOP OFFENDING FILES', 'yellow' if color else 'TOP OFFENDING FILES')}")
        lines.append("-" * 40)
        for file_result in sorted(files_with_violations, key=lambda x: len(x['violations']), reverse=True)[:5]:
            lines.append(f"  {file_result['path']}: {len(file_result['violations'])} violations (Score: {file_result['score']}/100)")
    
    return '\n'.join(lines)


# Concept: TODO - Explain the core idea behind main
# Trade-off: TODO - Document any trade-offs or design decisions
# Execution: TODO - Describe how this function works at a high level


# TODO: Split this function (currently 39 lines > 30 limit)
def main():
# Concept: TODO - Purpose of main
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach
    parser = argparse.ArgumentParser(description='Enforce code contracts')
    parser.add_argument('path', nargs='?', default='.', help='Directory or file to scan')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    args = parser.parse_args()
    
    target = Path(args.path)
    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)
    
    engine = ContractEngine()
    
    if target.is_file():
        # Single file mode
        violations, score = engine.analyze_file(target)
        results = {
            "scan_time": "now",
            "files_analyzed": 1,
            "average_score": score,
            "total_violations": len(violations),
            "summary": engine.get_summary(violations),
            "file_results": [{"path": target.name, "violations": violations, "score": score}]
        }
    else:
        # Directory mode
        results = engine.analyze_directory(target)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results, color=not args.no_color))
    
    # Exit code: 0 if compliant (>80), 1 otherwise
    sys.exit(0 if results['average_score'] >= 80 else 1)


if __name__ == "__main__":
    main()

# Concept: TODO - Purpose of format_report
# Trade-off: TODO - Design decisions
# Execution: TODO - Implementation approach