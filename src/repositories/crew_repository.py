"""Репозиторий бригад.

Модуль содержит CrewRepository — CRUD для модели Crew
плюс фильтрация по зоне и активные бригады.
"""

from typing import List, Optional

from src.models.crew import Crew
from src.repositories.base_repository import BaseRepository


class CrewRepository(BaseRepository[Crew]):
    """Репозиторий для работы с бригадами.

    Расширяет BaseRepository специфичными методами:
    - поиск по названию;
    - фильтрация по зоне;
    - работа с активными бригадами.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели Crew."""
        super().__init__(Crew)

    def get_by_name(self, name: str) -> Optional[Crew]:
        """Находит бригаду по названию.

        Args:
            name: Название бригады.

        Returns:
            Бригада или None.
        """
        return self.session.query(Crew).filter_by(name=name).first()

    def get_by_zone(self, zone: str) -> List[Crew]:
        """Возвращает бригады в указанной зоне.

        Args:
            zone: Зона работы (район).

        Returns:
            Список бригад.
        """
        return self.session.query(Crew).filter_by(zone=zone).all()

    def get_active(self) -> List[Crew]:
        """Возвращает все активные бригады.

        Returns:
            Список активных бригад.
        """
        return self.session.query(Crew).filter_by(is_active=True).all()

    def search(self, query: str) -> List[Crew]:
        """Ищет бригады по названию или зоне.

        Args:
            query: Строка поиска.

        Returns:
            Список бригад.
        """
        pattern = f"%{query}%"
        return (
            self.session.query(Crew)
            .filter((Crew.name.ilike(pattern)) | (Crew.zone.ilike(pattern)))
            .all()
        )
