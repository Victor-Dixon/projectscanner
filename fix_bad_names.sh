#!/bin/bash
echo "Fixing bad function names..."

# bots.py: run -> execute_scan
sed -i 's/def run(self):/def execute_scan(self):/g' src/core/projectscanner/bots.py

# deploy_agent_policy.py: run -> execute_deployment
sed -i 's/def run(self, dry_run: bool = False) -> int:/def execute_deployment(self, dry_run: bool = False) -> int:/g' src/deployment/agents/deploy_agent_policy.py

# agents_md_checker.py: run -> run_check
sed -i 's/def run(self, paths: list) -> int:/def run_check(self, paths: list) -> int:/g' src/quality/agents_md_checker.py

# complexity_checker.py: run -> analyze_complexity
sed -i 's/def run(self, paths: List[str]) -> int:/def analyze_complexity(self, paths: List[str]) -> int:/g' src/quality/complexity_checker.py

# loc_checker.py: run -> count_lines
sed -i 's/def run(self, paths: List[str]) -> int:/def count_lines(self, paths: List[str]) -> int:/g' src/quality/loc_checker.py

echo "✅ Fixed 5 bad function names"
