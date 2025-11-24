from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional
import os

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Default to in-container path for Docker deployments
    database_url: str = Field(
        default="sqlite:////app/data/expenses.db",
        env="DATABASE_URL"
    )

    db_type: Optional[str] = "sqlite"
    db_host: Optional[str] = "localhost"
    db_port: Optional[str] = "5432"
    db_name: Optional[str] = "expenses"
    db_user: Optional[str] = "postgres"
    db_password: Optional[str] = ""

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        # Allow env vars to override .env file
        case_sensitive = False

    @classmethod
    def load_settings(cls) -> "Settings":
        return cls()


settings = Settings.load_settings()
