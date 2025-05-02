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
            logger.warning(f"Empty message payload: {payload}")
            return {"error": "Empty message"}

        # Пытаемся найти существующую задачу по title
        existing = await TaskRepo.find_by_title(text)
        if existing:
            logger.info(f"Found existing task: {existing.id}")
            return TaskResponse.from_mongo(existing).dict()

        # Новая задача: запускаем граф AI-агента
        logger.info(f"New task, invoking AI agent pipeline: {text}")
        updated_initiative = await AIAgent.process_new_task(text)

        # Сохраняем обновлённую инициативу (включая новые объекты)
        await TaskRepo.save_initiative(updated_initiative)

        # Возвращаем результат по новой задаче
        # Fetch the full initiative doc first
        initiative_doc = await TaskRepo.find_newest_by_initiative(
            updated_initiative["id"]
        )

        # Extract the newest task (assuming last task in last block)
        new_task_data = None
        if initiative_doc and initiative_doc.get("blocks"):
            last_block = initiative_doc["blocks"][-1]
            if last_block and last_block.get("tasks"):
                new_task_data = last_block["tasks"][-1]

        if not new_task_data:
            logger.error(
                f"Could not extract task data from initiative {updated_initiative['id']}"
            )
            # Handle error appropriately, maybe return the initiative itself or an error message
            return {"error": "Failed to extract task details after saving initiative."}

        # Prepare data for TaskResponse.from_mongo
        new_task_data["title"] = new_task_data.get("name")  # Map name to title
        new_task_data["_id"] = new_task_data.get(
            "id", "temp_task_id"
        )  # Use LLM ID as placeholder _id
        new_task_data["type"] = "task"  # Set the type explicitly
        new_task_data["initiative_id"] = str(
            initiative_doc["_id"]
        )  # Convert initiative ObjectId to string
        # Ensure block_id is also present if needed by TaskResponse (check TaskResponse model)
        # new_task_data["block_id"] = str(last_block.get("_id")) # Assuming last_block has _id

        return TaskResponse.from_mongo(new_task_data).dict()

    @staticmethod
    async def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
        """
        Возвращает задачу из БД по ID
        """
        doc = await TaskRepo.find_by_id(task_id)
        if not doc:
            return None
        return TaskResponse.from_mongo(doc)
