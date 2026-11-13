"""Параметри варіанта. Змініть значення за таблицею свого варіанта."""

VARIANT_NUMBER = 1
DOMAIN = "Реєстр вразливостей вебзастосунку"
DESCRIPTION = (
    "Облік знахідок перевірки вебзастосунку. Категорія — компонент системи, "
    "value — навчальна оцінка небезпеки (score), status — стан опрацювання."
)
UNIT = "score"
THRESHOLD = 7.0

CATEGORY_NAMES = ["web", "api", "database"]
TITLE_PREFIX = "Знахідка вебаудиту"
VALUES = [9.1, 5.4, 3.2, 7.5, 8.0, 2.4, 6.3, 7.1]

# Обмеження value: для варіантів 7-9 VALUE_MAX = None, для 4-6 VALUE_IS_INTEGER = True.
VALUE_MIN = 0
VALUE_MAX: float | None = 10
VALUE_IS_INTEGER = False

ALLOWED_STATUSES = ("new", "in_progress", "done")
