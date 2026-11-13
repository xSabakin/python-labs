from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from labs.lab03 import config

Status = Literal["new", "in_progress", "done"]

if config.VALUE_IS_INTEGER:
    ValueType = Annotated[int, Field(ge=config.VALUE_MIN, le=config.VALUE_MAX)]
else:
    ValueType = Annotated[
        float,
        Field(ge=config.VALUE_MIN, le=config.VALUE_MAX, allow_inf_nan=False),
    ]


class CategoryCreate(BaseModel):
    """Тіло запиту створення категорії."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=2, max_length=40)


class CategoryRead(CategoryCreate):
    """Категорія у відповіді."""

    id: int


class RecordCreate(BaseModel):
    """Тіло запиту створення запису."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    code: str = Field(min_length=3, max_length=40)
    title: str = Field(min_length=3, max_length=120)
    category_id: int = Field(gt=0)
    value: ValueType
    status: Status


class RecordReplace(RecordCreate):
    """Тіло запиту повної заміни запису (усі поля обов’язкові)."""


class RecordRead(RecordCreate):
    """Запис у відповіді."""

    id: int
    category_name: str
