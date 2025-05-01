"""
Инициализация и настройка логирования (Loguru).
"""

import sys
from loguru import logger
from app.core.config import settings


def init_logging() -> None:
    """
    Конфигурирует Loguru: вывод в stdout и файл при необходимости.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            rotation="10 MB",
            retention="7 days",
            level=settings.LOG_LEVEL,
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
