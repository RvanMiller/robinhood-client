# CI/CD Setup Guide

This repository uses GitHub Actions for Continuous Integration and automated publishing to Test PyPI.

## Workflow Overview

The CI/CD pipeline consists of two main jobs:

### 1. Test Job
- **Triggers**: On pull requests to `main` and pushes to `main`
- **Matrix Strategy**: Tests against Python 3.12 and 3.13
- **Steps**:
  - Code checkout
  - Python setup with Poetry
  - Dependency caching for faster builds
  - Code linting with Ruff (checking and formatting)
  - Unit test execution (integration tests are excluded)
  - Package building verification

### 2. Publish Job
- **Triggers**: Only when code is pushed to `main` (i.e., after PR merge)
- **Dependencies**: Requires the test job to pass
- **Steps**:
  - Code checkout
  - Python setup with Poetry
  - Package building
  - Publishing to Test PyPI

## Required GitHub Configuration

### Trusted Publishing Setup
This repository uses PyPI's Trusted Publishing feature, which eliminates the need for API tokens. The publishing is authenticated using GitHub's OIDC tokens.

**No secrets configuration required!** The workflow uses trusted publishing with the following setup:
- Publisher: GitHub Actions
- Repository: `RvanMiller/robinhood-client` 
- Workflow: `ci-publish.yml`
- Environment: Not specified (publishes from main branch)

## How It Works

### For Pull Requests
- The workflow runs tests and linting on every PR
- Tests must pass before the PR can be merged
- No publishing occurs on PRs

### For Main Branch Pushes (After PR Merge)
- All tests run again to ensure main branch stability
- If tests pass, the package is automatically built and published to Test PyPI using trusted publishing
- No manual token management required - authentication happens automatically via GitHub OIDC
- Version bumping is handled by Poetry based on `pyproject.toml`

## Local Development

### Running Tests Locally
```bash
# Run unit tests only (same as CI)
poetry run pytest tests/unit/

# Run with verbose output
poetry run pytest tests/unit/ -v

# Run specific test file
poetry run pytest tests/unit/common/clients_tests.py
```

### Linting Locally
```bash
# Check for issues
poetry run ruff check .

# Auto-fix issues
poetry run ruff check . --fix

# Check formatting
poetry run ruff format --check .

# Apply formatting
poetry run ruff format .
```

### Building Package Locally
```bash
# Build wheel and source distribution
poetry build

# Check built package
ls dist/
```

## Version Management

To publish a new version:
1. Update the version in `pyproject.toml`
2. Create a PR with your changes
3. After the PR is reviewed and merged, the package will automatically be published to Test PyPI

## Test PyPI vs PyPI

Currently configured for **Test PyPI** with trusted publishing:
- Test PyPI URL: https://test.pypi.org/
- Package URL will be: https://test.pypi.org/project/robinhood-client/
- Authentication: GitHub OIDC (no tokens needed)

When ready for production, you can:
1. Configure trusted publishing for production PyPI in your PyPI account settings
2. Change the `repository-url` in the workflow from Test PyPI to production PyPI (remove the repository-url line entirely)
3. The same trusted publishing setup will work for production PyPI

## Troubleshooting

### Tests Failing
- Check the Actions tab in GitHub for detailed error messages
- Run tests locally to debug: `poetry run pytest tests/unit/ -v`

### Publishing Failing
- Verify that trusted publishing is correctly configured in your Test PyPI account settings
- Ensure the repository name, workflow name, and branch match your trusted publishing configuration
- Check that the version in `pyproject.toml` hasn't been published before
- Verify that the package name `robinhood-client` is available on Test PyPI
- Make sure the workflow has `id-token: write` permissions

### Linting Errors
- Run `poetry run ruff check . --fix` to auto-fix issues
- Run `poetry run ruff format .` to fix formatting
