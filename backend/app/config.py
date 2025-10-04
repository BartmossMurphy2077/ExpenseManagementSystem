from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./data/expenses.db"

    # Database specific settings
    db_type: str = "sqlite"
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "expenses"
    db_user: str = "postgres"
    db_password: str = ""

    class Config:
        env_file = Path(__file__).parent.parent / ".env"

    @classmethod
    def load_settings(cls):
        # Load from .env file first, then from environment variables
        base_dir = Path(__file__).resolve().parent.parent
        dotenv_path = base_dir / ".env"

        if dotenv_path.exists():
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=dotenv_path)

        return cls()


settings = Settings.load_settings()

# Validate required settings
if not settings.secret_key:
    raise ValueError("SECRET_KEY must be set in environment variables or .env file")
