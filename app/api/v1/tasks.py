from datetime import datetime

from fastapi import APIRouter, Request, HTTPException
from loguru import logger

from app.core.config import settings
from app.services.task_manager import TaskManager
from app.models.task import TaskResponse
import app.db.mongodb as mongodb


router = APIRouter()


@router.post("/webhook/{bot_token}")
async def telegram_webhook(bot_token: str, request: Request):
    """
    Обрабатывает входящие вебхуки от Telegram.
    Если это команда, сразу отвечаем.
    Иначе запускаем асинхронный pipeline через TaskManager.
    """

    if bot_token != settings.BOT_TOKEN:
        logger.warning(f"Invalid bot token: {bot_token}")
        raise HTTPException(status_code=403, detail="Invalid bot token")

    payload = await request.json()
    message = payload.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()

    # Handle slash-commands immediately via inline response
    if text.startswith("/") and chat_id:
        reply = (
            "👋 Welcome to AI Planner Bot!\n"
            "Send me a task description and I'll prioritize it."
        )
        # Return inline method for Telegram to send
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": reply,
        }

    # Otherwise, let TaskManager decide
    try:
        result = await TaskManager.handle_telegram(payload)
    except Exception as e:
        logger.exception(f"Error handling Telegram webhook: {e}")
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": "⚠️ Error",
        }

    # If TaskManager returned a sync reply (error/info), send it now
    if isinstance(result, dict) and result.get("message") and chat_id:
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": result["message"],
        }

    # For new tasks, the background worker will send the response
    return {"ok": True}


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    Возвращает информацию по задаче по её ID.
    """
    task = await TaskManager.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/admin/business-priority", tags=["admin"])
async def set_priority(data: dict):
    """
    {"speech": "New CEO speech text…"}
    """
    speech = data.get("speech")
    if not speech:
        raise HTTPException(status_code=400, detail="'speech' field required")
    doc = {"speech": speech, "created_at": datetime.utcnow()}
    insertion = await mongodb.db["business_priorities"].insert_one(doc)
    if not insertion.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to insert")
    return {"ok": True, "id": str(insertion.inserted_id)}
