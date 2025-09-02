# Trusted Publishing Setup Guide

This guide explains how to configure PyPI Trusted Publishing for the `robinhood-client` package.

## What is Trusted Publishing?

Trusted Publishing is a security feature that allows you to publish packages to PyPI directly from GitHub Actions without using API tokens. It uses OpenID Connect (OIDC) to authenticate your GitHub repository with PyPI.

## Benefits

- ✅ No API tokens to manage or store as secrets
- ✅ More secure authentication
- ✅ Automatic token rotation
- ✅ Easier setup and maintenance

## Setup Instructions

### 1. Test PyPI Setup (Current Configuration)

1. Go to [Test PyPI](https://test.pypi.org/) and log in or create an account
2. Navigate to your account settings: https://test.pypi.org/manage/account/publishing/
3. Click "Add a new pending publisher"
4. Fill in the form with **EXACTLY** these values:
   - **PyPI project name**: `robinhood-client`
   - **Owner**: `RvanMiller`
   - **Repository name**: `robinhood-client`
   - **Workflow filename**: `ci-publish.yml`
   - **Environment name**: Leave empty
5. Click "Add"

**Important**: The values must match exactly what GitHub sends in the OIDC claims. Based on your error, use these exact values:
- Repository: `RvanMiller/robinhood-client`
- Workflow: `ci-publish.yml` (just the filename, not the full path)

### 2. Production PyPI Setup (When Ready)

When you're ready to publish to production PyPI:

1. Go to [PyPI](https://pypi.org/) and log in
2. Follow the same steps as above for Test PyPI
3. Update the workflow file by removing the `repository-url` line:
   ```yaml
   - name: Publish to PyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     # Remove the repository-url line to publish to production PyPI
   ```

## Workflow Requirements

The GitHub Actions workflow must have the `id-token: write` permission for trusted publishing to work:

```yaml
permissions:
  id-token: write  # IMPORTANT: mandatory for trusted publishing
```

This is already configured in your `ci-publish.yml` workflow.

## Verification

After setup, when you push to the main branch:

1. The workflow will run tests
2. If tests pass, it will build the package
3. The package will be automatically published using trusted publishing
4. No manual intervention or secret configuration required

## Troubleshooting

### "Publisher with matching claims was not found" Error

If you get this exact error, it means the trusted publisher configuration doesn't match the workflow claims. Here's how to fix it:

1. **Check your Test PyPI trusted publisher configuration**:
   - Go to https://test.pypi.org/manage/account/publishing/
   - Look for an entry with project name `robinhood-client`
   - If it doesn't exist, add it using the exact values above
   - If it exists, verify the configuration matches exactly

2. **Verify these exact claim values in your Test PyPI config**:
   - **Repository**: `RvanMiller/robinhood-client`
   - **Workflow**: `ci-publish.yml`
   - **Environment**: (leave empty)

3. **If the publisher exists but still fails**:
   - Delete the existing publisher configuration
   - Create a new one with the exact values above
   - Wait a few minutes for the configuration to propagate

### Package Name Issues

If you get a "project does not exist" error:
1. The package name `robinhood-client` might not be available
2. You may need to choose a different name (e.g., `robinhood-api-client`)
3. Update the name in `pyproject.toml` and reconfigure trusted publishing

### Common Issues

1. **Publishing fails with authentication error**
   - Verify the trusted publisher configuration matches exactly
   - Check that `id-token: write` permission is set
   - Ensure the workflow name is exactly `ci-publish.yml`

2. **Package name conflicts**
   - If the package name is taken, you may need to choose a different name
   - Update the name in `pyproject.toml` and reconfigure trusted publishing

3. **Version conflicts**
   - Each version can only be published once
   - Increment the version in `pyproject.toml` before publishing

## Security Notes

- Trusted publishing only works from the specified repository and workflow
- No secrets are stored in GitHub
- Publishing can only happen from the main branch (as configured)
- The OIDC token is automatically generated and validated by PyPI
