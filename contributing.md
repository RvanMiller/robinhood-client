# Contributing

Anyone and everyone is encouraged to contribute to this project. The most helpful changes are pull requests that fix one of the open issues in the Issues tab.

## Project Scope

This library is designed to provide a Python interface for functionality available in the Robinhood Mobile App and Browser App. We focus on:

- **Data Retrieval**: Orders, account information, market data
- **Authentication**: Session management and MFA support  
- **Core API Operations**: Direct mappings to Robinhood's API endpoints

**Out of Scope**: Additional analysis features like calculating average losses, dividend summaries, or other functionality that could be provided by separate analysis libraries. The goal is to maintain a focused, lightweight client that mirrors the official app's capabilities.

## Development Workflow

1. **Pull Requests**: Unit tests run automatically on all PR pushes
2. **Merge to Main**: Accepted PRs trigger automatic release to Test PyPI
3. **Production Release**: After validation on Test PyPI and successful integration tests (run by project maintainers), packages are published to official PyPI via GitHub releases

## Pull Request Process

1. Ensure changes align with the project scope (Robinhood app functionality only)
2. Make sure that if you make any grammar or documentation changes, that they are in a separate commit from any code changes
3. Update version number in `pyproject.toml` following [Semantic Versioning 2.0](https://semver.org):
   - **Major** (X.0.0): Breaking API changes
   - **Minor** (0.X.0): New features, backward compatible
   - **Patch** (0.0.X): Bug fixes, backward compatible
4. Add imports for new public functions to appropriate `__init__.py` files
5. Write comprehensive tests covering your changes:
   - Unit tests for all new functionality
   - Integration tests for API interactions (when applicable)
   - Avoid tests that place real orders
6. Follow the existing code patterns and architectural guidelines
7. Be responsive to feedback during the review process

## Development Setup

This project uses Poetry for dependency management. To set up your development environment:

1. **Install Poetry** (if you haven't already):
   ```bash
   pip install poetry
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

## Testing

The project has comprehensive test coverage with both unit and integration tests:

### Unit Tests
Run unit tests (no API calls, use mocks):
```bash
poetry run pytest tests/unit/
```

### Integration Tests  
Run integration tests (requires valid Robinhood credentials):
```bash
# Set required environment variables first
export RH_USERNAME="your_username"
export RH_PASSWORD="your_password"  
export RH_MFA_CODE="your_mfa_secret"
export RH_ACCOUNT_NUMBER="your_account_number"

poetry run pytest tests/integration/
```

### Test Guidelines
- **Unit tests**: Mock external dependencies, test business logic
- **Integration tests**: Test actual API interactions with real credentials
- **No order placement**: Avoid tests that submit real trading orders
- **Follow naming convention**: Test files end with `_tests.py`
- **Test methods**: Use `test_`, `it_`, `and_`, `but_`, `they_` prefixes

## Code Quality

```bash
# Linting
poetry run ruff check .

# Auto-fix issues  
poetry run ruff check . --fix

# Format code
poetry run ruff format .
```

## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, gender identity and expression, level of experience,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or
advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic
  address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

### Scope

This Code of Conduct applies both within project spaces and in public spaces
when an individual is representing the project or its community. Examples of
representing a project or community include using an official project e-mail
address, posting via an official social media account, or acting as an appointed
representative at an online or offline event. Representation of a project may be
further defined and clarified by project maintainers.
