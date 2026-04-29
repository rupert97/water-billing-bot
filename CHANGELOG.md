# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and core functionality
- AWS Lambda handler with EventBridge integration
- DynamoDB state management for notifications
- Similpay API client for bill queries
- Telegram Bot integration for notifications
- Comprehensive test suite
- GitHub Actions CI/CD pipeline

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## [1.0.0] - 2026-04-28

### Added
- Initial release of Water Billing Tracker Bot
- Automated water bill monitoring via Similpay API
- Telegram notifications for new and urgent bills
- Smart state management to prevent duplicate alerts
- AWS Lambda and DynamoDB integration
- Full test coverage
- Complete documentation
- CI/CD pipeline with GitHub Actions
- MIT License

### Features
- Daily automated bill checking
- Telegram alerts with bill details
- 2-day urgent reminder before due date
- Zero external dependencies (uses Python stdlib + boto3)
- AWS Free Tier compatible ($0/month)
- Easy deployment with provided scripts

---

## Format Notes

### Sections
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes

### Versioning
- MAJOR: Breaking changes
- MINOR: Backward-compatible new features
- PATCH: Backward-compatible bug fixes

### Examples

```markdown
## [1.1.0] - 2026-05-15

### Added
- Support for multiple Telegram recipients
- Lambda layers for dependency management

### Fixed
- Handle edge case with malformed API responses
- Prevent duplicate urgent notifications

### Security
- Update boto3 to patch security vulnerability
```

---

## How to Update

When making changes:
1. Update CHANGELOG.md before creating PR
2. Add entry to [Unreleased] section
3. Move to appropriate version when releasing
4. Follow format and sections consistently
5. Link to related issues/PRs when relevant

Example:
```markdown
### Fixed
- Handle empty Similpay responses (#45)
- Prevent duplicate notifications (#42)
```
