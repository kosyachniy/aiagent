#!/usr/bin/env python3
"""
Скрипт для первоначального импорта всех инициатив из MongoDB в Google Sheets.
"""
import asyncio
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection, db, TaskRepo
from app.integrations.sheets import update_roadmap_sheet


async def migrate_all_initiatives():
    await connect_to_mongo()
    initiatives = (
        await db[TaskRepo.collection_name]
        .find({"type": "initiative"})
        .to_list(length=None)
    )
    print(f"Found {len(initiatives)} initiatives to migrate.")

    for init in initiatives:
        init_id = str(init.get("_id"))
        try:
            sheet_url = update_roadmap_sheet(init)
            print(f"Initiative {init_id} migrated successfully: {sheet_url}")
        except Exception as e:
            print(f"Error migrating initiative {init_id}: {e}")

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(migrate_all_initiatives())
