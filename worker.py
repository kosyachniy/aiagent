import os

from loguru import logger
from dramatiq import set_broker, Worker
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Retries

# Configure Redis broker from environment variable
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
broker = RedisBroker(url=redis_url)

# Attach retry middleware for dramatiq actors
broker.add_middleware(Retries())

# Set the configured broker as default
set_broker(broker)

# Register tasks
import tasks.tasks  # noqa: F401

# Launch worker to consume tasks
if __name__ == "__main__":
    import os, sys
    from dramatiq.cli import main

    # Ensure broker URL is set
    os.environ.setdefault(
        "DRAMATIQ_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379")
    )
    # Build CLI args: module name and optional flags
    sys.argv = ["dramatiq", "tasks.tasks", "--processes", "1", "--threads", "4"]
    main()
