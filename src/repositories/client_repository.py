"""Репозитории клиентов и объектов уборки.

Модуль содержит два репозитория:
- ClientRepository — CRUD для клиентов + поиск.
- ObjectRepository — CRUD для объектов уборки + поиск по клиенту.
"""

from typing import List, Optional

from src.models.client import Client, ClientType, Object
from src.repositories.base_repository import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """Репозиторий для работы с клиентами.

    Расширяет BaseRepository специфичными методами:
    - поиск по имени, телефону, email;
    - фильтрация по типу (физлицо/юрлицо);
    - работа с активными клиентами.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели Client."""
        super().__init__(Client)

    def search(self, query: str) -> List[Client]:
        """Ищет клиентов по имени, телефону или email.

        Args:
            query: Строка поиска.

        Returns:
            Список клиентов, подходящих под запрос.
        """
        pattern = f"%{query}%"
        return (
            self.session.query(Client)
            .filter(
                (Client.name.like(pattern))
                | (Client.phone.like(pattern))
                | (Client.email.like(pattern))
            )
            .all()
        )

    def get_by_phone(self, phone: str) -> Optional[Client]:
        """Находит клиента по телефону.

        Args:
            phone: Номер телефона.

        Returns:
            Клиент или None, если не найден.
        """
        return self.session.query(Client).filter_by(phone=phone).first()

    def get_by_type(self, client_type: str) -> List[Client]:
        """Возвращает клиентов указанного типа.

        Args:
            client_type: Тип (см. ClientType).

        Returns:
            Список клиентов.
        """
        return self.session.query(Client).filter_by(type=client_type).all()

    def get_active(self) -> List[Client]:
        """Возвращает всех активных клиентов.

        Returns:
            Список активных клиентов.
        """
        return self.session.query(Client).filter_by(is_active=True).all()

    def get_individuals(self) -> List[Client]:
        """Возвращает клиентов-физлиц.

        Returns:
            Список физлиц.
        """
        return self.get_by_type(ClientType.INDIVIDUAL)

    def get_companies(self) -> List[Client]:
        """Возвращает клиентов-юрлиц.

        Returns:
            Список юрлиц.
        """
        return self.get_by_type(ClientType.COMPANY)


class ObjectRepository(BaseRepository[Object]):
    """Репозиторий для работы с объектами уборки.

    Расширяет BaseRepository специфичными методами:
    - поиск объектов по клиенту;
    - фильтрация по типу объекта;
    - поиск по адресу.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели Object."""
        super().__init__(Object)

    def get_by_client(self, client_id: int) -> List[Object]:
        """Возвращает все объекты клиента.

        Args:
            client_id: ID клиента.

        Returns:
            Список объектов.
        """
        return self.session.query(Object).filter_by(client_id=client_id).all()

    def get_by_type(self, object_type: str) -> List[Object]:
        """Возвращает объекты указанного типа.

        Args:
            object_type: Тип (см. ObjectType).

        Returns:
            Список объектов.
        """
        return self.session.query(Object).filter_by(object_type=object_type).all()

    def search_by_address(self, query: str) -> List[Object]:
        """Ищет объекты по адресу.

        Args:
            query: Часть адреса.

        Returns:
            Список объектов.
        """
        pattern = f"%{query}%"
        return self.session.query(Object).filter(Object.address.like(pattern)).all()

    def get_active(self) -> List[Object]:
        """Возвращает все активные объекты.

        Returns:
            Список активных объектов.
        """
        return self.session.query(Object).filter_by(is_active=True).all()
