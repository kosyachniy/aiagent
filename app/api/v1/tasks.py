from fastapi import APIRouter, Request, HTTPException
from loguru import logger
from app.core.config import settings
from app.services.task_manager import TaskManager
from app.models.task import TaskResponse

router = APIRouter()


@router.post("/webhook/{bot_token}", response_model=dict)
async def telegram_webhook(bot_token: str, request: Request):
    """
    Обрабатывает входящие вебхуки от Telegram.
    Проверяет токен, вызывает логику TaskManager и возвращает результат.
    """
    if bot_token != settings.BOT_TOKEN:
        logger.warning("Invalid bot token: %s", bot_token)
        raise HTTPException(status_code=403, detail="Invalid bot token")

    payload = await request.json()
    result = await TaskManager.handle_telegram(payload)
    return {"ok": True, "result": result}


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    Возвращает информацию по задаче по её ID.
    """
    task = await TaskManager.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
