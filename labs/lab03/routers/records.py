"""Маршрути записів."""

from typing import Annotated

from fastapi import APIRouter, Body, Path, Query, Response, status

from labs.lab03 import config, repository
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace, Status

router = APIRouter(prefix="/records", tags=["records"])

NOT_FOUND = {404: {"description": "Запис або категорію не знайдено"}}
CONFLICT = {409: {"description": "Запис із таким code вже існує"}}


@router.get("", response_model=list[RecordRead], summary="Список записів")
def list_records(
    category_id: Annotated[
        int | None, Query(gt=0, description="Лише записи цієї категорії")
    ] = None,
    status_filter: Annotated[
        Status | None, Query(alias="status", description="Лише з цим статусом")
    ] = None,
    min_value: Annotated[
        float | None,
        Query(
            ge=config.VALUE_MIN,
            le=config.VALUE_MAX,
            description="value >= min_value",
        ),
    ] = None,
    q: Annotated[
        str | None,
        Query(min_length=1, max_length=120, description="Підрядок у title"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Макс. кількість")] = 20,
    offset: Annotated[int, Query(ge=0, description="Скільки пропустити")] = 0,
) -> list[dict]:
    """Список записів із фільтрами (AND), сортування за id."""
    return repository.list_records(
        category_id=category_id,
        status=status_filter,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/bulk",
    response_model=list[RecordRead],
    status_code=status.HTTP_201_CREATED,
    summary="Пакетне створення записів",
    responses={**NOT_FOUND, **CONFLICT},
)
def create_records_bulk(
    body: Annotated[list[RecordCreate], Body(min_length=1, max_length=100)],
) -> list[dict]:
    """Атомарно створити від 1 до 100 записів."""
    return repository.create_records_bulk([item.model_dump() for item in body])


@router.get(
    "/{record_id}",
    response_model=RecordRead,
    summary="Отримати запис",
    responses=NOT_FOUND,
)
def get_record(
    record_id: Annotated[int, Path(gt=0, description="Ідентифікатор запису")],
) -> dict:
    """Повернути один запис."""
    return repository.get_record(record_id)


@router.post(
    "",
    response_model=RecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити запис",
    responses={**NOT_FOUND, **CONFLICT},
)
def create_record(body: RecordCreate) -> dict:
    """Створити запис."""
    return repository.create_record(body.model_dump())


@router.put(
    "/{record_id}",
    response_model=RecordRead,
    summary="Замінити запис",
    responses={**NOT_FOUND, **CONFLICT},
)
def replace_record(
    record_id: Annotated[int, Path(gt=0, description="Ідентифікатор запису")],
    body: RecordReplace,
) -> dict:
    """Повністю замінити змінювані поля запису."""
    return repository.replace_record(record_id, body.model_dump())


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити запис",
    responses=NOT_FOUND,
)
def delete_record(
    record_id: Annotated[int, Path(gt=0, description="Ідентифікатор запису")],
) -> Response:
    """Видалити запис."""
    repository.delete_record(record_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
