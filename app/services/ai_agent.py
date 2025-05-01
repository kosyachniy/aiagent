"""
Интеграция с LangChain и LangGraph: навигатор + переприоритизатор.
"""

from typing import Dict
from loguru import logger
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
        logger.debug("Running NavigatorGraph for task: %s", task_text)
        nav_result = await NavigatorGraph.run(task_text)

        # Шаг 2: Переприоритизация с учётом ресурсов и бизнес-приоритетов
        logger.debug(
            "Running ReprioritizerGraph for initiative: %s",
            nav_result.get("initiative_id"),
        )
        reprio_result = await ReprioritizerGraph.run(nav_result)

        # Итоговый JSON инициативы
        return reprio_result
