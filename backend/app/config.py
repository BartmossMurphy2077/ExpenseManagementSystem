from pydantic import BaseSettings, Field
from pathlib import Path
from typing import Optional
import os

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # required
    secret_key: str = Field(..., env="SECRET_KEY")

    # JWT
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database URL, prefer DATABASE_URL if provided
    database_url: str = Field("sqlite:///./data/expenses.db", env="DATABASE_URL")

    # Backwards-compatible database pieces if someone uses them
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
        # Pydantic BaseSettings automatically reads from env and the env_file declared above.
        # Keeping a loader for explicitness and for tests.
        return cls()


settings = Settings.load_settings()

if not settings.secret_key:
    raise ValueError("SECRET_KEY must be set in environment variables or .env file")
