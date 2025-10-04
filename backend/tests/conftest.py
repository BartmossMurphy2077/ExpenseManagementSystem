# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app import models, crud, schemas
from app.database import DatabaseConfig, DatabaseManager
from datetime import datetime
import uuid


class TestDatabaseConfig(DatabaseConfig):
    def __init__(self):
        # Use unique database for each test run
        self.db_name = f"test_{uuid.uuid4().hex}.db"

    def get_engine(self):
        return create_engine(
            f"sqlite:///{self.db_name}",
            connect_args={"check_same_thread": False}
        )


@pytest.fixture(scope="function")
def db():
    """Creates a fresh database for each test function."""
    config = TestDatabaseConfig()
    db_manager = DatabaseManager(config)
    session = next(db_manager.get_db())
    try:
        yield session
    finally:
        session.close()
        db_manager.engine.dispose()
        # Clean up database file
        import os
        if os.path.exists(config.db_name):
            try:
                os.unlink(config.db_name)
            except PermissionError:
                pass


@pytest.fixture(scope="function")
def test_user(db):
    """Creates a test user for each test function."""
    user_data = schemas.UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword"
    )
    user = crud.UserCRUD.create_user(db, user_data)
    return user
