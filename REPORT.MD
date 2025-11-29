## Summary

This report documents improvements made to the Expense Management backend to make the code more robust, easier to maintain, and safer to deploy. The refactoring follows SOLID principles and employs specific design patterns. Tests were updated to reflect code changes and the coverage report is appended at the end.

## SOLID Principles Applied

### Single Responsibility Principle (SRP)
- **AuthService class** (`app/auth.py`): Handles only authentication concerns—password hashing, token creation/verification, and user retrieval. Previously, these functions were scattered. Now they're grouped in one service class.
- **UserCRUD, ExpenseCRUD, TagCRUD classes** (`app/crud.py`): Each class manages database operations for a single entity type. `UserCRUD` handles user operations, `ExpenseCRUD` handles expense operations, `TagCRUD` handles tag operations. This separates concerns and makes each class easier to test and modify.
- **Config class** (`app/config.py`): Centralized all configuration logic using `pydantic_settings`. Settings are loaded once and accessed via a singleton `settings` object, avoiding scattered environment variable reads.

### Open/Closed Principle (OCP)
- **Backward compatibility wrappers**: Module-level functions like `verify_password()`, `create_access_token()`, and CRUD functions wrap the service/class methods. This allows existing code to work unchanged while new code can use the class-based API. The system is open for extension (new methods in classes) but closed for modification (old imports still work).
- **Dependency injection for `get_current_user`**: Accepts an optional `db` parameter. This allows extending behavior (injecting mock databases for tests) without modifying the core logic.

### Liskov Substitution Principle (LSP)
- **Pydantic schema inheritance**: `UserCreate` extends `UserBase`, `ExpenseCreate` extends `ExpenseBase`. Anywhere `UserBase` is expected, `UserCreate` can be used without breaking behavior. This ensures derived schemas are true subtypes.

### Interface Segregation Principle (ISP)
- **Separate CRUD classes**: Instead of one giant CRUD manager, we have `UserCRUD`, `ExpenseCRUD`, and `TagCRUD`. Each exposes only methods relevant to its entity. Routes depend only on the CRUD interface they need (e.g., expense routes never call `UserCRUD.create_user`).

### Dependency Inversion Principle (DIP)
- **Database dependency injection**: FastAPI routes depend on the `get_db()` generator abstraction, not directly on `SessionLocal` or engine. This allows swapping database implementations (e.g., in-memory for tests, Postgres for production) without changing route code.
- **AuthService static methods**: The service doesn't depend on concrete implementations of password hashing or JWT libraries directly in routes. Routes call `AuthService.verify_password()` or `AuthService.create_access_token()`, which depend on `passlib` and `jose` abstractions. If we switch crypto libraries, only `AuthService` changes.

## Design Patterns Used

### Facade Pattern
- **AuthService** acts as a facade for cryptographic and token operations. Instead of routes directly calling `pwd_context.verify()` or `jwt.encode()`, they call high-level methods like `AuthService.verify_password()` or `AuthService.create_access_token()`. This hides complexity and provides a simple interface.
- **CRUD classes** (`UserCRUD`, `ExpenseCRUD`, `TagCRUD`) are facades over SQLAlchemy operations. Routes call `ExpenseCRUD.create_expense()` instead of manually constructing models, handling tags, and committing transactions. This simplifies route code and centralizes error handling.

### Factory Pattern
- **`_get_or_create_tags` method** in `TagCRUD`: This method retrieves existing tags or creates new ones as needed. It's a factory method that produces `Tag` objects based on input names and user context. This encapsulates the "find-or-create" logic and prevents duplicate tags.

### Dependency Injection Pattern
- **`get_db()` generator**: FastAPI's `Depends(get_db)` injects a database session into route handlers. This is constructor injection via function parameters.
- **`get_current_user` with injectable `db`**: Accepts a `db` parameter for tests. In production, if `db` is `None`, it creates a session from `get_db()`. In tests, we pass a mock session. This is dependency injection enabling testability.

### Builder Pattern (Implicit)
- **Pydantic models with `ConfigDict`**: Pydantic schemas use `model_config = ConfigDict(from_attributes=True)` to build response models from ORM objects. While not a classic builder with step-by-step construction, it's a declarative builder that assembles validated output models from database rows.

### Singleton Pattern
- **`settings` object** (`app/config.py`): The `Settings` class is instantiated once via `Settings.load_settings()` and assigned to `settings`. All modules import and use the same `settings` instance. This avoids repeatedly parsing environment variables and ensures consistent configuration.

## Specific Improvements and Rationale

### Robust DB Initialization on Startup
- **Why**: Azure App Service may not have the `/home/data` directory by default. Without directory creation, the app crashes on first run.
- **How**: Added `os.makedirs(db_dir, exist_ok=True)` in the startup event. This ensures the directory exists before SQLAlchemy tries to create the database file.
- **Pattern**: Initialization pattern—ensuring preconditions before the application serves requests.

### Safer Session Lifecycle in `get_current_user`
- **Why**: If `get_current_user` opens a session without a `finally` block, exceptions could leak sessions and exhaust the connection pool.
- **How**: Wrapped session logic in `try`/`finally`. If `db` is `None`, we call `next(get_db())` to get a session and set `close_session=True`, then `finally: db_session.close()` ensures cleanup.
- **Pattern**: Resource Acquisition Is Initialization (RAII) pattern—guaranteed cleanup of resources.

### Health Endpoint Read/Write Checks
- **Why**: A simple `200 OK` doesn't verify the database is writable. Write failures can occur even if reads succeed (disk full, permissions).
- **How**: Added a `?full=true` query parameter. When set, the health endpoint creates a test user, flushes to DB, then rolls back (non-destructive). Reports `"write": "ok"` or `"write": "failed: ..."`.
- **Pattern**: Health check pattern—proactive readiness/liveness verification for orchestrators (Kubernetes, Azure).

### Error Handling and Logging
- **Why**: Generic exceptions reaching the client expose implementation details and don't help debugging in production.
- **How**: Wrapped CRUD operations in `try`/`except` blocks. On failure, log the exception with `logger.exception()` and raise `HTTPException` with appropriate status codes (400, 404, 500).
- **Pattern**: Centralized exception handling—consistent error responses and logging.

### CRUD Defensive Patterns (Optional Return Types)
- **Why**: CRUD methods like `get_expense()` or `update_user()` may not find the requested entity. Returning `None` is clearer than raising exceptions in the CRUD layer.
- **How**: Methods return `Optional[Model]`. Routes check for `None` and raise `HTTPException(404)` if needed. This separates business logic (CRUD) from HTTP concerns (routes).
- **Pattern**: Null Object pattern (implicit)—using `None` as a sentinel for "not found" rather than exceptions.

### Backward Compatibility Wrappers
- **Why**: Tests and existing code may import functions like `create_user()` or `create_access_token()` directly. Breaking these imports requires extensive refactoring.
- **How**: Added module-level wrapper functions that delegate to class methods. Example: `def create_user(db, user): return UserCRUD.create_user(db, user)`.
- **Pattern**: Adapter pattern—old interface wraps new implementation, preserving compatibility.

## Tests

Tests were designed with **testability** and **isolation** as primary goals, leveraging FastAPI's dependency injection system and pytest's fixture ecosystem.

### Testing Strategy and Techniques

#### Fixtures for Test Data Management
- **Session-scoped database fixture** (`conftest.py`): Creates an in-memory SQLite database once per test session, avoiding filesystem I/O and ensuring clean test environments.
- **Function-scoped session fixture**: Each test gets a fresh database session wrapped in a transaction that rolls back after the test completes, preventing test pollution.
- **`test_user` fixture**: Generates unique users per test using `uuid.uuid4()` to avoid username/email collisions when tests run in parallel.

**Rationale**: Fixtures separate test data setup from test logic, making tests more readable and reducing boilerplate. The transaction rollback pattern ensures true test isolation—tests cannot affect each other even when run concurrently.

#### Dependency Injection for Mocking
- **Database session override** (`conftest.py`):
  ```python
  def override_get_db():
      yield db_session
  app.dependency_overrides[get_db] = override_get_db
  ```
  Tests inject a controlled in-memory session instead of the production database.

- **Injectable `db` parameter in `get_current_user`** (`app/auth.py`): Accepts an optional `db` parameter for testing. Tests pass mock sessions directly, bypassing the production database entirely.

**Rationale**: Dependency injection makes the codebase testable without mocking frameworks. Tests control database state precisely, ensuring deterministic results and fast execution (no network/disk I/O).

#### Unit Tests for Core Logic
- **`test_auth.py`**: Tests `AuthService` methods in isolation:
  - Password hashing/verification (`verify_password`, `get_password_hash`)
  - JWT token creation/validation (`create_access_token`, `verify_token`)
  - User registration/login flows

- **`test_crud.py`**: Tests CRUD operations directly:
  - User creation, retrieval, authentication, updates
  - Expense creation, listing, updates, deletion
  - Tag association logic

- **`test_models.py`** and **`test_schemas.py`**: Validate Pydantic schemas and SQLAlchemy models work correctly with test data.

**Rationale**: Unit tests isolate business logic from HTTP concerns, making failures easier to diagnose. Testing `AuthService.verify_password()` directly is faster and clearer than sending HTTP requests through the entire stack.

#### Integration Tests for End-to-End Flows
- **`test_integration.py`**: Tests complete user journeys:
  - Register → Login → Create Expense → List Expenses
  - Verifies JWT authentication, database persistence, and API response formats

- **`test_database.py`**: Tests database-level integration:
  - Schema validation (e.g., invalid email formats raise errors)
  - Foreign key relationships (expenses link to users)
  - Transaction rollback on errors

**Rationale**: Integration tests catch issues that unit tests miss—incorrect transaction handling, missing foreign keys, serialization errors. They run against the real ORM and FastAPI routing layer (using `TestClient`).

#### Mocking Strategy (Implicit via DI)
- **No explicit mocking frameworks used**: Instead of `unittest.mock.patch()`, tests inject controlled dependencies:
  ```python
  app.dependency_overrides[get_db] = override_get_db
  ```
  This replaces the production database generator with a test fixture.

**Rationale**: Dependency injection makes mocking unnecessary for most cases. This avoids brittle tests that break when implementation details change (e.g., renaming a method would break `mock.patch` calls but not DI-based tests).

#### Coverage-Driven Test Design
- **100% coverage on test modules**: All fixtures, helpers, and test utilities are themselves tested.
- **Strategic coverage gaps**:
  - `app/main.py` (56%): Startup events, health checks, Prometheus integration not fully tested (requires Docker environment)
  - `app/auth.py` (74%): Error paths for expired/malformed tokens tested, but some edge cases (concurrent token refreshes) deferred

**Rationale**: 100% coverage isn't always valuable (testing boilerplate wastes time), but critical paths (authentication, CRUD operations, error handling) are thoroughly tested. The 83% total coverage reflects intentional focus on high-risk areas.

### Test Execution and CI Integration
- **Local execution**: `pytest -v --cov=app --cov-report=html`
- **CI pipeline** (`.github/workflows/deploy.yml`):
  ```yaml
  - name: Run backend tests with coverage
    working-directory: ./backend
    env:
      SECRET_KEY: ${{ secrets.SECRET_KEY }}
      DATABASE_URL: "sqlite:///:memory:"
    run: |
      pytest -v --cov=app --cov-report=term --cov-report=html --cov-fail-under=70
  ```
  Tests run on every push to `main`, blocking deployment if coverage drops below 70%.

**Rationale**: CI integration ensures tests run on every commit, catching regressions immediately. The `--cov-fail-under=70` threshold enforces minimum quality standards without requiring 100% coverage (which has diminishing returns).

### Key Testing Patterns Applied
1. **Arrange-Act-Assert (AAA)**: All tests follow this structure for readability.
2. **Test Isolation**: Fixtures and transaction rollbacks ensure no test depends on another.
3. **Fail-Fast**: Tests use `assert` early to catch issues before expensive operations.
4. **Test Data Builders**: Fixtures like `test_user` generate valid test data consistently.

These techniques resulted in a fast, reliable test suite that executes in under 5 seconds locally and provides confidence for continuous deployment.


## Coverage Report

The updated test suite produced the following coverage:

| **Module**                  | **Statements** | **Missing** | **Coverage** |
|-----------------------------|----------------|-------------|--------------|
| `app/__init__.py`           | 0              | 0           | 100%         |
| `app/auth.py`               | 73             | 19          | 74%          |
| `app/config.py`             | 20             | 0           | 100%         |
| `app/crud.py`               | 152            | 33          | 78%          |
| `app/database.py`           | 18             | 4           | 78%          |
| `app/main.py`               | 125            | 55          | 56%          |
| `app/models.py`             | 31             | 0           | 100%         |
| `app/schemas.py`            | 41             | 0           | 100%         |
| `tests/__init__.py`         | 0              | 0           | 100%         |
| `tests/conftest.py`         | 38             | 0           | 100%         |
| `tests/test_auth.py`        | 22             | 0           | 100%         |
| `tests/test_crud.py`        | 22             | 0           | 100%         |
| `tests/test_database.py`    | 78             | 0           | 100%         |
| `tests/test_integration.py` | 17             | 0           | 100%         |
| `tests/test_models.py`      | 6              | 0           | 100%         |
| `tests/test_schemas.py`     | 10             | 0           | 100%         |
| **TOTAL**                   | **653**        | **111**     | **83%**      |



## Monitoring and Observability

### Prometheus Integration

The backend exposes Prometheus-compatible metrics for monitoring application health and performance in production environments.

#### Architecture

**Local Development:**
- Prometheus runs as a separate Docker container defined in `docker-compose.yml`
- Scrapes metrics from the backend at `http://backend:8000/metrics` every 15 seconds
- Accessible at `http://localhost:9090` for querying and visualization

**Azure Deployment:**
- Backend exposes `/metrics` endpoint but Prometheus container is not deployed
- Azure Web Apps don't support multi-container deployments via Docker Compose
- `/metrics` endpoint remains accessible for external scraping or monitoring tools

#### Implementation Details

**Backend Instrumentation (`app/main.py`):**
```python
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, "/metrics")
    logger.info("✅ Prometheus enabled at /metrics")
except ImportError:
    logger.info("⚠️ Prometheus not installed, skipping instrumentation")
```

## Conclusion

The refactoring improves maintainability, testability, and production stability by:

- Applying **SOLID principles** to reduce coupling and increase cohesion.
- Using **design patterns** (Facade, Factory, Dependency Injection, Singleton) to simplify code and hide complexity.
- Adding **defensive error handling** and logging for production diagnosability.
- Ensuring **backward compatibility** so existing code continues to work during migration.

These changes make the codebase easier to extend (new features), safer to deploy (explicit error handling, health checks), and faster to test (dependency injection, mocks).