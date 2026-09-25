import hashlib
import csv
import json
import os
import sys
from datetime import datetime
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from shared.student import STUDENT_NAME, GROUP_NAME, VARIANT_NUMBER

print(f"Студент: {STUDENT_NAME} | Група {GROUP_NAME} | Варіант: {VARIANT_NUMBER}  ")
PERSONAL_SALT = f"{VARIANT_NUMBER:05d}"
MIN_PASSWORD_LENGTH = 12

CSV_FILE = r"C:\Users\Sabakin\PycharmProjects\python-labs\labs\lab01\data\users.csv"
JSON_LOG_FILE = r"C:\Users\Sabakin\PycharmProjects\python-labs\labs\lab01\data\log.json"

users_db = []


class ValidationError(Exception):
    pass


# Хешування
def generate_hash(password: str, salt: str = "00000") -> str:
    if not password or not salt:
        raise ValueError("Пароль або сіль не можуть бути порожніми (None або \"\").")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Пароль коротший за мінімальну довжину ({MIN_PASSWORD_LENGTH} символів).")

    data = password + salt
    return hashlib.sha3_512(data.encode('utf-8')).hexdigest()


# Реєстрація користувачів
users_to_register = (
    ("admin", "SuperSecureAdminPass1"),
    ("john_doe", "JohnDoePass12345"),
    ("jane_smith", "JaneSmithPass987"),
    ("user_4", "PasswordForUser4"),
    ("test_user", "TestPassword1234"),
    ("student1", "StudentPass12345"),
    ("developer", "DevPassword9876"),
    ("manager", "ManagerPass12345"),
    ("guest", "GuestPassword123"),
    ("support", "SupportPass12345")
)


def create_user(username, password):
    hash_value = generate_hash(password, PERSONAL_SALT)
    return (username, hash_value)


# Перенесли обробку файлових помилок сюди
def create_users(users_list):
    try:
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for username, password in users_list:
                user_data = create_user(username, password)
                writer.writerow(user_data)
    except (PermissionError, IOError) as e:
        print(f"Помилка запису у CSV-файл ({CSV_FILE}): {e}")


# Перенесли обробку файлових помилок сюди
def read_db():
    global users_db
    users_db = []

    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and len(row) == 2:
                    users_db.append(tuple(row))
    except (FileNotFoundError,PermissionError, IOError) as e:
        print(f"Помилка читання CSV-файлу ({CSV_FILE}): {e}")
        return

    print(f"{'Логін':<15} | {'Хеш пароля'}")
    print("-" * 145)
    for user, pwd_hash in users_db:
        print(f"{user:<15} | {pwd_hash}")


# Перенесли обробку файлових помилок запису логів сюди
def log_event(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        username = args[0] if args else kwargs.get('username', 'unknown')
        result_status = "failure"

        try:
            result = func(*args, **kwargs)
            result_status = "success" if result else "failure"
            return result
        except Exception as e:
            result_status = "failure"
            raise e
        finally:
            log_entry = {
                "event": "login",
                "user": username,
                "result": result_status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": list(args),
                "kwargs": kwargs
            }

            try:
                logs = []
                if os.path.exists(JSON_LOG_FILE):
                    with open(JSON_LOG_FILE, "r", encoding="utf-8") as f:
                        try:
                            logs = json.load(f)
                        except json.JSONDecodeError:
                            logs = []

                logs.append(log_entry)
                with open(JSON_LOG_FILE, "w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=4, ensure_ascii=False)
            except (PermissionError, IOError) as e:
                print(f"Помилка запису логу у JSON ({JSON_LOG_FILE}): {e}")

    return wrapper


@log_event
def login(username: str, password: str) -> bool:
    if not username or not password:
        raise ValueError("Логін або пароль не можуть бути порожніми.")

    input_hash = generate_hash(password, PERSONAL_SALT)

    for db_user, db_hash in users_db:
        if db_user == username and db_hash == input_hash:
            return True
    return False

# Тепер main() чистий і відповідає лише за логіку виконання кроків
def main():
    print("=== 1. Додавання 10 користувачів у існуючий CSV ===")
    create_users(users_to_register)
    print("Успішно!\n")

    print("=== 2. Зчитування бази даних (CSV) ===")
    read_db()
    print("\n=== 3. Робимо 10 спроб входу (запишуться у JSON) ===")

    attempts = [
        ("admin", "SuperSecureAdminPass1"),
        ("john_doe", "JohnDoePass12345"),
        ("jane_smith", "WrongPassword123456"),
        ("user_4", "PasswordForUser4"),
        ("test_user", "TestPassword1234"),
        ("student1", "Short1"),
        ("developer", "DevPassword9876"),
        ("unknown_guy", "SomePassword12345"),
        ("", "Password123456"),
        ("support", "SupportPass12345")
    ]

    for i, (usr, pwd) in enumerate(attempts, 1):
        try:
            result = login(usr, pwd)
            status = "Успішний вхід" if result else "Відмовлено (невірні дані)"
            print(f"Спроба {i:02d} | Логін: {usr or '<пустий>':<12} -> {status}")
        except ValueError as e:
            print(f"Спроба {i:02d} | Логін: {usr or '<пустий>':<12} -> Перехоплено ValueError: {e}")
        except ValidationError as e:
            print(f"Спроба {i:02d} | Логін: {usr or '<пустий>':<12} -> Перехоплено ValidationError: {e}")


if __name__ == "__main__":
    main()