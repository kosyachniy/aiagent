"""
Клиент MongoDB и репозиторий для работы с задачами.
"""

from typing import Optional
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger
from app.core.config import settings

# Global client and database reference
global client, db
client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    """Open connection to MongoDB and initialize 'db'."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    logger.info(f"Connected to MongoDB: {settings.MONGO_URI}")


async def close_mongo_connection() -> None:
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


class TaskRepo:
    collection_name = "tasks"

    @staticmethod
    async def find_by_title(title: str) -> Optional[dict]:
        """Поиск задачи по заголовку"""
        return await db[TaskRepo.collection_name].find_one({"title": title})

    @staticmethod
    async def find_by_id(task_id: str) -> Optional[dict]:
        """Поиск документа по _id"""
        try:
            oid = ObjectId(task_id)
        except Exception:
            return None
        return await db[TaskRepo.collection_name].find_one({"_id": oid})

    @staticmethod
    async def save_initiative(initiative: dict) -> None:
        """Сохранение (upsert) инициативы с вложенными блоками и задачами"""
        raw_id = initiative.get("id") or initiative.get("_id")
        oid = ObjectId(raw_id) if isinstance(raw_id, str) else raw_id
        initiative_copy = initiative.copy()
        initiative_copy["_id"] = oid
        # удалим внешнее поле id, если есть
        initiative_copy.pop("id", None)
        await db[TaskRepo.collection_name].replace_one(
            {"_id": oid}, initiative_copy, upsert=True
        )
        logger.debug(f"Initiative saved: {oid}")

    @staticmethod
    async def find_newest_by_initiative(initiative_id: str) -> Optional[dict]:
        """Находит самую новую задачу в рамках инициативы по дате создания или ObjectId"""
        try:
            oid = ObjectId(initiative_id)
        except Exception:
            return None
        cursor = (
            db[TaskRepo.collection_name]
            .find({"initiative_id": oid})
            .sort("_id", -1)
            .limit(1)
        )
        results = await cursor.to_list(length=1)
        return results[0] if results else None
