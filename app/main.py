# app/main.py

import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.api.v1.router import router
from app.db.mongodb import connect_to_mongo, close_mongo_connection

def create_app() -> FastAPI:
    # Configure Loguru
    logger.remove()  # remove default handler
    logger.add(sys.stdout, level=settings.LOG_LEVEL or "INFO", enqueue=True, backtrace=True, diagnose=True)
    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            rotation="10 MB",
            retention="7 days",
            level=settings.LOG_LEVEL or "INFO",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Include API routes (Telegram webhook, etc.)
    app.include_router(router)

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        logger.debug("Health check requested")
        return {"status": "ok"}

    # HTTPException handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    # Catch-all exception handler
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.url.path}")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)

    # Startup & shutdown events for MongoDB
    app.add_event_handler("startup", connect_to_mongo)
    app.add_event_handler("shutdown", close_mongo_connection)

    return app

app = create_app()
