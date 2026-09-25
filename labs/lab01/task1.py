
import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from shared.student import STUDENT_NAME, GROUP_NAME, VARIANT_NUMBER

passwords = [
    "password123", "Qwerty!2023", "admin", "MyP@ssw0rd", "123456",
    "SecurePass!", "test", "P@ssw0rd123", "welcome", "StrongP@ss1"
]

criteria = {
    "min_length": 8,
    "require_digits": True,
    "require_upper": True,
    "require_special": True
}

forbidden_passwords = {"password", "123456", "admin", "test", "welcome", "qwerty"}

# 3. Генерація 3 випадкових індексів та додавання дублікатів в кінець списку
random_indices = [random.randint(0, len(passwords) - 1) for _ in range(3)]
for idx in random_indices:
    passwords.append(passwords[idx])


# 4. Функція для оцінки надійності пароля
def evaluate_password(pwd: str, criteria_dict: dict, forbidden_set: set, full_list: list) -> str:
    min_len = criteria_dict["min_length"]

# Перевірка Заборонених
    if pwd in forbidden_set or len(pwd) < min_len:
        return "Заборонений"

# Наявність груп символів
    has_digit = any(c.isdigit() for c in pwd)
    has_upper = any(c.isupper() for c in pwd)
    has_lower = any(c.islower() for c in pwd)
    has_special = any(not c.isalnum() for c in pwd)

# Перевірка виконання обов'язкових критеріїв пароля
    meets_digits = has_digit if criteria_dict.get("require_digits") else True
    meets_upper = has_upper if criteria_dict.get("require_upper") else True
    meets_special = has_special if criteria_dict.get("require_special") else True
    meets_all_criteria = meets_digits and meets_upper and meets_special

    is_unique = full_list.count(pwd) == 1
    has_extended_len = len(pwd) >= (min_len + 4)

# Надійність пароля
    if meets_all_criteria and has_extended_len and is_unique:
        return "Дуже сильний"
    elif meets_all_criteria:
        return "Сильний"
    else:
        # Підрахунок кількості присутніх типів символів
        groups_count = sum([has_digit, has_upper, has_lower, has_special])
        if groups_count >= 2:
            return "Середній"
        else:
            return "Слабкий"

print(f"Студент: {STUDENT_NAME} | Група {GROUP_NAME} | Варіант: {VARIANT_NUMBER}  ")
print("=" * 68)
print(f"{'№':<3} | {'Пароль':<18} | {'Довжина':<8} | {'Унікальний':<10} | {'Категорія':<15}")
print("-" * 68)

for i, pwd in enumerate(passwords, start=1):
    category = evaluate_password(pwd, criteria, forbidden_passwords, passwords)
    is_unique_str = "Так" if passwords.count(pwd) == 1 else "Ні"
    print(f"{i:<3} | {pwd:<18} | {len(pwd):<8} | {is_unique_str:<10} | {category:<15}")