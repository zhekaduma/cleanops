"""Подключение к базе данных SQLite.

Модуль содержит Singleton-класс DatabaseConnection, который управляет
единственным подключением к БД и предоставляет фабрику сессий SQLAlchemy.

Для SQLite используется StaticPool — одно общее соединение на всё
приложение. Это предотвращает исчерпание пула при множественных
репозиториях (каждый репозиторий создаёт свою сессию).
"""

from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.config.app_config import config


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей CleanOps.

    Наследуя от этого класса, модели автоматически регистрируются в
    метаданных SQLAlchemy и получают доступ к функционалу ORM.
    """


class DatabaseConnection:
    """Singleton-подключение к базе данных.

    Управляет единственным Engine и предоставляет сессии для работы
    с БД. Для SQLite используется StaticPool — одно общее соединение.
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
        import shutil

        # При запуске из .exe — копируем встроенную БД рядом с .exe,
        # если её там ещё нет
        if getattr(__import__("sys"), "frozen", False):
            db_path = config.DB_PATH

            # Если БД рядом с .exe нет — копируем из _MEIPASS
            if not db_path.exists():
                meipass_db = config._MEIPASS_DIR / "data" / "cleanops.db"
                if meipass_db.exists():
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(meipass_db, db_path)
                    print(f"[Database] БД скопирована из _MEIPASS: {db_path}")

        db_url = f"sqlite:///{config.DB_PATH}"

        # SQLite: используем StaticPool — одно соединение на всё приложение.
        # connect_args={"check_same_thread": False} — разрешаем доступ
        # из разных потоков (необходимо для PyQt).
        self.engine: Engine = create_engine(
            db_url,
            echo=config.DEBUG,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
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
        """
        return self.SessionLocal()

    def create_all_tables(self) -> None:
        """Создаёт все таблицы в БД согласно зарегистрированным моделям."""
        Base.metadata.create_all(self.engine)

    def drop_all_tables(self) -> None:
        """Удаляет все таблицы из БД. Используется в тестах."""
        Base.metadata.drop_all(self.engine)


# Глобальный экземпляр
db = DatabaseConnection()
