"""
Модуль для экспорта и обновления RoadMap в Google Sheets с помощью pygsheets.
"""

import os
from loguru import logger
import pygsheets
from typing import Dict, Any
from app.core.config import settings


def get_sheets_client() -> pygsheets.client.Client:
    # Ожидается, что JSON сервисного аккаунта передан в env-переменной
    credentials = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not credentials:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON env var is not set")
    return pygsheets.authorize(service_account_env_var="GOOGLE_SERVICE_ACCOUNT_JSON")


def update_roadmap_sheet(initiative: Dict[str, Any]) -> str:
    """
    Обновляет таблицу RoadMap для одной инициативы:
    - Очищает существующие данные
    - Пишет заголовки и плоский список задач с вложенностью
    Возвращает публичную ссылку на документ.
    """
    gc = get_sheets_client()
    spread = gc.open_by_key(settings.GOOGLE_SHEETS_ID)
    # Используем первый лист или по названию
    ws = spread.sheet1

    # Очистка листа
    ws.clear()

    # Подготовка данных для записи
    rows = [["ID", "Title", "Type", "Priority", "Deadline", "Executor", "Capacity"]]

    def flatten(item: Dict[str, Any], parent_path: str = ""):
        path = f"{parent_path} > {item['title']}" if parent_path else item["title"]
        rows.append(
            [
                item.get("id", ""),
                path,
                item.get("type", ""),
                item.get("priority", ""),
                item.get("deadline", ""),
                item.get("executor", ""),
                item.get("capacity", ""),
            ]
        )
        for sub in item.get("subtasks", []):
            flatten(sub, path)

    flatten(initiative)

    # Запись строк в лист
    ws.update_values("A1", rows)
    logger.info(f"Updated Google Sheet for initiative {initiative.get('id')}")
    return spread.url
