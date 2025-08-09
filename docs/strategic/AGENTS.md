# 🤖 AGENT POLICY & ENFORCEMENT FRAMEWORK

## 📋 MISSION STATEMENT
This document establishes mandatory coding standards and enforcement mechanisms for all agent-generated code across the portfolio. Compliance is non-negotiable and enforced through automated tooling.

## 🎯 CORE PRINCIPLES

### 1. **Object-Oriented Programming (OOP)**
- **MANDATORY**: All code must be class-based
- **Single Responsibility Principle (SRP)**: Each class has one reason to change
- **Encapsulation**: Private methods/properties where appropriate
- **Inheritance**: Use composition over inheritance when possible

### 2. **Code Quality Standards**
- **Lines of Code (LOC) Limits**:
  - Core modules: ≤ 350 lines
  - GUI modules: ≤ 500 lines
  - Average target: ≈ 250 lines
  - **VIOLATION**: Automatic rejection if exceeded

- **Cyclomatic Complexity**:
  - Functions: ≤ 10 complexity
  - Classes: ≤ 15 complexity
  - **VIOLATION**: Automatic rejection if exceeded

### 3. **Architecture Requirements**
- **Separation of Concerns**: Clear boundaries between layers
- **Dependency Injection**: Avoid tight coupling
- **Error Handling**: Comprehensive exception management
- **Logging**: Structured logging for all operations

## 🛠️ ENFORCEMENT TOOLS

### 🛰️ GitHub Actions Workflow (Primary Enforcement)
**Cloud-based enforcement that cannot be bypassed by agents**
```yaml
# .github/workflows/agent-enforcer.yml
name: Agent Enforcer
on: [push, pull_request]
jobs:
  enforce:
    runs-on: ubuntu-latest
    steps:
      - name: Run Ruff (linting)
      - name: Check cyclomatic complexity
      - name: Check LOC per file
      - name: Verify AGENTS.md exists
      - name: Run custom complexity checks
```

### 🧩 Pre-commit Hooks (Local Development)
**Local enforcement for developer convenience**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=88]
  
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: local
    hooks:
      - id: loc-checker
        name: LOC Checker
        entry: python scripts/loc_checker.py
        language: python
        stages: [commit]
      
      - id: complexity-checker
        name: Complexity Checker
        entry: python scripts/complexity_checker.py
        language: python
        stages: [commit]
```

### CI/CD Pipeline Rules
- **Automatic Checks**: Every PR must pass
- **Metrics Tracking**: LOC, complexity, test coverage
- **Quality Gates**: Block merge on violations
- **Performance Monitoring**: Response time tracking

## 📊 QUALITY METRICS

### Code Quality Score
```
Score = (Test Coverage * 0.3) + 
        (Code Complexity Score * 0.3) + 
        (Documentation Coverage * 0.2) + 
        (Performance Score * 0.2)

Minimum Score: 80/100
```

### Automated Checks
- [ ] LOC within limits
- [ ] Cyclomatic complexity ≤ threshold
- [ ] Test coverage ≥ 80%
- [ ] No security vulnerabilities
- [ ] Performance benchmarks met
- [ ] Documentation complete

## 🚫 VIOLATION CONSEQUENCES

### Immediate Actions
1. **Pre-commit Block**: Code cannot be committed
2. **CI Failure**: Pipeline stops execution
3. **PR Rejection**: Merge blocked until fixed
4. **Review Required**: Manual approval needed

### Escalation
1. **First Violation**: Warning + documentation
2. **Second Violation**: Mandatory refactor
3. **Third Violation**: Code freeze until compliance
4. **Persistent Issues**: Architecture review required

## 📁 PROJECT STRUCTURE

### Standard Agent Repository Layout
```
agent-repo/
├── src/
│   ├── core/           # Core business logic
│   ├── gui/            # User interface components
│   ├── utils/          # Shared utilities
│   └── tests/          # Test suite
├── docs/               # Documentation
├── scripts/            # Build/deployment scripts
├── .pre-commit-config.yaml
├── AGENTS.md           # This file
├── requirements.txt    # Dependencies
└── README.md          # Project overview
```

## 🔧 IMPLEMENTATION CHECKLIST

### For New Repositories
- [ ] Clone from `template-agent-repo`
- [ ] Install pre-commit hooks
- [ ] Configure CI/CD pipeline
- [ ] Set up quality monitoring
- [ ] Document architecture decisions

### For Existing Repositories
- [ ] Add AGENTS.md file
- [ ] Install pre-commit hooks
- [ ] Refactor code to meet standards
- [ ] Update CI/CD configuration
- [ ] Train team on new standards

## 📈 MONITORING & REPORTING

### Weekly Reports
- Repository compliance status
- Quality metrics trends
- Violation patterns
- Improvement recommendations

### Monthly Reviews
- Policy effectiveness assessment
- Tool performance evaluation
- Standard updates
- Team training needs

## 🎓 TRAINING & RESOURCES

### Required Knowledge
- OOP principles and patterns
- Code quality best practices
- Testing methodologies
- Performance optimization
- Security best practices

### Resources
- [Python Style Guide](https://peps.python.org/pep-0008/)
- [Clean Code Principles](https://clean-code-developer.com/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Testing Best Practices](https://realpython.com/python-testing/)

## 📞 SUPPORT & ESCALATION

### Questions & Issues
- **Technical Issues**: Create GitHub issue with `[AGENT-POLICY]` label
- **Policy Questions**: Contact architecture team
- **Tool Problems**: Submit bug report with logs

### Emergency Overrides
- **Temporary Exemption**: Requires CTO approval
- **Emergency Fixes**: Must be followed by compliance review
- **Architecture Changes**: Require design review

---

## ✅ COMPLIANCE VERIFICATION

**Last Updated**: [Current Date]
**Next Review**: [Monthly]
**Enforcement Level**: MANDATORY
**Compliance Status**: [To be filled per repository]

---

*This document is living and will be updated as standards evolve. All changes require architecture team approval.* 