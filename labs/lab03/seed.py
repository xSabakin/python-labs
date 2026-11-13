import json
import sqlite3
from contextlib import closing
from pathlib import Path

from pydantic import ValidationError

from labs.lab03.database import get_connection, initialize_database
from labs.lab03.schemas import CategoryCreate, RecordCreate

SEED_PATH = Path(__file__).resolve().parent / "data" / "seed.json"
EXPECTED_CATEGORIES = 3
EXPECTED_RECORDS = 8


def load_seed() -> tuple[list[dict], list[dict]]:
    """Прочитати та перевірити початкові дані."""
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    categories, records = payload["categories"], payload["records"]
    if len(categories) != EXPECTED_CATEGORIES or len(records) != EXPECTED_RECORDS:
        raise ValueError("Очікується 3 категорії та 8 записів")
    for category in categories:
        CategoryCreate(name=category["name"])
        if not isinstance(category["id"], int) or category["id"] <= 0:
            raise ValueError("id категорії має бути додатним цілим")
    for record in records:
        RecordCreate(**record)
    return categories, records


def seed() -> None:
    """Заповнити порожню базу в одній транзакції."""
    initialize_database()
    try:
        categories, records = load_seed()
    except (OSError, ValueError, KeyError, ValidationError) as exc:
        print(f"Некоректні початкові дані: {exc}")
        return

    with closing(get_connection()) as connection:
        count = connection.execute(
            "SELECT (SELECT COUNT(*) FROM categories) + (SELECT COUNT(*) FROM records)"
        ).fetchone()[0]
        if count:
            print("База вже містить дані — заповнення пропущено.")
            return
        try:
            with connection:
                connection.executemany(
                    "INSERT INTO categories (id, name) VALUES (:id, :name)",
                    categories,
                )
                connection.executemany(
                    "INSERT INTO records (code, title, category_id, value, status) "
                    "VALUES (:code, :title, :category_id, :value, :status)",
                    records,
                )
        except sqlite3.Error as exc:
            print(f"Помилка заповнення, зміни скасовано: {exc}")
            return
    print(f"Додано {len(categories)} категорії та {len(records)} записів.")


if __name__ == "__main__":
    seed()
