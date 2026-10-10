"""Репозиторий журнала действий.

Модуль содержит AuditLogRepository — CRUD для модели AuditLog
плюс фильтрация по пользователю, действию, сущности, дате.
"""

from datetime import date, datetime
from typing import List, Optional

from src.models.user import AuditLog
from src.repositories.base_repository import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Репозиторий для работы с журналом действий.

    Расширяет BaseRepository специфичными методами:
    - получение действий пользователя;
    - фильтрация по типу действия, сущности, дате.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели AuditLog."""
        super().__init__(AuditLog)

    def get_by_user(self, user_id: int) -> List[AuditLog]:
        """Возвращает действия пользователя.

        Args:
            user_id: ID пользователя.

        Returns:
            Список записей.
        """
        return (
            self.session.query(AuditLog)
            .filter_by(user_id=user_id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def get_by_action(self, action: str) -> List[AuditLog]:
        """Возвращает записи с указанным действием.

        Args:
            action: Тип действия (create, update, delete, login).

        Returns:
            Список записей.
        """
        return (
            self.session.query(AuditLog)
            .filter_by(action=action)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def get_by_entity(self, entity: str) -> List[AuditLog]:
        """Возвращает записи по указанной сущности.

        Args:
            entity: Сущность (Order, Client, User).

        Returns:
            Список записей.
        """
        return (
            self.session.query(AuditLog)
            .filter_by(entity=entity)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def get_by_date_range(self, start: date, end: date) -> List[AuditLog]:
        """Возвращает записи за период.

        Args:
            start: Начало периода.
            end: Конец периода.

        Returns:
            Список записей.
        """
        start_dt = datetime.combine(start, datetime.min.time())
        end_dt = datetime.combine(end, datetime.max.time())
        return (
            self.session.query(AuditLog)
            .filter(AuditLog.created_at.between(start_dt, end_dt))
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def get_recent(self, limit: int = 50) -> List[AuditLog]:
        """Возвращает последние записи журнала.

        Args:
            limit: Максимум записей.

        Returns:
            Список последних записей.
        """
        return (
            self.session.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
