"""Подключение к базе данных SQLite.

Модуль содержит Singleton-класс DatabaseConnection, который управляет
единственным подключением к БД и предоставляет фабрику сессий SQLAlchemy.

Attributes:
    engine: SQLAlchemy Engine — движок подключения к БД.
    SessionLocal: Фабрика сессий (sessionmaker).
"""

from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config.app_config import config


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей CleanOps.

    Наследуя от этого класса, модели автоматически регистрируются в
    метаданных SQLAlchemy и получают доступ к функционалу ORM.
    """


class DatabaseConnection:
    """Singleton-подключение к базе данных.

    Управляет единственным Engine и предоставляет сессии для работы
    с БД. Позволяет избежать множественных подключений и утечек ресурсов.

    Attributes:
        _instance: Единственный экземпляр класса.
        engine: SQLAlchemy Engine для подключения к SQLite.
        SessionLocal: Фабрика сессий.
    """

    _instance: Optional["DatabaseConnection"] = None

    def __new__(cls) -> "DatabaseConnection":
        """Создаёт или возвращает единственный экземпляр подключения."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Инициализирует Engine и фабрику сессий."""
        # SQLite URL: файл в data/cleanops.db
        db_url = f"sqlite:///{config.DB_PATH}"

        # echo=True — выводит SQL-запросы в консоль (для отладки)
        self.engine: Engine = create_engine(
            db_url,
            echo=config.DEBUG,
            future=True,
        )

        # Фабрика сессий — каждый вызов создаёт новую сессию
        self.SessionLocal: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_session(self) -> Session:
        """Возвращает новую сессию для работы с БД.

        Returns:
            Session: Сессия SQLAlchemy.

        Example:
            >>> db = DatabaseConnection()
            >>> with db.get_session() as session:
            ...     session.add(obj)
            ...     session.commit()
        """
        return self.SessionLocal()

    def create_all_tables(self) -> None:
        """Создаёт все таблицы в БД согласно зарегистрированным моделям.

        Внимание: модели должны быть импортированы до вызова этого метода,
        иначе SQLAlchemy не увидит их и не создаст таблицы.
        """
        Base.metadata.create_all(self.engine)

    def drop_all_tables(self) -> None:
        """Удаляет все таблицы из БД. Используется в тестах."""
        Base.metadata.drop_all(self.engine)


# Глобальный экземпляр — импортируется в других модулях
db = DatabaseConnection()
