"""
Configuration from environment using Pydantic v2-settings.
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine which .env file to load
_env_file = (
    ".env.development"
    if os.path.exists(".env.development")
    else ".env.production" if os.path.exists(".env.production") else ".env"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_file, env_file_encoding="utf-8", extra="ignore"
    )

    PROJECT_NAME: str = "AI Planner"
    PROJECT_VERSION: str = "0.1.0"
    BOT_TOKEN: str
    MONGO_URI: str = "mongodb://localhost:27017/aiagent"
    MONGO_DB_NAME: str = "aiagent"
    OPENAI_API_KEY: str
    GOOGLE_SHEETS_ID: str
    YANDEX_TRACKER_BASE_URL: str
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str | None = None


# Load settings
settings = Settings()
