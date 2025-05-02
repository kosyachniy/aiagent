"""
Логика обработки задач: проверка существующих, создание/обновление и вызов ИИ-агента.
"""

from typing import Any, Dict, Optional

from loguru import logger

from app.db.mongodb import TaskRepo
from app.models.task import Task, TaskResponse
from app.services.ai_agent import AIAgent


class TaskManager:
    @staticmethod
    async def handle_telegram(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основная точка входа для обработки Telegram-пейлоада.
        Определяет, известна ли задача, и возвращает результат.
        """

        text = payload.get("message", {}).get("text", "").strip()
        if not text:
            logger.warning("Empty message payload: %s", payload)
            return {"error": "Empty message"}

        # Пытаемся найти существующую задачу по title
        existing = await TaskRepo.find_by_title(text)
        if existing:
            logger.info("Found existing task: %s", existing.id)
            return TaskResponse.from_mongo(existing).dict()

        # Новая задача: запускаем граф AI-агента
        logger.info("New task, invoking AI agent pipeline: %s", text)
        updated_initiative = await AIAgent.process_new_task(text)

        # Сохраняем обновлённую инициативу (включая новые объекты)
        await TaskRepo.save_initiative(updated_initiative)

        # Возвращаем результат по новой задаче
        new_task = TaskRepo.find_newest_by_initiative(updated_initiative.id)
        return TaskResponse.from_mongo(new_task).dict()

    @staticmethod
    async def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
        """
        Возвращает задачу из БД по ID
        """
        doc = await TaskRepo.find_by_id(task_id)
        if not doc:
            return None
        return TaskResponse.from_mongo(doc)
