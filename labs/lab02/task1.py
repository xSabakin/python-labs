import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

PBKDF2_ITERATIONS = 100_000
SESSION_TIMEOUT_SEC = 900

EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9_. -]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


class User:
    def __init__(
        self,
        username: str,
        email: str,
        role: str,
        password: str,
        active: bool = True,
    ):
        self.username = username
        self.email = email  # Викличе сеттер з валідацією
        self.role = role
        self.active = active
        self.__password_hash = b""
        self.__password_salt = b""
        self.set_password(password)

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str) or not EMAIL_PATTERN.match(value):
            raise ValueError("Некоректний формат email")
        self._email = value

    def set_password(self, password: str) -> None:
        if not isinstance(password, str) or not password:
            raise ValueError("Пароль не може бути порожнім")

        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__password_salt,
            PBKDF2_ITERATIONS,
        )

    def check_password(self, password: str) -> bool:
        if not isinstance(password, str):
            return False

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__password_salt,
            PBKDF2_ITERATIONS,
        )
        return hmac.compare_digest(self.__password_hash, password_hash)

    def deactivate(self) -> None:
        self.active = False

    def __str__(self) -> str:
        status = "active" if self.active else "inactive"
        return (
            f"User(username={self.username}, email={self.email}, "
            f"role={self.role}, status={status})"
        )


class Admin(User):
    def __init__(
        self,
        username: str,
        email: str,
        role: str,
        password: str,
        active: bool = True,
        permissions: set[str] | None = None,
    ):
        super().__init__(username, email, role, password, active)
        self.permissions = set(permissions or set())

    def grant_permission(self, permission: str) -> None:
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self) -> str:
        permissions = ", ".join(sorted(self.permissions)) or "none"
        return f"{super().__str__()}, permissions=[{permissions}]"


class Session:
    def __init__(
        self,
        ip: str,
        login_time: datetime | None = None,
        last_activity: datetime | None = None,
    ):
        now = datetime.now(timezone.utc)
        self.ip = ip
        self.login_time = login_time or now
        self.last_activity = last_activity or self.login_time

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("Таймаут має бути додатним")
        elapsed = datetime.now(timezone.utc) - self.last_activity
        return elapsed <= timedelta(seconds=timeout_sec)


@dataclass
class AuditEntry:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self):
        self.entries: list[AuditEntry] = []

    def add_log(self, username: str, action: str) -> None:
        self.entries.append(
            AuditEntry(
                timestamp=datetime.now(timezone.utc),
                username=username,
                action=action,
            )
        )

    def show_all(self) -> None:
        for entry in self.entries:
            timestamp = entry.timestamp.isoformat(timespec="seconds")
            print(f"{timestamp} | {entry.username} | {entry.action}")


class UserAccount:
    def __init__(
        self,
        user: User,
        session: Session | None = None,
        audit_log: AuditLog | None = None,
    ):
        self.user = user
        self.session = session
        self.audit_log = audit_log or AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        if (
            username != self.user.username
            or not self.user.active
            or not self.user.check_password(password)
        ):
            self.audit_log.add_log(username, "login_failure")
            return False

        self.session = Session(ip)
        self.session.touch()
        self.audit_log.add_log(username, "login_success")
        return True

    def is_authenticated(self) -> bool:
        return (
            self.user.active
            and self.session is not None
            and self.session.is_active(SESSION_TIMEOUT_SEC)
        )

    def logout(self) -> None:
        if self.session is not None:
            self.audit_log.add_log(self.user.username, "logout")
            self.session = None

    def __getitem__(self, key: str):
        if key not in {"user", "session", "audit_log"}:
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value) -> None:
        expected_types = {
            "user": (User,),
            "session": (Session, type(None)),
            "audit_log": (AuditLog,),
        }
        if key not in expected_types:
            raise KeyError(key)
        if not isinstance(value, expected_types[key]):
            raise TypeError(f"Некоректний тип значення для ключа {key}")
        setattr(self, key, value)


def demo() -> None:
    audit_log = AuditLog()
    admin = Admin(
        username="admin_user",
        email="admin_2026@example.com",
        role="administrator",
        password="SecureLab2#3",
    )
    account = UserAccount(admin, audit_log=audit_log)

    print(f"Студент: {STUDENT_NAME} | Група {GROUP_NAME} | Варіант: {VARIANT_NUMBER}  ")

    print("=== Вхід до системи ===")
    print(
        "Невдалий вхід:",
        account.login("admin_user", "WrongPassword", "192.168.1.10"),
    )
    print(
        "Успішний вхід:",
        account.login("admin_user", "SecureLab2#3", "192.168.1.10"),
    )
    print("Автентифіковано:", account.is_authenticated())

    print("\n=== Email та права адміністратора ===")
    admin.email = "new_admin@example.com"
    print("Новий email:", admin.email)
    try:
        admin.email = "wrong-email"
    except ValueError as error:
        print("Помилка email:", error)

    admin.grant_permission("firewall.audit")
    admin.grant_permission("users.manage")
    admin.revoke_permission("users.manage")
    print(admin)
    print("Доступ firewall.audit:", admin.has_permission("firewall.audit"))

    print("\n=== Завершення сеансу за таймаутом ===")
    session = account["session"]
    session.last_activity -= timedelta(seconds=SESSION_TIMEOUT_SEC + 1)
    print("Автентифіковано після таймауту:", account.is_authenticated())

    account.login("admin_user", "SecureLab2#3", "192.168.1.10")
    account.logout()
    print("Автентифіковано після виходу:", account.is_authenticated())

    print("\n=== Журнал аудиту ===")
    audit_log.show_all()


if __name__ == "__main__":
    demo()
