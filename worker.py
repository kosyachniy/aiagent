import os
from dramatiq import set_broker
from dramatiq.brokers.redis import RedisBroker

# Конфигурация брокера Redis через переменные окружения
# По умолчанию подключаемся к localhost:6379 или к сервису 'redis'
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
broker = RedisBroker(url=redis_url)
set_broker(broker)

# Импорт воркеров, чтобы зарегистрировать все actors
import tasks.tasks  # noqa: F401
