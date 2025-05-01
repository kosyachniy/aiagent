import pytest
from app.integrations.sheets import flatten, update_roadmap_sheet


@pytest.fixture
def sample_initiative():
    return {
        "id": "1",
        "title": "Initiative",
        "type": "initiative",
        "priority": "high",
        "deadline": "2025-06-01",
        "executor": "dev1",
        "capacity": 40,
        "subtasks": [
            {
                "id": "2",
                "title": "Block1",
                "type": "block",
                "priority": "medium",
                "deadline": "2025-06-08",
                "executor": "dev2",
                "capacity": 20,
                "subtasks": [],
            }
        ],
    }


def test_flatten_structure(sample_initiative):
    rows = []
    # import flatten from sheets module
    from app.integrations.sheets import flatten as _flatten

    _flatten(sample_initiative, rows)
    # Header + one block + root
    assert any(row[1].endswith("Initiative") for row in rows)
    assert any("Block1" in row[1] for row in rows)
