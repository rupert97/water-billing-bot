# Contributing to Water Billing Bot

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

Be respectful, inclusive, and supportive of other contributors. We're committed to providing a harassment-free experience.

## 📋 Before You Start

1. **Check existing issues** - Avoid duplicate work
2. **Read documentation** - Understand the codebase structure
3. **Set up development environment** - Follow the Quick Start guide

## 🔧 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/water-billing-bot.git
cd water-billing-bot

# Add upstream remote
git remote add upstream https://github.com/original/water-billing-bot.git
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

## 💻 Development Workflow

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_similpay_client.py -v

# Run with specific marker
pytest -m "not integration" -v
```

## 📝 Commit Guidelines

Use clear, descriptive commit messages:

```
[TYPE] Short description (50 chars max)

Detailed explanation if needed (wrap at 72 chars).
Explain what and why, not how.

Fixes #123
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting (black, isort)
- `refactor:` Code restructuring
- `test:` Test additions/improvements
- `chore:` Maintenance, dependencies

### Examples

```
feat: Add support for multiple telegram chats

Allow configuration of multiple chat IDs to send
notifications to multiple recipients.

Fixes #45
```

```
fix: Handle malformed API responses gracefully

Add try-except block to handle cases where
Similpay API returns unexpected data format.
```

## 🧪 Testing Requirements

All contributions must include tests:

1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test module interactions
3. **Coverage** - Aim for 80%+ coverage on new code

```bash
# Check coverage
pytest --cov=src --cov-report=term-missing
```

## 🚀 Pull Request Process

### Before Submitting

```bash
# Update from upstream
git fetch upstream
git rebase upstream/main

# Run full test suite
pytest
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/

# Push to your fork
git push origin feature/your-feature-name
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
- [ ] Added/updated unit tests
- [ ] Tests pass locally
- [ ] Coverage maintained

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated Checks** - GitHub Actions runs tests
2. **Code Review** - Maintainers review code
3. **Feedback** - Address review comments
4. **Merge** - Merged by maintainer

## 📚 Documentation Contribution

### Update README

If your change affects usage:
```bash
# Edit README.md
git add README.md
git commit -m "docs: Update README for feature X"
```

### Update Module Docs

```bash
# Edit MODULE_DOCUMENTATION.md
# Run tests to ensure code samples work
pytest
```

## 🐛 Bug Reports

### What to Include

1. **Description** - What's the bug?
2. **Steps to Reproduce** - How to trigger it?
3. **Expected Behavior** - What should happen?
4. **Actual Behavior** - What actually happens?
5. **Environment** - Python version, OS, AWS region
6. **Logs** - CloudWatch logs or error messages

### Example

```markdown
**Description**
Lambda handler crashes when Similpay API returns empty response.

**Steps to Reproduce**
1. Deploy function
2. Run with API returning empty response
3. Check CloudWatch logs

**Expected Behavior**
Function logs error and returns 500 status

**Actual Behavior**
Function crashes with KeyError

**Environment**
- Python 3.12
- Windows 10
- us-east-1 region

**Logs**
```
KeyError: 'Code'
Traceback:...
```
```

## ✨ Feature Requests

### What to Include

1. **Use Case** - Why is this needed?
2. **Proposed Solution** - How should it work?
3. **Alternatives** - Other ways to solve this?
4. **Additional Context** - Any other info?

### Example

```markdown
**Use Case**
Currently, bills are sent to a single Telegram chat.
Need to support multiple recipients.

**Proposed Solution**
Add TELEGRAM_CHAT_IDS environment variable
accepting comma-separated values.

**Implementation**
Modify TelegramNotifier to accept list of chat IDs
and send to each one.

**Alternatives**
- Use Telegram groups (requires manual setup)
- Create multiple Lambda functions (expensive)
```

## 🎯 Areas for Contribution

- **Core Features** - Enhance bill processing logic
- **Integrations** - Add support for other APIs
- **Testing** - Increase test coverage
- **Documentation** - Improve guides and examples
- **Performance** - Optimize Lambda execution
- **Security** - Improve credential handling

## 📞 Questions?

- Create a discussion on GitHub
- Ask in issues (label as question)
- Check existing documentation

## ✅ Checklist Before Submitting

- [ ] Fork and clone repository
- [ ] Create feature branch
- [ ] Implement changes with tests
- [ ] Format code (black, isort)
- [ ] Run linting and type checks
- [ ] All tests pass locally
- [ ] Update relevant documentation
- [ ] Commit with clear messages
- [ ] Push to fork and create PR
- [ ] Respond to review feedback

## 🎉 Thank You!

Your contributions help make Water Billing Bot better for everyone!
