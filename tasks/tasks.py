import asyncio
import dramatiq
from loguru import logger
from telegram import Bot

from app.core.config import settings
from app.services.ai_agent import AIAgent
from app.db.mongodb import TaskRepo
from app.integrations.sheets import update_roadmap_sheet
from app.integrations.tracker import get_tracker_link

# Set up broker from REDIS_URL environment in worker.py or use default
# broker = RedisBroker(url=os.getenv("REDIS_URL"))
# dramatiq.set_broker(broker)
import dramatiq as _dramatiq  # noqa: F401


@dramatiq.actor(max_retries=3, min_backoff=10000, max_backoff=60000)
def process_new_task(task_text: str, chat_id: int):
    """
    Фоновая обработка новой задачи:
    1. Навигация и переприоритизация через AI-агент
    2. Сохранение обновлённой инициативы в БД
    3. Обновление Google Sheets
    4. Отправка сообщения в Telegram с результатом
    """
    logger.info(f'[process_new_task] Start for chat_id={chat_id}, task="{task_text}"')

    async def pipeline():
        updated = await AIAgent.process_new_task(task_text)
        await TaskRepo.save_initiative(updated)
        return updated

    try:
        updated_initiative = asyncio.run(pipeline())
    except Exception as e:
        logger.exception(f"Error in AI pipeline: {e}")
        raise

    try:
        sheet_url = update_roadmap_sheet(updated_initiative)
    except Exception as e:
        logger.exception(f"Error updating Google Sheets: {e}")
        sheet_url = None

    bot = Bot(token=settings.BOT_TOKEN)
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
    Обновление листа Google Sheets по инициативе.
    Если передан chat_id — отправка ссылки в Telegram.
    """
    logger.info(f"[update_sheet] Initiative {initiative_id}")

    async def fetch():
        return await TaskRepo.find_by_id(initiative_id)

    initiative = asyncio.run(fetch())
    if not initiative:
        logger.error(f"Initiative {initiative_id} not found")
        return

    try:
        sheet_url = update_roadmap_sheet(initiative)
    except Exception as e:
        logger.exception(f"Error updating sheet: {e}")
        sheet_url = None

    if chat_id:
        bot = Bot(token=settings.BOT_TOKEN)
        msg = f"Обновлён RoadMap: {sheet_url or 'ошибка'}"
        try:
            bot.send_message(chat_id=chat_id, text=msg)
            logger.info(f"Sheet URL sent to chat {chat_id}")
        except Exception:
            logger.exception(f"Failed to send sheet URL to {chat_id}")
