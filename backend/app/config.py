from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

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
        # Read from environment variables only
        case_sensitive = False

    @classmethod
    def load_settings(cls) -> "Settings":
        return cls()


settings = Settings.load_settings()
