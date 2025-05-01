import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection, db, TaskRepo
from app.services.task_manager import TaskManager


@pytest.fixture(autouse=True, scope="module")
async def test_db_setup_and_teardown():
    """
    Fixture для настройки тестовой БД и её очистки.
    """
    # Переключаемся на тестовую БД
    settings.MONGO_DB_NAME = "ai_planner_test"
    # Подключаемся
    await connect_to_mongo()
    # Очищаем коллекции перед тестами
    await db.drop_collection(TaskRepo.collection_name)
    await db.drop_collection("business_priorities")
    await db.drop_collection("resources")
    yield
    # Очищаем после тестов
    await db.drop_collection(TaskRepo.collection_name)
    await db.drop_collection("business_priorities")
    await db.drop_collection("resources")
    # Закрываем соединение
    await close_mongo_connection()


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_webhook_invalid_token():
    payload = {"message": {"text": "Test"}}
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        resp = await client.post(f"/webhook/invalid_token", json=payload)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Invalid bot token"


@pytest.mark.asyncio
async def test_webhook_existing_task(monkeypatch):
    # Подготовка: вставляем документ задачи в БД
    doc = {"title": "ExistingTask", "type": "task", "priority": "medium"}
    insert = await db[TaskRepo.collection_name].insert_one(doc)

    # Мокаем отправку в Telegram ниже, но здесь проверяем ответ сразу из TaskManager
    async def fake_find_by_title(title):
        return await db[TaskRepo.collection_name].find_one({"title": title})

    monkeypatch.setattr(TaskRepo, "find_by_title", fake_find_by_title)

    payload = {"message": {"text": "ExistingTask"}}
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        resp = await client.post(f"/webhook/{settings.BOT_TOKEN}", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("result", {}).get("title") == "ExistingTask"


@pytest.mark.asyncio
async def test_get_task_not_found():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        resp = await client.get(
            f"/tasks/507f1f77bcf86cd799439011"
        )  # несуществующий ObjectId
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Task not found"
