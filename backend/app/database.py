import os
from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from abc import ABC, abstractmethod

from .models import Base
from .config import settings

# Use settings.database_url if present; otherwise compose from db pieces (fallback)
DATABASE_URL = settings.database_url


class DatabaseConfig(ABC):
    @abstractmethod
    def get_engine(self):
        raise NotImplementedError


class SQLiteConfig(DatabaseConfig):
    def __init__(self, db_path: str = "./data/expenses.db"):
        self.db_path = db_path
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        data_dir = os.path.dirname(self.db_path)
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)

    def get_engine(self):
        database_url = f"sqlite:///{self.db_path}"
        return create_engine(database_url, connect_args={"check_same_thread": False}, future=True)


class PostgreSQLConfig(DatabaseConfig):
    def __init__(self, url: str):
        self.url = url

    def get_engine(self):
        return create_engine(self.url, future=True)


class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, future=True)
        self._create_tables()

    def _create_tables(self):
        # For simple local apps using SQLite this is fine; for production use migrations (Alembic)
        Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Generator[Session, None, None]:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Factory: pick engine from settings.database_url
if DATABASE_URL.startswith("sqlite"):
    # try to extract path from URL (sqlite:///./data/expenses.db)
    # fallback to default path
    db_path = DATABASE_URL.replace("sqlite:///", "")
    config = SQLiteConfig(db_path=db_path)
    engine = config.get_engine()
else:
    # For postgres and others, use the full URL
    config = PostgreSQLConfig(url=DATABASE_URL)
    engine = config.get_engine()

db_manager = DatabaseManager(engine)
get_db = db_manager.get_db
