import asyncio
import dramatiq
from loguru import logger
from telegram import Bot

from app.core.config import settings
from app.services.ai_agent import AIAgent
from app.db.mongodb import TaskRepo
from app.integrations.sheets import update_roadmap_sheet
from app.integrations.tracker import get_tracker_link


dramatiq.set_broker(dramatiq.get_broker())

@dramatiq.actor(max_retries=3, retry_delay=10000)
def process_new_task(task_text: str, chat_id: int):
    """
    Фоновая обработка новой задачи:
    1. Навигация и переприоритизация через AI-агент
    2. Сохранение обновлённой инициативы в БД
    3. Обновление Google Sheets
    4. Отправка сообщения в Telegram с результатом
    """
    logger.info(f"[process_new_task] Start for chat_id={chat_id}, task="{task_text}" )")

    async def pipeline():
        # Запустить полный пайплайн AI-агента
        updated = await AIAgent.process_new_task(task_text)
        # Сохранить в MongoDB
        await TaskRepo.save_initiative(updated)
        return updated

    try:
        updated_initiative = asyncio.run(pipeline())
    except Exception as e:
        logger.exception("Error in AI pipeline: %s", e)
        raise

    # Обновить Google Sheets и получить ссылку
    try:
        sheet_url = update_roadmap_sheet(updated_initiative)
    except Exception as e:
        logger.exception("Error updating Google Sheets: %s", e)
        sheet_url = None

    # Сформировать ответ и отправить в Telegram
    bot = Bot(token=settings.BOT_TOKEN)
    # Пример текста, можно расширить
    text = (
        f"Новая задача обработана.\n"
        f"Инициатива: {updated_initiative.get('title')}\n"
        f"Ссылка на Google Sheets: {sheet_url or 'ошибка'}"
    )
    try:
        bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Message sent to chat {chat_id}")
    except Exception:
        logger.exception(f"Failed to send Telegram message to {chat_id}")


@dramatiq.actor
def update_sheet(initiative_id: str, chat_id: int = None):
    """
    Обновление листа Google Sheets по инициативе (может вызываться отдельно).
    Если передан chat_id, вышлет ссылку в Telegram.
    """
    logger.info(f"[update_sheet] Initiative {initiative_id}")

    async def fetch():
        doc = await TaskRepo.find_by_id(initiative_id)
        return doc

    initiative = asyncio.run(fetch())
    if not initiative:
        logger.error(f"Initiative {initiative_id} not found")
        return

    try:
        sheet_url = update_roadmap_sheet(initiative)
    except Exception as e:
        logger.exception("Error updating sheet: %s", e)
        sheet_url = None

    if chat_id:
        bot = Bot(token=settings.BOT_TOKEN)
        msg = f"Обновлён RoadMap: {sheet_url or 'ошибка'}"
        try:
            bot.send_message(chat_id=chat_id, text=msg)
            logger.info(f"Sheet URL sent to chat {chat_id}")
        except Exception:
            logger.exception(f"Failed to send sheet URL to {chat_id}")
