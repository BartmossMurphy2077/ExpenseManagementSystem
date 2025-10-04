# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app import models, crud, schemas
from app.database import DatabaseConfig, DatabaseManager
from datetime import datetime

class TestDatabaseConfig(DatabaseConfig):
    def get_engine(self):
        return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

@pytest.fixture(scope="function")
def db():
    """Creates a fresh database for each test function."""
    db_manager = DatabaseManager(TestDatabaseConfig())
    session = next(db_manager.get_db())
    try:
        yield session
    finally:
        session.close()

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
