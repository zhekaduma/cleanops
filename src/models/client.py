"""ORM-модели клиентов и объектов уборки.

Модуль содержит две модели:
- Client — клиент (физическое или юридическое лицо).
- Object — объект уборки (квартира, офис, помещение).

Соответствует разделу ТЗ 4.2.2 (справочники клиентов и объектов).
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base
from src.models.base import ReprMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.order import Order


class ClientType:
    """Тип клиента.

    Attributes:
        INDIVIDUAL: Физическое лицо.
        COMPANY: Юридическое лицо (компания).
    """

    INDIVIDUAL = "individual"
    COMPANY = "company"

    ALL = (INDIVIDUAL, COMPANY)
    LABELS = {
        INDIVIDUAL: "Физлицо",
        COMPANY: "Юрлицо",
    }


class ObjectType:
    """Тип объекта уборки.

    Attributes:
        APARTMENT: Квартира.
        HOUSE: Частный дом.
        OFFICE: Офис.
        WAREHOUSE: Склад.
        OTHER: Другое.
    """

    APARTMENT = "apartment"
    HOUSE = "house"
    OFFICE = "office"
    WAREHOUSE = "warehouse"
    OTHER = "other"

    ALL = (APARTMENT, HOUSE, OFFICE, WAREHOUSE, OTHER)
    LABELS = {
        APARTMENT: "Квартира",
        HOUSE: "Дом",
        OFFICE: "Офис",
        WAREHOUSE: "Склад",
        OTHER: "Другое",
    }


class Client(Base, TimestampMixin, ReprMixin):
    """Клиент клининговой компании.

    Может быть физическим или юридическим лицом. Хранит контактные данные
    и информацию о скидке.

    Attributes:
        client_id: Уникальный идентификатор.
        type: Тип клиента (см. ClientType).
        name: ФИО или название компании.
        phone: Телефон.
        email: Email.
        address: Юридический адрес (для юрлиц).
        discount: Персональная скидка в процентах.
        notes: Заметки.
        is_active: Активен ли клиент.
        objects: Объекты уборки клиента.
        orders: Заказы клиента.
    """

    __tablename__ = "clients"
    _repr_fields = ["client_id", "name", "type"]

    client_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ClientType.INDIVIDUAL,
        comment="Тип клиента (физлицо/юрлицо)",
    )
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True,
        comment="ФИО или название компании",
    )
    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True,
        comment="Телефон",
    )
    email: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Email",
    )
    address: Mapped[str | None] = mapped_column(
        String(300), nullable=True,
        comment="Юридический адрес",
    )
    discount: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0.0, nullable=False,
        comment="Персональная скидка в процентах",
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Заметки о клиенте",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Активен ли клиент",
    )

    # Связи
    objects: Mapped[list["Object"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="client")


class Object(Base, TimestampMixin, ReprMixin):
    """Объект уборки (адрес).

    Может быть квартирой, домом, офисом, складом. Хранит площадь,
    тип и особенности доступа.

    Attributes:
        object_id: Уникальный идентификатор.
        client_id: ID клиента-владельца.
        address: Адрес объекта.
        area: Площадь в квадратных метрах.
        object_type: Тип объекта (см. ObjectType).
        access_notes: Особенности доступа (код домофона и т.д.).
        is_active: Активен ли объект.
        client: Связь с клиентом.
        orders: Заказы на этот объект.
    """

    __tablename__ = "objects"
    _repr_fields = ["object_id", "address", "area"]

    object_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.client_id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="ID клиента",
    )
    address: Mapped[str] = mapped_column(
        String(300), nullable=False,
        comment="Адрес объекта",
    )
    area: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False,
        comment="Площадь в м²",
    )
    object_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ObjectType.APARTMENT,
        comment="Тип объекта",
    )
    access_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Особенности доступа",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Активен ли объект",
    )

    # Связи
    client: Mapped["Client"] = relationship(back_populates="objects")
    orders: Mapped[list["Order"]] = relationship(back_populates="object")
