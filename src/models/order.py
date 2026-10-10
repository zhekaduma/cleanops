"""ORM-модели заказа и позиций заказа.

Модуль содержит две модели:
- Order — заказ на уборку.
- OrderItem — позиция заказа (дополнительная услуга).

Соответствует разделу ТЗ 4.2.1 (калькулятор) и 4.2.4 (распределение бригад).
"""

from datetime import date, datetime, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base
from src.models.base import ReprMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.checklist import ChecklistTask
    from src.models.client import Client, Object
    from src.models.crew import Crew
    from src.models.payment import Payment
    from src.models.service import Service
    from src.models.user import User


class CleaningType:
    """Тип уборки.

    Attributes:
        MAINTENANCE: Поддерживающая уборка.
        GENERAL: Генеральная уборка.
        POST_RENOVATION: Уборка после ремонта.
        WINDOWS: Мойка окон.
    """

    MAINTENANCE = "maintenance"
    GENERAL = "general"
    POST_RENOVATION = "post_renovation"
    WINDOWS = "windows"

    ALL = (MAINTENANCE, GENERAL, POST_RENOVATION, WINDOWS)
    LABELS = {
        MAINTENANCE: "Поддерживающая",
        GENERAL: "Генеральная",
        POST_RENOVATION: "После ремонта",
        WINDOWS: "Мойка окон",
    }


class OrderStatus:
    """Статус заказа.

    Соответствует разделу ТЗ 4.2.4 (канбан-доска).
    """

    NEW = "new"
    CALCULATED = "calculated"
    CONFIRMED = "confirmed"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAID = "paid"
    CANCELLED = "cancelled"

    ALL = (NEW, CALCULATED, CONFIRMED, ASSIGNED, IN_PROGRESS, COMPLETED, PAID, CANCELLED)
    LABELS = {
        NEW: "Новый",
        CALCULATED: "Рассчитан",
        CONFIRMED: "Подтверждён",
        ASSIGNED: "Назначен",
        IN_PROGRESS: "В работе",
        COMPLETED: "Завершён",
        PAID: "Оплачен",
        CANCELLED: "Отменён",
    }


class Order(Base, TimestampMixin, ReprMixin):
    """Заказ на уборку.

    Центральная сущность системы. Содержит все параметры заказа:
    клиент, объект, тип уборки, площадь, коэффициенты, итоговую стоимость.

    Attributes:
        order_id: Уникальный идентификатор.
        client_id: ID клиента.
        object_id: ID объекта уборки.
        crew_id: ID назначенной бригады (может быть NULL).
        manager_id: ID менеджера, создавшего заказ.
        status: Статус заказа (см. OrderStatus).
        cleaning_type: Тип уборки (см. CleaningType).
        area: Площадь уборки в м².
        urgency_coef: Коэффициент срочности.
        dirt_coef: Коэффициент загрязнения.
        discount: Скидка в рублях.
        total_price: Итоговая стоимость.
        planned_date: Планируемая дата уборки.
        planned_start: Планируемое время начала.
        planned_end: Планируемое время окончания.
        actual_start: Фактическое время начала.
        actual_end: Фактическое время окончания.
        notes: Заметки.
    """

    __tablename__ = "orders"
    _repr_fields = ["order_id", "status", "total_price"]

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.client_id", ondelete="RESTRICT"),
        nullable=False, index=True,
        comment="ID клиента",
    )
    object_id: Mapped[int] = mapped_column(
        ForeignKey("objects.object_id", ondelete="RESTRICT"),
        nullable=False, index=True,
        comment="ID объекта уборки",
    )
    crew_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("crews.crew_id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="ID назначенной бригады",
    )
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="ID менеджера",
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=OrderStatus.NEW, index=True,
        comment="Статус заказа",
    )
    cleaning_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default=CleaningType.MAINTENANCE,
        comment="Тип уборки",
    )
    area: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False,
        comment="Площадь уборки в м²",
    )
    urgency_coef: Mapped[float] = mapped_column(
        Numeric(4, 2), default=1.0, nullable=False,
        comment="Коэффициент срочности",
    )
    dirt_coef: Mapped[float] = mapped_column(
        Numeric(4, 2), default=1.0, nullable=False,
        comment="Коэффициент загрязнения",
    )
    discount: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0.0, nullable=False,
        comment="Скидка в рублях",
    )
    total_price: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, default=0.0,
        comment="Итоговая стоимость",
    )
    planned_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, index=True,
        comment="Планируемая дата",
    )
    planned_start: Mapped[Optional[time]] = mapped_column(
        Time, nullable=True,
        comment="Планируемое время начала",
    )
    planned_end: Mapped[Optional[time]] = mapped_column(
        Time, nullable=True,
        comment="Планируемое время окончания",
    )
    actual_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="Фактическое начало",
    )
    actual_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="Фактическое окончание",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Заметки",
    )

    # Связи
    client: Mapped["Client"] = relationship(back_populates="orders")
    object: Mapped["Object"] = relationship(back_populates="orders")
    crew: Mapped[Optional["Crew"]] = relationship(back_populates="orders")
    manager: Mapped[Optional["User"]] = relationship(
        back_populates="orders",
        foreign_keys=[manager_id],
    )
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    checklist_tasks: Mapped[list["ChecklistTask"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base, ReprMixin):
    """Позиция заказа — дополнительная услуга.

    Промежуточная таблица между Order и Service (many-to-many с
    дополнительными полями quantity и sum).

    Attributes:
        order_item_id: Уникальный идентификатор.
        order_id: ID заказа.
        service_id: ID услуги.
        quantity: Количество (штук, м², часов).
        price: Цена за единицу на момент заказа.
        sum: Сумма = quantity × price.
    """

    __tablename__ = "order_items"
    _repr_fields = ["order_item_id", "service_id", "quantity", "sum"]

    order_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="ID заказа",
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.service_id", ondelete="RESTRICT"),
        nullable=False, index=True,
        comment="ID услуги",
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=1.0,
        comment="Количество",
    )
    price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False,
        comment="Цена за единицу",
    )
    sum: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False,
        comment="Сумма",
    )

    # Связи
    order: Mapped["Order"] = relationship(back_populates="items")
    service: Mapped["Service"] = relationship()
