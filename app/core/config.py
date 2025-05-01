"""
Чтение конфигурации из окружения через Pydantic BaseSettings.
"""

from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Planner"
    PROJECT_VERSION: str = "0.1.0"
    BOT_TOKEN: str
    MONGO_URI: str
    MONGO_DB_NAME: str = "ai_planner"
    OPENAI_API_KEY: str
    GOOGLE_SHEETS_ID: str
    YANDEX_TRACKER_BASE_URL: str
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
