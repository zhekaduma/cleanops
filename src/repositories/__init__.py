"""Репозитории CleanOps.

Пакет содержит все репозитории для работы с БД через паттерн Repository
(см. ТЗ, раздел 1.2.2). Каждый репозиторий инкапсулирует SQL-запросы и
предоставляет типизированный интерфейс для работы с моделями.

Example:
    >>> from src.repositories import UserRepository, OrderRepository
    >>> user_repo = UserRepository()
    >>> user = user_repo.get_by_username("admin")
"""

from src.repositories.audit_repository import AuditLogRepository
from src.repositories.base_repository import BaseRepository
from src.repositories.checklist_repository import ChecklistTaskRepository
from src.repositories.client_repository import ClientRepository, ObjectRepository
from src.repositories.crew_repository import CrewRepository
from src.repositories.order_repository import (
    OrderItemRepository,
    OrderRepository,
)
from src.repositories.payment_repository import PaymentRepository
from src.repositories.service_repository import ServiceRepository
from src.repositories.user_repository import UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "ClientRepository",
    "ObjectRepository",
    "ServiceRepository",
    "CrewRepository",
    "OrderRepository",
    "OrderItemRepository",
    "ChecklistTaskRepository",
    "PaymentRepository",
    "AuditLogRepository",
]
