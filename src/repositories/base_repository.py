"""Базовый репозиторий для CRUD-операций.

Модуль содержит универсальный класс BaseRepository, который реализует
стандартные операции Create/Read/Update/Delete для любой ORM-модели.
Конкретные репозитории наследуются от него и добавляют специфичные методы.

Паттерн Repository (см. ТЗ, раздел 1.2.2) изолирует бизнес-логику от SQL.
"""

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from src.config.database import db

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Базовый репозиторий с CRUD-операциями.

    Реализует стандартные операции для любой ORM-модели. Конкретные
    репозитории наследуются и вызывают super().__init__(Model).

    Attributes:
        model: Класс ORM-модели, с которой работает репозиторий.
        session: Сессия SQLAlchemy для работы с БД.

    Example:
        >>> class UserRepository(BaseRepository[User]):
        ...     def __init__(self):
        ...         super().__init__(User)
    """

    def __init__(self, model: Type[T]) -> None:
        """Инициализирует репозиторий для конкретной модели.

        Args:
            model: ORM-модель (например, User, Order).
        """
        self.model = model
        self.session: Session = db.get_session()

    def create(self, **kwargs: Any) -> T:
        """Создаёт новую запись в БД.

        Args:
            **kwargs: Атрибуты создаваемого объекта.

        Returns:
            Созданный объект с заполненным ID.

        Example:
            >>> repo.create(username="admin", password_hash="...")
        """
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, obj_id: int) -> Optional[T]:
        """Возвращает запись по первичному ключу.

        Args:
            obj_id: Значение первичного ключа.

        Returns:
            Объект или None, если не найден.
        """
        return self.session.query(self.model).filter_by(**{
            self._pk_name(): obj_id
        }).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Возвращает список записей с пагинацией.

        Args:
            skip: Сколько записей пропустить (для пагинации).
            limit: Максимальное количество записей.

        Returns:
            Список объектов.
        """
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def update(self, obj_id: int, **kwargs: Any) -> Optional[T]:
        """Обновляет запись по ID.

        Args:
            obj_id: Значение первичного ключа.
            **kwargs: Атрибуты для обновления.

        Returns:
            Обновлённый объект или None, если запись не найдена.
        """
        obj = self.get_by_id(obj_id)
        if obj is None:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj_id: int) -> bool:
        """Удаляет запись по ID.

        Args:
            obj_id: Значение первичного ключа.

        Returns:
            True если удалено, False если запись не найдена.
        """
        obj = self.get_by_id(obj_id)
        if obj is None:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True

    def count(self) -> int:
        """Возвращает общее количество записей.

        Returns:
            Число записей в таблице.
        """
        return self.session.query(self.model).count()

    def exists(self, obj_id: int) -> bool:
        """Проверяет существование записи по ID.

        Args:
            obj_id: Значение первичного ключа.

        Returns:
            True если запись существует.
        """
        return self.get_by_id(obj_id) is not None

    def _pk_name(self) -> str:
        """Возвращает имя первичного ключа модели.

        Returns:
            Имя атрибута первичного ключа (например, 'user_id').

        Raises:
            ValueError: Если у модели не найдено первичного ключа.
        """
        pk_columns = self.model.__table__.primary_key.columns
        if not pk_columns:
            raise ValueError(
                f"Модель {self.model.__name__} не имеет первичного ключа"
            )
        return list(pk_columns)[0].name

    def close(self) -> None:
        """Закрывает сессию.

        Вызывать после завершения работы с репозиторием.
        """
        self.session.close()
