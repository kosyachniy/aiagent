from mongo_migrate import Migrator
from app.core.config import settings

migrator = Migrator(
    url=settings.MONGO_URI,
    database=settings.MONGO_DB_NAME,
    collection="migrations",  # where run history is stored
)
