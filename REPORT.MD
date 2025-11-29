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

Tests were updated to:

- **Use the injectable `db` dependency**: Tests pass a mock or in-memory session to routes via `app.dependency_overrides`. This avoids touching the real database.
- **Cover AuthService methods**: Added unit tests for `AuthService.create_access_token()`, `verify_token()`, and password hashing. Verified that expired tokens return `None`.
- **Verify health endpoint behavior**: Tested both `?full=false` (read-only check) and `?full=true` (write check with rollback). Ensured the write test doesn't pollute the database.
- **Ensure CRUD returns optionals correctly**: Tested that `get_expense()` returns `None` for non-existent IDs and that routes handle this by raising 404.
- **Test startup DB path creation**: Used a temporary directory and verified that `os.makedirs()` is called and the directory exists before table creation.

**Rationale**: Dependency injection and clear interfaces made tests deterministic and fast. Coverage increased because the facade pattern and DIP made mocking straightforward.

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

### Coverage Gaps

- **`app/main.py` (56%)**: Remaining gaps are in startup event error branches and some route exception handlers. These are typically exercised in full integration/e2e tests against running containers.
- **`app/auth.py` (74%)**: Some JWT error paths (malformed tokens) are not fully covered. Consider adding negative tests for invalid token formats.
- **`app/crud.py` (78%)**: Tag creation edge cases (duplicate tags with different users) and some rollback branches are not fully exercised.
- **`app/database.py` (78%)**: The `get_db()` generator's exception handling isn't fully covered; this is hard to test without simulating DB crashes.

**Recommendation**: Add targeted integration tests or use mocking to simulate error conditions (DB unavailable, disk full) to increase coverage.

## Conclusion

The refactoring improves maintainability, testability, and production stability by:

- Applying **SOLID principles** to reduce coupling and increase cohesion.
- Using **design patterns** (Facade, Factory, Dependency Injection, Singleton) to simplify code and hide complexity.
- Adding **defensive error handling** and logging for production diagnosability.
- Ensuring **backward compatibility** so existing code continues to work during migration.

These changes make the codebase easier to extend (new features), safer to deploy (explicit error handling, health checks), and faster to test (dependency injection, mocks).
