# backend/tests/test_database.py
import pytest
import tempfile
import os
from app.database import SQLiteConfig, DatabaseManager
from app.models import Base
from sqlalchemy import text


def test_sqlite_config():
    # Use a regular temp file path instead of NamedTemporaryFile
    import uuid
    tmp_path = f"./test_db_{uuid.uuid4().hex}.db"

    try:
        config = SQLiteConfig(tmp_path)
        engine = config.get_engine()

        # Test that we can connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

        # Close engine properly
        engine.dispose()
    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except PermissionError:
                pass  # File might still be locked on Windows


def test_database_manager():
    import uuid
    tmp_path = f"./test_db_{uuid.uuid4().hex}.db"

    try:
        config = SQLiteConfig(tmp_path)
        db_manager = DatabaseManager(config)

        # Test that we can get a session
        db_session = next(db_manager.get_db())
        assert db_session is not None

        # Test that tables are created by checking if we can query them
        from app.models import User
        users = db_session.query(User).all()
        assert isinstance(users, list)

        db_session.close()
        db_manager.engine.dispose()
    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except PermissionError:
                pass


def test_database_directory_creation():
    test_dir = "./test_data_dir"
    test_db_path = f"{test_dir}/test.db"

    try:
        # Ensure directory doesn't exist
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)

        config = SQLiteConfig(test_db_path)
        assert os.path.exists(test_dir)

        # Test engine creation
        engine = config.get_engine()
        engine.dispose()

    finally:
        # Cleanup
        if os.path.exists(test_dir):
            import shutil
            try:
                shutil.rmtree(test_dir)
            except PermissionError:
                pass
