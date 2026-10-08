"""ORM-модели пользователей и журнала действий.

Модуль содержит две модели:
- User — пользователи системы (администратор, менеджер, клинер и т.д.).
- AuditLog — журнал действий пользователей (audit log).

Соответствует разделу ТЗ 4.1.2 (роли) и 4.1.5 (журналирование).
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base
from src.models.base import ReprMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.order import Order
    from src.models.payment import Payment


class UserRole:
    """Роли пользователей системы.

    Соответствует разделу ТЗ 4.1.2.

    Attributes:
        ADMIN: Администратор — полный доступ.
        MANAGER: Менеджер — приём заказов, назначение бригад.
        BRIGADIER: Бригадир — управление бригадой.
        CLEANER: Клинер — выполнение заказов.
        ACCOUNTANT: Бухгалтер — финансы и отчёты.
        OBSERVER: Наблюдатель — просмотр отчётов.
    """

    ADMIN = "admin"
    MANAGER = "manager"
    BRIGADIER = "brigadier"
    CLEANER = "cleaner"
    ACCOUNTANT = "accountant"
    OBSERVER = "observer"

    ALL = (ADMIN, MANAGER, BRIGADIER, CLEANER, ACCOUNTANT, OBSERVER)

    LABELS = {
        ADMIN: "Администратор",
        MANAGER: "Менеджер",
        BRIGADIER: "Бригадир",
        CLEANER: "Клинер",
        ACCOUNTANT: "Бухгалтер",
        OBSERVER: "Наблюдатель",
    }


class User(Base, TimestampMixin, ReprMixin):
    """Пользователь системы CleanOps.

    Представляет сотрудника клининговой компании, имеющего доступ к системе.
    Пароль хранится в виде bcrypt-хеша (см. раздел ТЗ 4.1.5).

    Attributes:
        user_id: Уникальный идентификатор.
        username: Логин для входа (уникальный).
        password_hash: Хеш пароля (bcrypt).
        full_name: ФИО сотрудника.
        phone: Телефон.
        email: Email (уникальный).
        role: Роль в системе (см. UserRole).
        is_active: Активен ли аккаунт.
        last_login: Время последнего входа.
        audit_logs: Журнал действий пользователя.
        orders: Заказы, созданные пользователем (как менеджером).
    """

    __tablename__ = "users"
    _repr_fields = ["user_id", "username", "role"]

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True,
        comment="Логин для входа",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Хеш пароля (bcrypt)",
    )
    full_name: Mapped[str] = mapped_column(
        String(150), nullable=False,
        comment="ФИО сотрудника",
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
        comment="Телефон",
    )
    email: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True,
        comment="Email",
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=UserRole.CLEANER,
        comment="Роль в системе",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Активен ли аккаунт",
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
        comment="Время последнего входа",
    )

    # Связи
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="manager",
        foreign_keys="Order.manager_id",
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="created_by_user",
        foreign_keys="Payment.created_by",
    )


class AuditLog(Base, ReprMixin):
    """Запись журнала действий пользователя.

    Соответствует разделу ТЗ 4.1.5 (журналирование) и 4.1.9 (логирование
    доступа к критичным данным).

    Attributes:
        log_id: Уникальный идентификатор записи.
        user_id: ID пользователя, совершившего действие.
        action: Тип действия (create, update, delete, login, ...).
        entity: Сущность, над которой выполнено действие (Order, Client, ...).
        entity_id: ID сущности.
        details: Детали в формате JSON-строки.
        ip_address: IP-адрес пользователя.
        created_at: Дата и время записи.
        user: Связь с пользователем.
    """

    __tablename__ = "audit_logs"
    _repr_fields = ["log_id", "user_id", "action", "entity"]

    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="ID пользователя",
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Тип действия (create/update/delete/login)",
    )
    entity: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Сущность (Order/Client/User/...)",
    )
    entity_id: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="ID сущности",
    )
    details: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Детали действия (JSON)",
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True,
        comment="IP-адрес (IPv4 или IPv6)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True,
        comment="Дата и время записи",
    )

    # Связи
    user: Mapped["User | None"] = relationship(back_populates="audit_logs")
