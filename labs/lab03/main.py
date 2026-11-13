"""FastAPI-застосунок ЛР №3."""

import logging
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from labs.lab03 import config, repository
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records
from shared import student

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Створити відсутні таблиці під час запуску."""
    initialize_database()
    yield


app = FastAPI(
    title=f"ЛР №3: {config.DOMAIN}",
    description=f"{config.DESCRIPTION} Одиниця вимірювання: {config.UNIT}. "
    f"Поріг: {config.THRESHOLD}.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(categories.router)
app.include_router(records.router)


@app.exception_handler(repository.NotFoundError)
async def not_found_handler(_: Request, exc: repository.NotFoundError) -> JSONResponse:
    """404 для відсутніх записів і категорій."""
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(repository.ConflictError)
async def conflict_handler(_: Request, exc: repository.ConflictError) -> JSONResponse:
    """409 для дублікатів і непорожніх категорій."""
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(sqlite3.Error)
async def sqlite_handler(_: Request, exc: sqlite3.Error) -> JSONResponse:
    """500 без технічних деталей; деталі — у лог."""
    logger.exception("Помилка бази даних: %s", exc)
    return JSONResponse(
        status_code=500, content={"detail": "Внутрішня помилка сервера"}
    )


@app.get("/ping", summary="Перевірка доступності", tags=["service"])
def ping() -> dict[str, str]:
    """Повернути стан API."""
    return {"status": "ok"}


@app.get("/student", summary="Дані студента", tags=["service"])
def get_student() -> dict[str, str | int]:
    """Повернути дані з shared/student.py (підлаштуйте імена змінних)."""
    return {
        "student_name": student.STUDENT_NAME,
        "group_name": student.GROUP_NAME,
        "variant_number": student.VARIANT_NUMBER,
    }
