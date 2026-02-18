"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://academic:academic@localhost:5432/profstack"

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
