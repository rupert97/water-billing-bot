# GitHub Setup Guide

Complete guide for pushing Water Billing Bot to GitHub.

## Prerequisites

- Git installed locally
- GitHub account
- Project repository created on GitHub

## Step 1: Initialize Local Repository

```bash
# Navigate to project directory
cd water-billing-bot

# Initialize git repository
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Water Billing Bot project setup"
```

## Step 2: Connect to GitHub

```bash
# Add GitHub remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Verify remote
git remote -v
# Should output:
# origin  https://github.com/YOUR_USERNAME/REPO_NAME.git (fetch)
# origin  https://github.com/YOUR_USERNAME/REPO_NAME.git (push)
```

## Step 3: Push to GitHub

```bash
# Create and push to main branch
git branch -M main
git push -u origin main
```

## Step 4: Verify Setup

Visit your repository on GitHub and verify:

- [ ] All files are present
- [ ] README.md displays correctly
- [ ] `.gitignore` is active (no `__pycache__` folders)
- [ ] GitHub Actions workflows appear under "Actions" tab
- [ ] Issue templates appear when creating new issue
- [ ] Pull request template appears when creating PR

## Step 5: Configure GitHub Repository

### Settings → General

1. **Repository name** - water-billing-bot
2. **Description** - "Serverless automation tool for water bill notifications via Telegram"
3. **Homepage URL** - Link to deployed docs (optional)
4. **Topics** - Add: `aws-lambda`, `telegram`, `automation`, `serverless`, `billing`
5. **Default branch** - `main`

### Settings → Code and automation → Branches

1. **Add branch protection rule**
   - Branch name pattern: `main`
   - ✓ Require pull request reviews before merging
   - ✓ Require status checks to pass
   - ✓ Require branches to be up to date
   - ✓ Dismiss stale pull request approvals
   - ✓ Require code review from code owners

### Settings → Code and automation → Actions

1. Enable GitHub Actions
2. Allow all actions and reusable workflows
3. Require approval for first-time contributors

### Settings → Secrets and variables → Actions

If you want to run tests with real AWS credentials (optional):

1. Add `AWS_ACCESS_KEY_ID`
2. Add `AWS_SECRET_ACCESS_KEY`
3. Add `AWS_DEFAULT_REGION`

⚠️ **Never commit sensitive credentials!**

## Step 6: Enable GitHub Pages (Optional)

If you want to host documentation:

1. Go to Settings → Pages
2. Set source to `main` branch
3. Select `/root` or `/docs` folder
4. Save

Visit `https://YOUR_USERNAME.github.io/REPO_NAME`

## Step 7: Add Badges to README

Update README.md with:

```markdown
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Tests](https://github.com/YOUR_USERNAME/water-billing-bot/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/water-billing-bot/actions)
```

## Step 8: Create Release

```bash
# Create a git tag
git tag -a v1.0.0 -m "Initial release"

# Push tag to GitHub
git push origin v1.0.0

# On GitHub: Go to Releases → Create Release from Tag
# Add release notes and description
```

## Step 9: Publish to PyPI (Optional)

If you want to publish the package:

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI
twine upload dist/*
```

Users can then install with:
```bash
pip install water-billing-bot
```

## Workflow for Future Contributions

### For Maintainers

```bash
# Update code
git add .
git commit -m "feat: Add new feature"

# Push to main (after PR review)
git push origin main

# Create release when ready
git tag -a v1.1.0 -m "Version 1.1.0"
git push origin v1.1.0
```

### For Contributors

```bash
# Fork repository on GitHub

# Clone your fork
git clone https://github.com/YOUR_USERNAME/water-billing-bot.git

# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git commit -m "feat: Your feature"

# Push to your fork
git push origin feature/your-feature

# Create Pull Request on GitHub
```

## Maintenance

### Regular Tasks

- [ ] Review and merge PRs
- [ ] Address GitHub Issues
- [ ] Update CHANGELOG.md
- [ ] Create releases
- [ ] Monitor GitHub Actions
- [ ] Update dependencies when needed

### Monitor

- Check Actions tab for CI/CD failures
- Review security alerts
- Keep dependencies updated

### Commands

```bash
# Check for security vulnerabilities
pip audit

# Update all dependencies
pip install --upgrade -r requirements.txt

# Review git history
git log --oneline --graph --all
```

## Troubleshooting

### Push Rejected

```bash
# Update from remote
git pull origin main

# Retry push
git push origin main
```

### Large Files

If you try to push files > 100MB:

```bash
# Use Git LFS (Large File Storage)
git lfs install
git lfs track "*.large"
git add .gitattributes
git commit -m "Add LFS tracking"
```

### Branch Protection

If branch is protected:
1. Create feature branch
2. Push to feature branch
3. Create PR
4. Wait for review and merge

## Resources

- [GitHub Docs](https://docs.github.com)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Keep a Changelog](https://keepachangelog.com)
- [Semantic Versioning](https://semver.org)

## Next Steps

After setup:

1. ✅ Invite collaborators
2. ✅ Monitor first runs of GitHub Actions
3. ✅ Test pull request workflow
4. ✅ Update documentation with links
5. ✅ Share project with others!

---

**Questions?** Check GitHub documentation or create an issue in your repository.
