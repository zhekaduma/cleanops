"""ORM-модель услуги (прайс-лист).

Модуль содержит модель Service — дополнительная услуга клининговой
компании (мытьё окон, химчистка и т.д.).

Соответствует разделу ТЗ 4.2.2 (управление услугами).
"""

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base
from src.models.base import ReprMixin, TimestampMixin


class ServiceUnit:
    """Единица измерения услуги.

    Attributes:
        PIECE: За штуку.
        SQM: За квадратный метр.
        HOUR: За час.
    """

    PIECE = "piece"
    SQM = "sqm"
    HOUR = "hour"

    ALL = (PIECE, SQM, HOUR)
    LABELS = {
        PIECE: "шт",
        SQM: "м²",
        HOUR: "ч",
    }


class Service(Base, TimestampMixin, ReprMixin):
    """Дополнительная услуга компании.

    Представляет услугу из прайс-листа, которую можно добавить к заказу.
    Например: «Мытьё окон», «Химчистка мебели».

    Attributes:
        service_id: Уникальный идентификатор.
        name: Название услуги.
        cleaning_type: К какому типу уборки относится (или universal).
        unit: Единица измерения (шт, м², ч).
        price: Цена за единицу.
        norm_hours: Нормо-часы на выполнение.
        is_active: Активна ли услуга в прайсе.
    """

    __tablename__ = "services"
    _repr_fields = ["service_id", "name", "price"]

    service_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(150), nullable=False, index=True,
        comment="Название услуги",
    )
    unit: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ServiceUnit.PIECE,
        comment="Единица измерения",
    )
    price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False,
        comment="Цена за единицу",
    )
    norm_hours: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0.0, nullable=False,
        comment="Нормо-часы",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Активна ли услуга",
    )
