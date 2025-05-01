import pytest
from app.services.task_manager import TaskManager
from app.db.mongodb import TaskRepo


class DummyTaskDoc:
    def __init__(self, title):
        self.id = "123"
        self.title = title


@pytest.mark.asyncio
async def test_handle_empty_message(monkeypatch):
    payload = {"message": {"text": ""}}
    result = await TaskManager.handle_telegram(payload)
    assert "error" in result and result["error"] == "Empty message"


@pytest.mark.asyncio
async def test_handle_existing_task(monkeypatch):
    payload = {"message": {"text": "TestTask"}}
    # Mock TaskRepo.find_by_title
    monkeypatch.setattr(TaskRepo, "find_by_title", lambda title: DummyTaskDoc(title))
    result = await TaskManager.handle_telegram(payload)
    assert result.get("id") == "123"
    assert result.get("title") == "TestTask"
