import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "DATAGUARD AI - Data Migration Validation System"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dataguard-ai-secret-key-2026-gpt4o-insurtech")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database: Default SQLite for zero-config portability, configurable for SQL Server / PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dataguard.db")

    # OpenAI GPT-4o Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 800

    # File Storage Paths (local or Azure Blob Storage compatible)
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./storage/uploads")
    REPORT_DIR: str = os.getenv("REPORT_DIR", "./storage/reports")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORT_DIR, exist_ok=True)

