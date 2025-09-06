# Robinhood Client AI Development Guide

## Project Overview
This is an unofficial Python REST client for the Robinhood API, forked from robin_stocks with cloud support enhancements. The codebase is structured around a layered architecture with authentication, data retrieval, and trading capabilities.

## Architecture Patterns

### Three-Layer Architecture
- **Common Layer** (`robinhood_client/common/`): Authentication, session management, base clients, schemas
- **Data Layer** (`robinhood_client/data/`): API clients for retrieving market data and order information
- **Trading Layer** (`robinhood_client/trading/`): Trading operations (currently under development)

### Client Inheritance Pattern
All API clients extend `BaseOAuthClient` which provides:
- OAuth2 authentication with token persistence
- Session persistence via pluggable `SessionStorage` implementations
- Standardized request/response handling with error management

Example client structure:
```python
class OrdersDataClient(BaseOAuthClient):
    def __init__(self, session_storage: SessionStorage):
        super().__init__(url=BASE_API_URL, session_storage=session_storage)
```

### Session Storage Pattern
The project uses a strategy pattern for session persistence:
- `FileSystemSessionStorage`: Local file storage (default)
- `AWSS3SessionStorage`: Cloud storage for containerized deployments
- Both use pickle serialization for `AuthSession` objects

### Request/Response Schema Pattern
All API interactions use Pydantic models with strict typing:
- Request models inherit from `BaseRequest` or `BaseCursorRequest` (for pagination)
- Response models inherit from `BaseResponse` or `BaseCursorResponse`
- Core business objects defined in `robinhood_client/common/schema.py`

## Development Workflow

### Poetry Dependencies
Always use Poetry for dependency management:
```bash
poetry install          # Install all dependencies
poetry add package      # Add runtime dependency
poetry add --group dev package  # Add dev dependency
```

### Testing Conventions
- Test files named `*_tests.py` (not `test_*.py`)
- Test classes: `Test*`, test methods: `test_*`, `it_*`, `and_*`, `but_*`, `they_*`
- Unit tests mock external dependencies; integration tests require real credentials
- Environment variables for integration tests: `RH_USERNAME`, `RH_PASSWORD`, `RH_MFA_CODE`, `RH_ACCOUNT_NUMBER`
- Use fake account numbers for unit tests (e.g., '123ABC').

### Code Quality
- Ruff for linting: `poetry run ruff check .`
- Python 3.12+ required
- Line length: 88 characters (Black-compatible)
- Double quotes for strings

## Critical Implementation Details

### Authentication Flow
1. Check `SessionStorage` for existing valid session
2. If none found, perform OAuth2 login with device token generation
3. Handle MFA verification workflow if required
4. Store session for reuse (unless `persist_session=False`)

### MFA Integration
Uses `pyotp` for TOTP codes. Integration tests show real-world pattern:
```python
totp = pyotp.TOTP(mfa_code).now()
client.login(username=username, password=password, mfa_code=totp)
```

### API Endpoint Management
Multiple Robinhood API bases defined in `constants.py`:
- `BASE_API_URL`: Main API (`api.robinhood.com`)
- `BASE_NUMMUS_URL`: Crypto operations (`nummus.robinhood.com`)
- Additional services: Phoenix, Minerva, Bonfire

### Error Handling
Custom `AuthenticationError` for auth failures. HTTP errors handled in base client with comprehensive status code checking.

### Logging Integration
Built-in logging system with environment variable configuration:
- `ROBINHOOD_LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `ROBINHOOD_LOG_FILE`: Optional file output
- Default: INFO level to console

## Common Patterns

### Adding New Data Clients
1. Create client class extending `BaseOAuthClient`
2. Define request/response models in `data/requests.py`
3. Use Pydantic schemas from `common/schema.py`
4. Follow the pagination pattern for list endpoints

### Testing New Features
- Create both unit tests (mocked) and integration tests (real API)
- Use the `authenticated_client` fixture for integration tests
- Mock `SessionStorage` and HTTP responses for unit tests
- Never test real order placement - use mock data only

### Integration Testing Patterns
- Module-level functions instead of class methods
- Shared authentication fixtures with module scope
- Consistent parameter patterns with type hints
- Similar validation approaches for field checking
- Comparable error handling and skipping logic

### Documentation
- Sphinx documentation in `docs/` directory
- Build with: `cd docs && poetry run make html`
- API documentation auto-generated from docstrings
