from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional
import os

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    secret_key: str = Field(default="", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = Field("sqlite:///./data/expenses.db", env="DATABASE_URL")

    db_type: Optional[str] = "sqlite"
    db_host: Optional[str] = "localhost"
    db_port: Optional[str] = "5432"
    db_name: Optional[str] = "expenses"
    db_user: Optional[str] = "postgres"
    db_password: Optional[str] = ""

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def load_settings(cls) -> "Settings":
        return cls()


settings = Settings.load_settings()

# Only validate SECRET_KEY if not in test environment
if not settings.secret_key and not os.getenv("PYTEST_CURRENT_TEST"):
    raise ValueError("SECRET_KEY must be set in environment variables or .env file")
