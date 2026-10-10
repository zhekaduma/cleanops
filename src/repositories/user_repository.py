"""Репозиторий пользователей.

Модуль содержит UserRepository — CRUD-операции для модели User
плюс специфичные методы: поиск по username, по email, по роли.
"""

from typing import List, Optional

from src.models.user import User, UserRole
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями.

    Расширяет BaseRepository специфичными методами:
    - поиск по username и email;
    - фильтрация по роли;
    - работа с активными пользователями.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели User."""
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Находит пользователя по логину.

        Args:
            username: Логин пользователя.

        Returns:
            Пользователь или None, если не найден.
        """
        return self.session.query(User).filter_by(username=username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Находит пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            Пользователь или None, если не найден.
        """
        return self.session.query(User).filter_by(email=email).first()

    def get_by_role(self, role: str) -> List[User]:
        """Возвращает список пользователей с указанной ролью.

        Args:
            role: Роль (см. UserRole).

        Returns:
            Список пользователей.
        """
        return self.session.query(User).filter_by(role=role).all()

    def get_active(self) -> List[User]:
        """Возвращает всех активных пользователей.

        Returns:
            Список активных пользователей.
        """
        return self.session.query(User).filter_by(is_active=True).all()

    def username_exists(self, username: str) -> bool:
        """Проверяет, занят ли логин.

        Args:
            username: Логин для проверки.

        Returns:
            True если логин уже занят.
        """
        return self.get_by_username(username) is not None

    def email_exists(self, email: str) -> bool:
        """Проверяет, занят ли email.

        Args:
            email: Email для проверки.

        Returns:
            True если email уже занят.
        """
        return self.get_by_email(email) is not None

    def get_managers(self) -> List[User]:
        """Возвращает список менеджеров.

        Returns:
            Список пользователей с ролью manager.
        """
        return self.get_by_role(UserRole.MANAGER)
