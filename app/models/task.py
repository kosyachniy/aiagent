from typing import List, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class TaskType(str, Enum):
    initiative = "initiative"
    block = "block"
    task = "task"


class Priority(str, Enum):
    urgent = "urgent"
    high = "high"
    important = "important"
    medium = "medium"
    low = "low"
    cancel = "cancel"


class Task(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
    )

    id: str = Field(..., alias="_id")
    title: str
    data: Optional[str]
    customer: Optional[str]
    executor: Optional[str]
    deadline: Optional[datetime]
    capacity: Optional[int]
    priority: Priority
    type: TaskType
    subtasks: List["Task"] = []


# Для рекурсивных ссылок
Task.update_forward_refs()


class TaskResponse(BaseModel):
    id: str
    title: str
    data: Optional[str]
    customer: Optional[str]
    executor: Optional[str]
    deadline: Optional[datetime]
    capacity: Optional[int]
    priority: Priority
    type: TaskType
    # Родительские связи (при необходимости)
    initiative_id: Optional[str]
    block_id: Optional[str]
    # Ссылки на внешние системы
    sheets_link: Optional[str]
    tracker_link: Optional[str]

    @classmethod
    def from_mongo(cls, doc: dict) -> "TaskResponse":
        """
        Преобразует документ MongoDB в модель ответа.
        Ожидается, что в doc уже есть поля initiative_id, block_id, sheets_link, tracker_link.
        """
        return cls(
            id=str(doc.get("_id")),
            title=doc.get("title"),
            data=doc.get("data"),
            customer=doc.get("customer"),
            executor=doc.get("executor"),
            deadline=doc.get("deadline"),
            capacity=doc.get("capacity"),
            priority=doc.get("priority"),
            type=doc.get("type"),
            initiative_id=doc.get("initiative_id"),
            block_id=doc.get("block_id"),
            sheets_link=doc.get("sheets_link"),
            tracker_link=doc.get("tracker_link"),
        )
