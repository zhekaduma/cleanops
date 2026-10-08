"""ORM-модель платежа.

Модуль содержит модель Payment — оплата заказа клиентом.

Соответствует разделу ТЗ 4.2.6 (учёт оплат).
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base
from src.models.base import ReprMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.order import Order
    from src.models.user import User


class PaymentMethod:
    """Способ оплаты.

    Соответствует разделу ТЗ 4.2.6 (F-6.2).
    """

    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    BANK = "bank"

    ALL = (CASH, CARD, TRANSFER, BANK)
    LABELS = {
        CASH: "Наличные",
        CARD: "Карта",
        TRANSFER: "Перевод",
        BANK: "Безнал",
    }


class PaymentStatus:
    """Статус платежа."""

    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

    ALL = (PENDING, PAID, REFUNDED, CANCELLED)
    LABELS = {
        PENDING: "Ожидает",
        PAID: "Оплачен",
        REFUNDED: "Возврат",
        CANCELLED: "Отменён",
    }


class Payment(Base, TimestampMixin, ReprMixin):
    """Платёж по заказу.

    Фиксирует оплату клиента. Может быть частичным (несколько платежей
    на один заказ).

    Attributes:
        payment_id: Уникальный идентификатор.
        order_id: ID заказа.
        amount: Сумма платежа.
        method: Способ оплаты (см. PaymentMethod).
        status: Статус платежа (см. PaymentStatus).
        paid_at: Дата и время оплаты.
        created_by: ID пользователя, принявшего платёж.
        comment: Комментарий.
        order: Связь с заказом.
        created_by_user: Связь с пользователем.
    """

    __tablename__ = "payments"
    _repr_fields = ["payment_id", "order_id", "amount", "method", "status"]

    payment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="ID заказа",
    )
    amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False,
        comment="Сумма платежа",
    )
    method: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PaymentMethod.CASH,
        comment="Способ оплаты",
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PaymentStatus.PENDING,
        index=True,
        comment="Статус платежа",
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True,
        comment="Дата и время оплаты",
    )
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="Кто принял платёж",
    )
    comment: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Комментарий",
    )

    # Связи
    order: Mapped["Order"] = relationship(back_populates="payments")
    created_by_user: Mapped["User | None"] = relationship(
        back_populates="payments",
        foreign_keys=[created_by],
    )
