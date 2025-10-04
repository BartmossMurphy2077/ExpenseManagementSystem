# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from abc import ABC, abstractmethod
from typing import Generator
import os
from .models import Base


class DatabaseConfig(ABC):
    @abstractmethod
    def get_engine(self):
        pass


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
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )


class PostgreSQLConfig(DatabaseConfig):
    def __init__(self, host: str, port: str, database: str, username: str, password: str):
        self.connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

    def get_engine(self):
        return create_engine(self.connection_string)


class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.engine = config.get_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()

    def _create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Generator[Session, None, None]:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Default configuration
db_manager = DatabaseManager(SQLiteConfig())
get_db = db_manager.get_db
