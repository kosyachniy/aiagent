"""
Интеграция с LangChain и LangGraph: навигатор + переприоритизатор.
"""

from typing import Dict
from loguru import logger
from bson import ObjectId
from app.langchain_graph.navigator import NavigatorGraph
from app.langchain_graph.reprioritizer import ReprioritizerGraph


class AIAgent:
    @staticmethod
    async def process_new_task(task_text: str) -> Dict:
        """
        Запускает два графа: навигатор (определение вложенности)
        и переприоритизатор (вычисление новых дедлайнов/приоритетов).
        Возвращает обновлённую json-структуру инициативы.
        """
        # Шаг 1: Навигатор определяет, куда вставить задачу
        logger.debug(f"Running NavigatorGraph for task: {task_text}")
        nav_result = await NavigatorGraph.run(task_text)

        # Шаг 2: Переприоритизация с учётом ресурсов и бизнес-приоритетов
        logger.debug(
            f"Running ReprioritizerGraph for initiative: {nav_result.get('initiative_id')}"
        )
        reprio_result = await ReprioritizerGraph.run(nav_result)

        # Итоговый JSON инициативы
        updated_initiative = reprio_result
        raw_id = updated_initiative.get("id")
        if isinstance(raw_id, str) and not ObjectId.is_valid(raw_id):
            logger.warning(
                f"Generated ID '{raw_id}' is not a valid ObjectId. Generating new one."
            )
            updated_initiative["id"] = str(ObjectId())
        elif raw_id is None:
            logger.warning(f"Initiative ID is missing. Generating new one.")
            updated_initiative["id"] = str(ObjectId())

        return updated_initiative
