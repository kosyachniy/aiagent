"""
Модуль для генерации ссылок на задачи в Yandex Tracker.
"""

from app.core.config import settings


def get_tracker_link(issue_id: str) -> str:
    """
    Формирует URL к задаче в Yandex Tracker по её ID.
    """
    base = settings.YANDEX_TRACKER_BASE_URL.rstrip("/")
    return f"{base}/issues/{issue_id}"
