"""
Модуль NavigatorGraph: определяет вложенность новой задачи в текущей дорожной карте.
Использует LangChain (OpenAI o4-mini) для анализа текста задачи и JSON текущих инициатив.
"""

import json
from loguru import logger
from langchain import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from app.core.config import settings
from app.db.mongodb import db, TaskRepo


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

    _llm = OpenAI(
        model_name="o4-mini",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    _chain = LLMChain(llm=_llm, prompt=_prompt)

    @staticmethod
    async def run(task_text: str) -> dict:
        """
        Выполняет LLMChain для определения вложенности задачи.
        Возвращает распарсенный JSON с инициативой и блоком.
        """
        # Извлекаем текущие инициативы из БД
        initiatives_docs = (
            await db[TaskRepo.collection_name]
            .find({"type": "initiative"})
            .to_list(length=None)
        )
        try:
            initiatives_json = json.dumps(
                initiatives_docs, default=str, ensure_ascii=False
            )
        except Exception as e:
            logger.exception("Error serializing initiatives: %s", e)
            initiatives_json = "[]"

        # Вызов модели
        try:
            logger.debug("NavigatorGraph input task: %s", task_text)
            response = await NavigatorGraph._chain.arun(
                task_text=task_text,
                initiatives=initiatives_json,
            )
            logger.debug("NavigatorGraph raw response: %s", response)
        except Exception as e:
            logger.exception("Error during NavigatorGraph run: %s", e)
            raise

        # Парсинг JSON-ответа
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            logger.error("NavigatorGraph returned invalid JSON: %s", response)
            raise ValueError("Invalid JSON from NavigatorGraph")

        return result
