# backend/tests/test_database.py
import pytest
import tempfile
import os
from app.database import SQLiteConfig, DatabaseManager
from app.models import Base
from sqlalchemy import text


def test_sqlite_config():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        config = SQLiteConfig(tmp_path)
        engine = config.get_engine()

        # Test that we can connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_database_manager():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        config = SQLiteConfig(tmp_path)
        db_manager = DatabaseManager(config)

        # Test that we can get a session
        db_session = next(db_manager.get_db())
        assert db_session is not None

        # Test that tables are created
        tables = db_manager.engine.table_names()
        expected_tables = ['users', 'expenses', 'tags', 'expense_tags']
        for table in expected_tables:
            assert table in tables

        db_session.close()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_database_directory_creation():
    test_dir = "./test_data_dir"
    test_db_path = f"{test_dir}/test.db"

    try:
        # Ensure directory doesn't exist
        if os.path.exists(test_dir):
            os.rmdir(test_dir)

        config = SQLiteConfig(test_db_path)
        assert os.path.exists(test_dir)

    finally:
        # Cleanup
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
