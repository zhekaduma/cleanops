"""Сервис авторизации и управления пользователями.

Модуль реализует бизнес-логику авторизации (см. ТЗ, F-7.1, 4.1.5):
- проверка логина/пароля через bcrypt;
- хеширование паролей;
- смена пароля;
- журналирование действий пользователя (audit log).
"""

from datetime import datetime
from typing import Optional

import bcrypt

from src.models.user import AuditLog, User
from src.repositories.audit_repository import AuditLogRepository
from src.repositories.user_repository import UserRepository


class AuthResult:
    """Результат попытки входа.

    Attributes:
        success: Успешна ли авторизация.
        user: Пользователь, если вход успешен.
        message: Сообщение об ошибке или успехе.
    """

    def __init__(
        self,
        success: bool,
        user: Optional[User] = None,
        message: str = "",
    ) -> None:
        """Инициализирует результат авторизации."""
        self.success = success
        self.user = user
        self.message = message


class AuthService:
    """Сервис авторизации.

    Отвечает за вход/выход пользователей, хеширование паролей и
    журналирование действий. Использует bcrypt (см. ТЗ, 4.1.5).
    """

    def __init__(self) -> None:
        """Инициализирует сервис с репозиториями."""
        self.user_repo = UserRepository()
        self.audit_repo = AuditLogRepository()

    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширует пароль через bcrypt.

        Args:
            password: Пароль в открытом виде.

        Returns:
            Хеш пароля (строка).
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Проверяет пароль против хеша.

        Args:
            password: Пароль в открытом виде.
            password_hash: Хеш из БД.

        Returns:
            True если пароль совпадает.
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8"),
            )
        except (ValueError, TypeError):
            return False

    def login(self, username: str, password: str) -> AuthResult:
        """Авторизует пользователя.

        Args:
            username: Логин.
            password: Пароль.

        Returns:
            AuthResult с пользователем или сообщением об ошибке.
        """
        user = self.user_repo.get_by_username(username)

        if user is None:
            return AuthResult(False, message="Неверный логин или пароль")

        if not user.is_active:
            return AuthResult(False, message="Учётная запись заблокирована")

        if not self.verify_password(password, user.password_hash):
            return AuthResult(False, message="Неверный логин или пароль")

        # Обновляем время последнего входа
        user.last_login = datetime.now()
        self.user_repo.session.commit()

        # Пишем в журнал
        self.log_action(
            user_id=user.user_id,
            action="login",
            entity="User",
            entity_id=user.user_id,
            details=f'{{"username": "{username}"}}',
        )

        return AuthResult(True, user=user, message="Успешный вход")

    def logout(self, user: User) -> None:
        """Выполняет выход пользователя.

        Args:
            user: Пользователь.
        """
        self.log_action(
            user_id=user.user_id,
            action="logout",
            entity="User",
            entity_id=user.user_id,
        )

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> bool:
        """Меняет пароль пользователя.

        Args:
            user_id: ID пользователя.
            old_password: Старый пароль.
            new_password: Новый пароль.

        Returns:
            True если пароль изменён.
        """
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            return False

        if not self.verify_password(old_password, user.password_hash):
            return False

        user.password_hash = self.hash_password(new_password)
        self.user_repo.session.commit()

        self.log_action(
            user_id=user_id,
            action="update",
            entity="User",
            entity_id=user_id,
            details='{"field": "password"}',
        )
        return True

    def create_user(
        self,
        username: str,
        password: str,
        full_name: str,
        role: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> Optional[User]:
        """Создаёт нового пользователя.

        Args:
            username: Логин.
            password: Пароль (будет захеширован).
            full_name: ФИО.
            role: Роль (см. UserRole).
            email: Email.
            phone: Телефон.
            created_by: ID создателя (для audit log).

        Returns:
            Созданный пользователь или None при ошибке.
        """
        if self.user_repo.username_exists(username):
            return None

        user = self.user_repo.create(
            username=username,
            password_hash=self.hash_password(password),
            full_name=full_name,
            role=role,
            email=email,
            phone=phone,
            is_active=True,
        )

        self.log_action(
            user_id=created_by or user.user_id,
            action="create",
            entity="User",
            entity_id=user.user_id,
            details=f'{{"username": "{username}", "role": "{role}"}}',
        )
        return user

    def log_action(
        self,
        user_id: Optional[int],
        action: str,
        entity: Optional[str] = None,
        entity_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Пишет действие в журнал.

        Args:
            user_id: ID пользователя.
            action: Тип действия.
            entity: Сущность.
            entity_id: ID сущности.
            details: Детали (JSON).
            ip_address: IP-адрес.

        Returns:
            Созданная запись журнала.
        """
        return self.audit_repo.create(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )
