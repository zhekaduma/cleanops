"""Базовые классы и миксины для ORM-моделей CleanOps.

Модуль содержит общие миксины, которые используются во всех моделях:
- TimestampMixin — добавляет поля created_at и updated_at.
- ReprMixin — удобное строковое представление объектов.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Миксин с полями времени создания и обновления записи.

    Attributes:
        created_at: Дата и время создания записи (заполняется автоматически).
        updated_at: Дата и время последнего обновления записи.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="Дата и время создания записи",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Дата и время последнего обновления",
    )


class ReprMixin:
    """Миксин для удобного строкового представления моделей.

    Классы-наследники должны определить атрибут `_repr_fields` —
    список полей, которые нужно отображать в repr().
    """

    _repr_fields: list[str] = []

    def __repr__(self) -> str:
        """Возвращает читаемое представление объекта."""
        cls_name = self.__class__.__name__
        fields = ", ".join(
            f"{field}={getattr(self, field, None)!r}"
            for field in self._repr_fields
        )
        return f"{cls_name}({fields})"
