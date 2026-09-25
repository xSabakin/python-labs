import hashlib
import csv
import json
import os
import sys
from datetime import datetime
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from shared.student import STUDENT_NAME, GROUP_NAME, VARIANT_NUMBER

# Параметри Варіанту 1
print(f"Студент: {STUDENT_NAME} | Група {GROUP_NAME} | Варіант: {VARIANT_NUMBER}  ")
PERSONAL_SALT = f"{VARIANT_NUMBER:05d}"
MIN_PASSWORD_LENGTH = 12

# ТУТ ВКАЖИ ШЛЯХИ ДО ТВОЇХ ІСНУЮЧИХ ФАЙЛІВ
CSV_FILE = r"C:\Users\Sabakin\PycharmProjects\python-labs\labs\lab01\data\users.csv"
JSON_LOG_FILE = r"C:\Users\Sabakin\PycharmProjects\python-labs\labs\lab01\data\log.json"

users_db = []


class ValidationError(Exception):
    pass


# --- 1. Хешування ---
def generate_hash(password: str, salt: str = "00000") -> str:
    if not password or not salt:
        raise ValueError("Пароль або сіль не можуть бути порожніми (None або \"\").")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Пароль коротший за мінімальну довжину ({MIN_PASSWORD_LENGTH} символів).")

    data = password + salt
    return hashlib.sha3_512(data.encode('utf-8')).hexdigest()


# --- 3. Реєстрація користувачів (10 записів) ---
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


def create_users(users_list):
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"Файл {CSV_FILE} не знайдено!")

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for username, password in users_list:
            user_data = create_user(username, password)
            writer.writerow(user_data)


# --- 4. Читання бази даних ---
def read_db():
    global users_db
    users_db = []

    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"Файл {CSV_FILE} не знайдено!")

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if row and len(row) == 2:
                users_db.append(tuple(row))

    print(f"{'Логін':<15} | {'Хеш пароля'}")
    print("-" * 145)
    for user, pwd_hash in users_db:
        print(f"{user:<15} | {pwd_hash}")


# --- 6. Логування подій (Декоратор) ---
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
            raise e  # Прокидаємо помилку далі, щоб зловити її в main()
        finally:
            log_entry = {
                "event": "login",
                "user": username,
                "result": result_status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": list(args),
                "kwargs": kwargs
            }

            if not os.path.exists(JSON_LOG_FILE):
                raise FileNotFoundError(f"Файл {JSON_LOG_FILE} не знайдено!")

            with open(JSON_LOG_FILE, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []

            logs.append(log_entry)

            with open(JSON_LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=4, ensure_ascii=False)

    return wrapper


# --- 5. Автентифікація ---
@log_event
def login(username: str, password: str) -> bool:
    if not username or not password:
        raise ValueError("Логін або пароль не можуть бути порожніми.")

    # Якщо пароль закороткий, generate_hash кине ValidationError, який ми зловимо в main()
    input_hash = generate_hash(password, PERSONAL_SALT)

    for db_user, db_hash in users_db:
        if db_user == username and db_hash == input_hash:
            return True
    return False


# --- 7. та 8. Головна функція з обробкою винятків ---
def main():
    try:
        print("=== 1. Додавання 10 користувачів у існуючий CSV ===")
        create_users(users_to_register)
        print("Успішно!\n")

        print("=== 2. Зчитування бази даних (CSV) ===")
        read_db()
        print("\n=== 3. Робимо 10 спроб входу (запишуться у JSON) ===")

        # Рівно 10 спроб, які згенерують 10 логів у log.json
        attempts = [
            ("admin", "SuperSecureAdminPass1"),  # 1. Успіх
            ("john_doe", "JohnDoePass12345"),  # 2. Успіх
            ("jane_smith", "WrongPassword123456"),  # 3. Невірний пароль (відмовлено)
            ("user_4", "PasswordForUser4"),  # 4. Успіх
            ("test_user", "TestPassword1234"),  # 5. Успіх
            ("student1", "Short1"),  # 6. Короткий пароль -> викличе ValidationError
            ("developer", "DevPassword9876"),  # 7. Успіх
            ("unknown_guy", "SomePassword12345"),  # 8. Неіснуючий юзер (відмовлено)
            ("", "Password123456"),  # 9. Пустий логін -> викличе ValueError
            ("support", "SupportPass12345")  # 10. Успіх
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

    # Перехоплення помилок роботи з файлами (вимоги Кроку 7)
    except (FileNotFoundError, PermissionError, IOError) as e:
        print(f"Помилка при роботі з файлами: {e}")
    except Exception as e:
        print(f"Непередбачена помилка: {e}")


if __name__ == "__main__":
    main()