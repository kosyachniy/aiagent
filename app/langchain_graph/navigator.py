"""
Модуль NavigatorGraph: определяет вложенность новой задачи в текущей дорожной карте.
Использует LangChain (OpenAI o4-mini) для анализа текста задачи и JSON текущих инициатив.
"""

import json

from loguru import logger
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings
import app.db.mongodb as mongodb
from app.db.mongodb import TaskRepo


class NavigatorGraph:
    # Prompt для определения, куда вставить задачу
    _template = """
У тебя есть новая задача:

{task_text}

И текущая дорожная карта (RoadMap) в формате JSON (список инициатив):

{initiatives}

Определи, в какую инициативу (initiative_id) и блок (block_id) следует поместить задачу.
Если нужно, создай новую инициативу или новый блок.
Верни результат в формате JSON со следующими полями:
{{
  "initiative_id": "<ID существующей или нового элемента>",
  "block_id": "<ID существующего или нового блока>",
  "updated_initiative": {{ /* полный объект инициативы с вложенными блоками и задачами */ }}
}}
"""

    _prompt = PromptTemplate(
        template=_template,
        input_variables=["task_text", "initiatives"],
    )

    _llm = ChatOpenAI(
        model_name="o4-mini",
        # temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    _pipeline = _prompt | _llm | StrOutputParser()

    @staticmethod
    async def run(task_text: str) -> dict:
        """
        Запускает RunnableSequence для определения вложенности задачи.
        Возвращает распарсенный JSON с инициативой и блоком.
        """
        # Извлекаем текущие инициативы из БД
        initiatives_docs = (
            await mongodb.db[TaskRepo.collection_name]
            .find({"type": "initiative"})
            .to_list(length=None)
        )
        try:
            initiatives_json = json.dumps(
                initiatives_docs, default=str, ensure_ascii=False
            )
        except Exception as e:
            logger.exception(f"Error serializing initiatives: {e}")
            initiatives_json = "[]"

        # Вызов модели через RunnableSequence
        try:
            logger.debug(f"NavigatorGraph input task: {task_text}")
            response = await NavigatorGraph._pipeline.ainvoke(
                {"task_text": task_text, "initiatives": initiatives_json}
            )
            logger.debug(f"NavigatorGraph raw response: {response}")
        except Exception as e:
            logger.exception(f"Error during NavigatorGraph run: {e}")
            raise

        # Парсинг JSON-ответа
        try:
            # Remove potential markdown code fences
            if response.startswith("```json"):
                response = response.removeprefix("```json\n").removesuffix("\n```")
            elif response.startswith("```"):
                response = response.removeprefix("```\n").removesuffix("\n```")

            result = json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"NavigatorGraph returned invalid JSON: {response}")
            raise ValueError("Invalid JSON from NavigatorGraph")

        return result
