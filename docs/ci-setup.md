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

## Required GitHub Secrets

You need to configure the following secret in your GitHub repository:

### TEST_PYPI_API_TOKEN
1. Go to [Test PyPI](https://test.pypi.org/)
2. Create an account or log in
3. Go to Account Settings → API tokens
4. Create a new API token with upload permissions
5. Copy the token (starts with `pypi-`)
6. In your GitHub repository:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: Paste your Test PyPI token

## How It Works

### For Pull Requests
- The workflow runs tests and linting on every PR
- Tests must pass before the PR can be merged
- No publishing occurs on PRs

### For Main Branch Pushes (After PR Merge)
- All tests run again to ensure main branch stability
- If tests pass, the package is automatically built and published to Test PyPI
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

Currently configured for **Test PyPI** only:
- Test PyPI URL: https://test.pypi.org/
- Package URL will be: https://test.pypi.org/project/robinhood-client/

When ready for production, you can:
1. Create a production PyPI account and API token
2. Add `PYPI_API_TOKEN` secret to GitHub
3. Modify the workflow to publish to PyPI instead of Test PyPI

## Troubleshooting

### Tests Failing
- Check the Actions tab in GitHub for detailed error messages
- Run tests locally to debug: `poetry run pytest tests/unit/ -v`

### Publishing Failing
- Verify `TEST_PYPI_API_TOKEN` secret is correctly set
- Ensure the version in `pyproject.toml` hasn't been published before
- Check that the package name `robinhood-client` is available on Test PyPI

### Linting Errors
- Run `poetry run ruff check . --fix` to auto-fix issues
- Run `poetry run ruff format .` to fix formatting
