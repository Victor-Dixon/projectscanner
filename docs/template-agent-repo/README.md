# 🤖 Template Agent Repository

This is a template repository that follows the **Agent Policy & Enforcement Framework** for creating high-quality, maintainable agent-generated code.

## 📋 Quick Start

```bash
# Clone this template
git clone <template-repo-url> your-agent-name

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Start developing!
```

## 🏗️ Project Structure

```
your-agent-name/
├── src/
│   ├── core/           # Core business logic (≤ 350 LOC)
│   ├── gui/            # User interface components (≤ 500 LOC)
│   ├── utils/          # Shared utilities
│   └── tests/          # Test suite
├── docs/               # Documentation
├── scripts/            # Build/deployment scripts
├── .pre-commit-config.yaml  # Quality enforcement
├── AGENTS.md           # Policy guidelines
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## 🎯 Code Standards

### **MANDATORY REQUIREMENTS**
- ✅ **OOP**: All code must be class-based
- ✅ **SRP**: Single Responsibility Principle
- ✅ **LOC Limits**: Core ≤ 350, GUI ≤ 500 lines
- ✅ **Complexity**: Functions ≤ 10, Classes ≤ 15

### **QUALITY TOOLS**
- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **Bandit**: Security scanning
- **Custom checks**: LOC, complexity, OOP structure

## 🚀 Development Workflow

### 1. **Setup Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### 2. **Development Process**
```bash
# Make changes to your code
# Pre-commit hooks will automatically run on commit

# Run checks manually
pre-commit run --all-files

# Run specific checks
python scripts/loc_checker.py src/
python scripts/complexity_checker.py src/
python scripts/oop_checker.py src/
```

### 3. **Quality Assurance**
```bash
# Run all quality checks
pre-commit run --all-files

# Run tests
python -m pytest tests/

# Check coverage
coverage run -m pytest tests/
coverage report
```

## 📊 Quality Metrics

### **Target Scores**
- **Test Coverage**: ≥ 80%
- **Code Quality Score**: ≥ 80/100
- **Performance**: < 100ms response times
- **Security**: Zero vulnerabilities

### **Monitoring**
- Automated checks on every commit
- CI/CD pipeline validation
- Regular quality reports

## 🔧 Customization

### **Repository-Specific Rules**
Edit `AGENTS.md` to add repository-specific guidelines:

```markdown
## Repository-Specific Standards

### Domain-Specific Requirements
- [ ] Add your specific requirements here
- [ ] Document any special considerations
- [ ] Define domain-specific metrics
```

### **Pre-commit Configuration**
Modify `.pre-commit-config.yaml` to add custom hooks:

```yaml
# Add custom hooks
- repo: local
  hooks:
    - id: custom-checker
      name: Custom Checker
      entry: python scripts/custom_checker.py
      language: python
      stages: [commit]
```

## 📖 Documentation

### **Required Documentation**
- [ ] `AGENTS.md`: Policy guidelines
- [ ] `README.md`: Project overview
- [ ] `docs/architecture.md`: System design
- [ ] `docs/api.md`: API documentation
- [ ] `docs/deployment.md`: Deployment guide

### **Code Documentation**
- [ ] All classes must have docstrings
- [ ] All public methods must be documented
- [ ] Complex logic must have inline comments
- [ ] Architecture decisions must be documented

## 🚨 Violation Handling

### **Pre-commit Blocks**
- Code cannot be committed if it violates standards
- Automatic formatting and linting fixes
- Manual intervention required for complex issues

### **CI/CD Pipeline**
- Automated quality checks on every PR
- Build failure on violations
- Quality gates prevent merge

### **Escalation Process**
1. **First Violation**: Warning + documentation
2. **Second Violation**: Mandatory refactor
3. **Third Violation**: Code freeze until compliance
4. **Persistent Issues**: Architecture review required

## 🎓 Best Practices

### **Class Design**
```python
class ExampleAgent:
    """Single responsibility: Handle example operations."""
    
    def __init__(self):
        """Initialize the agent."""
        self._data = []
    
    def process_data(self, data: List[str]) -> List[str]:
        """Process input data and return results."""
        # Implementation here
        pass
```

### **Error Handling**
```python
class RobustAgent:
    """Example of proper error handling."""
    
    def execute_operation(self, input_data: str) -> Result:
        """Execute operation with proper error handling."""
        try:
            result = self._process(input_data)
            return Result.success(result)
        except ValidationError as e:
            return Result.failure(f"Validation failed: {e}")
        except ProcessingError as e:
            return Result.failure(f"Processing failed: {e}")
```

### **Testing**
```python
class TestExampleAgent:
    """Test suite for ExampleAgent."""
    
    def test_process_data(self):
        """Test data processing functionality."""
        agent = ExampleAgent()
        result = agent.process_data(["test", "data"])
        assert len(result) == 2
```

## 📞 Support

### **Getting Help**
- **Technical Issues**: Create GitHub issue with `[AGENT-POLICY]` label
- **Policy Questions**: Contact architecture team
- **Tool Problems**: Submit bug report with logs

### **Resources**
- [Python Style Guide](https://peps.python.org/pep-0008/)
- [Clean Code Principles](https://clean-code-developer.com/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Testing Best Practices](https://realpython.com/python-testing/)

---

## ✅ Compliance Checklist

- [ ] All code is class-based
- [ ] LOC limits are respected
- [ ] Complexity limits are met
- [ ] Test coverage ≥ 80%
- [ ] Documentation is complete
- [ ] Pre-commit hooks are installed
- [ ] CI/CD pipeline is configured
- [ ] Security scan passes
- [ ] Performance benchmarks met

---

*This template ensures consistent, high-quality code across all agent repositories. Follow the guidelines strictly to maintain code quality and team productivity.* 