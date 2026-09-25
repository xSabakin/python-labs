
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from shared.student import STUDENT_NAME, GROUP_NAME, VARIANT_NUMBER

print(f"Студент: {STUDENT_NAME} | Група {GROUP_NAME} | Варіант: {VARIANT_NUMBER}  ")

users = {
    "admin001": {"role": "administrator", "clearance": 4, "department": "IT", "active": True},
    "user123": {"role": "analyst", "clearance": 2, "department": "Security", "active": True},
    "guest789": {"role": "guest", "clearance": 1, "department": "External", "active": True},
    "manager456": {"role": "manager", "clearance": 3, "department": "Operations", "active": True},
    "contractor99": {"role": "contractor", "clearance": 1, "department": "External", "active": False}
}

resources = [
    ("database_backup", 4), ("user_logs", 2), ("public_docs", 1),
    ("financial_reports", 3), ("system_config", 4), ("training_materials", 1),
    ("security_policies", 3), ("audit_logs", 4), ("employee_data", 3),
    ("temp_files", 1)
]

security_levels = ("Public", "Internal", "Confidential", "Secret")
blocked_users = {"contractor99", "temp_user", "suspended_acc"}

# 2. Сортування ресурсів за числом від 1 до 4
resources_sorted = sorted(resources, key=lambda x: x[1])

def check_access(user_id: str, resource_tuple: tuple) -> str:
    res_name, res_level = resource_tuple

    u_str = f"{user_id:<12}"
    r_str = f"{res_name:<19}"

    if user_id not in users:
        return f"user=[{u_str}] resource=[{r_str}] -> DENY (Користувача не існує)"

    if user_id in blocked_users:
        return f"user=[{u_str}] resource=[{r_str}] -> DENY (Заблокований)"

    user_info = users[user_id]

    if not user_info.get("active", True):
        return f"user=[{u_str}] resource=[{r_str}] -> DENY (Користувач не активний)"

    if user_info["clearance"] >= res_level:
        return f"user=[{u_str}] resource=[{r_str}] -> ALLOW"
    else:
        return f"user=[{u_str}] resource=[{r_str}] -> DENY (Немає прав достопу)"

print("═" * 78)

all_test_users = list(users.keys()) + list(blocked_users - set(users.keys()))

print("Ресурси (ВІД 1 ДО 4)")
for res_name, level in resources_sorted:
    level_text = security_levels[level - 1]
    print(f"- {res_name:<20} | Рівень: {level} ({level_text})")

for user_id in all_test_users:
    print("═" * 78)

    if user_id in users:
        u = users[user_id]

        # Визначаємо статус
        if user_id in blocked_users:
            status = "Заблокований"
        elif not u.get("active", True):
            status = "Неактивний "
        else:
            status = "Активний"

        print(f"КОРИСТУВАЧ: {user_id}")
        print(f"Роль: {u['role']:<13} | Допуск: {u['clearance']} | Відділ: {u['department']:<10} | Статус: {status}")
    else:
        print(f"КОРИСТУВАЧ: {user_id}")
        print("Статус: Відсутній у базі даних (Невідомий акаунт)")

    print("─" * 78)

    for res in resources_sorted:
        print(check_access(user_id, res))

    print()