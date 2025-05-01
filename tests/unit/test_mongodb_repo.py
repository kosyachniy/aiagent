import pytest
from bson import ObjectId
from app.db.mongodb import TaskRepo, db


@pytest.mark.asyncio
async def test_find_by_id_not_found(monkeypatch):
    # Simulate None return
    monkeypatch.setattr(db[TaskRepo.collection_name], "find_one", lambda *_: None)
    result = await TaskRepo.find_by_id("invalidid")
    assert result is None
