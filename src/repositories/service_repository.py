"""Репозиторий услуг (прайс-лист).

Модуль содержит ServiceRepository — CRUD для модели Service
плюс фильтрация по единицам измерения и активные услуги.
"""

from typing import List, Optional

from src.models.service import Service, ServiceUnit
from src.repositories.base_repository import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    """Репозиторий для работы с услугами.

    Расширяет BaseRepository специфичными методами:
    - поиск по названию;
    - фильтрация по единице измерения;
    - работа с активными услугами.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели Service."""
        super().__init__(Service)

    def search(self, query: str) -> List[Service]:
        """Ищет услуги по названию.

        Args:
            query: Строка поиска.

        Returns:
            Список услуг.
        """
        pattern = f"%{query}%"
        return self.session.query(Service).filter(Service.name.like(pattern)).all()

    def get_by_unit(self, unit: str) -> List[Service]:
        """Возвращает услуги с указанной единицей измерения.

        Args:
            unit: Единица (см. ServiceUnit).

        Returns:
            Список услуг.
        """
        return self.session.query(Service).filter_by(unit=unit).all()

    def get_active(self) -> List[Service]:
        """Возвращает все активные услуги.

        Returns:
            Список активных услуг.
        """
        return self.session.query(Service).filter_by(is_active=True).all()

    def get_by_name(self, name: str) -> Optional[Service]:
        """Находит услугу по точному названию.

        Args:
            name: Название услуги.

        Returns:
            Услуга или None.
        """
        return self.session.query(Service).filter_by(name=name).first()
