"""Application configuration loaded from environment variables."""

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://academic:academic@localhost:5432/profstack"

    @model_validator(mode="after")
    def fix_postgres_scheme(self) -> "Settings":
        # Railway (and Heroku) sometimes provide postgres:// which SQLAlchemy 2 rejects
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        return self

    # App
    app_env: str = "development"
    app_secret_key: str = "change-me"
    cors_origins: str = "http://localhost:3000"

    # Chatbot
    anthropic_api_key: str = ""

    # Notifications / email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    notification_email: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
