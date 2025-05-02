"""
Модуль ReprioritizerGraph: переприоритизация задач с учётом бизнес-приоритетов, ресурсов и текущего RoadMap.
Использует LangChain (OpenAI o4-mini) для расчёта новых дедлайнов и приоритетов.
"""

import json

from loguru import logger
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI

from app.core.config import settings
import app.db.mongodb as mongodb
from app.db.mongodb import TaskRepo


class ReprioritizerGraph:
    # Prompt для переприоритизации задач
    _template = """
У тебя есть обновлённая инициатива в формате JSON:

{initiative}

И полный список всех инициатив (RoadMap) в формате JSON:

{all_initiatives}

Бизнес-приоритеты компании (речь CEO):

{business_priorities}

Список доступных ресурсов (разработчики) в формате JSON:

{resources}

Пересчитай для данной инициативы и для всех потенциально затронутых задач новые поля:
- deadline (с учётом спринтов и возможных переносов)
- priority (urgent, high, important, medium, low, cancel)

Верни полный JSON обновлённой инициативы, включая изменённые дедлайны и приоритеты во всех вложенных блоках и задачах.
"""

    _prompt = PromptTemplate(
        template=_template,
        input_variables=[
            "initiative",
            "all_initiatives",
            "business_priorities",
            "resources",
        ],
    )

    _llm = OpenAI(
        model_name="o4-mini",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    _pipeline = _prompt | _llm

    @staticmethod
    async def run(nav_result: dict) -> dict:
        """
        Запускает RunnableSequence для переприоритизации указанной инициативы (nav_result).
        nav_result: {
            "initiative_id": str,
            "block_id": str,
            "updated_initiative": dict
        }
        Возвращает JSON с обновлённой инициативой.
        """
        try:
            # Текущая инициатива
            initiative = nav_result.get("updated_initiative", {})
            initiative_json = json.dumps(initiative, default=str, ensure_ascii=False)

            # Все RoadMap инициативы из БД
            all_docs = (
                await mongodb.db[TaskRepo.collection_name]
                .find({"type": "initiative"})
                .to_list(length=None)
            )
            all_json = json.dumps(all_docs, default=str, ensure_ascii=False)

            # Бизнес-приоритеты (предполагается коллекция business_priorities с полем speech)
            bp_doc = await mongodb.db["business_priorities"].find_one(
                sort=[("_id", -1)]
            )
            business_priorities = bp_doc.get("speech", "") if bp_doc else ""

            # Ресурсы разработчиков (предполагается коллекция resources)
            resources_docs = await mongodb.db["resources"].find().to_list(length=None)
            resources_json = json.dumps(resources_docs, default=str, ensure_ascii=False)

            # Вызов модели через RunnableSequence
            logger.debug(
                "ReprioritizerGraph input initiative: %s", initiative.get("id")
            )
            response = await ReprioritizerGraph._pipeline.arun(
                initiative=initiative_json,
                all_initiatives=all_json,
                business_priorities=business_priorities,
                resources=resources_json,
            )
            logger.debug("ReprioritizerGraph raw response: %s", response)
        except Exception as e:
            logger.exception("Error during ReprioritizerGraph run: %s", e)
            raise

        # Парсинг JSON-ответа
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            logger.error("ReprioritizerGraph returned invalid JSON: %s", response)
            raise ValueError("Invalid JSON from ReprioritizerGraph")

        return result
