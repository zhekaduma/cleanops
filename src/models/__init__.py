"""ORM-модели CleanOps.

Пакет содержит все модели базы данных. Импорт моделей через этот
пакет гарантирует их регистрацию в метаданных SQLAlchemy — это
необходимо для создания таблиц.

Example:
    >>> from src.models import User, Order, Client
    >>> user = User(username="admin", ...)
"""

from src.models.base import ReprMixin, TimestampMixin
from src.models.checklist import ChecklistTask
from src.models.client import Client, ClientType, Object, ObjectType
from src.models.crew import Crew
from src.models.order import (
    CleaningType,
    Order,
    OrderItem,
    OrderStatus,
)
from src.models.payment import Payment, PaymentMethod, PaymentStatus
from src.models.service import Service, ServiceUnit
from src.models.user import AuditLog, User, UserRole

__all__ = [
    # Mixins
    "TimestampMixin",
    "ReprMixin",
    # Models
    "User",
    "AuditLog",
    "Client",
    "Object",
    "Service",
    "Crew",
    "Order",
    "OrderItem",
    "ChecklistTask",
    "Payment",
    # Constants
    "UserRole",
    "ClientType",
    "ObjectType",
    "ServiceUnit",
    "CleaningType",
    "OrderStatus",
    "PaymentMethod",
    "PaymentStatus",
]
