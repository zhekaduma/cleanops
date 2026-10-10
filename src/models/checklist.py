"""ORM-модель задачи чек-листа.

Модуль содержит модель ChecklistTask — отдельная задача в чек-листе
заказа (например, «Помыть окна», «Пропылесосить»).

Соответствует разделу ТЗ 4.2.3 (чек-листы).
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base
from src.models.base import ReprMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.order import Order


class ChecklistTask(Base, TimestampMixin, ReprMixin):
    """Задача в чек-листе заказа.

    Формируется автоматически по шаблону для типа уборки и площади
    (см. раздел ТЗ 4.2.3, F-3.1). Клинер отмечает выполнение в UI,
    загружает фото «до/после» для спорных зон.

    Attributes:
        task_id: Уникальный идентификатор.
        order_id: ID заказа.
        template_type: Тип шаблона (по типу уборки).
        description: Описание задачи.
        is_required: Обязательная ли задача.
        is_done: Выполнена ли задача.
        done_at: Время выполнения.
        photo_before: Путь к фото «до».
        photo_after: Путь к фото «после».
        comment: Комментарий клинера.
        order: Связь с заказом.
    """

    __tablename__ = "checklist_tasks"
    _repr_fields = ["task_id", "order_id", "is_done", "description"]

    task_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="ID заказа",
    )
    template_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        comment="Тип шаблона (по типу уборки)",
    )
    description: Mapped[str] = mapped_column(
        String(300), nullable=False,
        comment="Описание задачи",
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Обязательная ли задача",
    )
    is_done: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True,
        comment="Выполнена ли задача",
    )
    done_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="Время выполнения",
    )
    photo_before: Mapped[Optional[str]] = mapped_column(
        String(300), nullable=True,
        comment="Путь к фото «до»",
    )
    photo_after: Mapped[Optional[str]] = mapped_column(
        String(300), nullable=True,
        comment="Путь к фото «после»",
    )
    comment: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Комментарий клинера",
    )

    # Связи
    order: Mapped["Order"] = relationship(back_populates="checklist_tasks")
