"""ORM-модель бригады клинеров.

Модуль содержит модель Crew — группа клинеров, выполняющая заказы.

Соответствует разделу ТЗ 4.2.2 (управление бригадами).
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base
from src.models.base import ReprMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.order import Order


class Crew(Base, TimestampMixin, ReprMixin):
    """Бригада клинеров.

    Группа сотрудников (1–N человек), выполняющая заказы на объекте.
    Имеет зону ответственности (район) и транспорт.

    Attributes:
        crew_id: Уникальный идентификатор.
        name: Название бригады.
        zone: Зона работы (район города).
        transport: Транспорт (модель и госномер).
        notes: Заметки.
        is_active: Активна ли бригада.
        orders: Заказы, назначенные на бригаду.
    """

    __tablename__ = "crews"
    _repr_fields = ["crew_id", "name", "zone"]

    crew_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
        comment="Название бригады",
    )
    zone: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Зона работы (район)",
    )
    transport: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Транспорт (модель, госномер)",
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Заметки о бригаде",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Активна ли бригада",
    )

    # Связи
    orders: Mapped[list["Order"]] = relationship(back_populates="crew")
