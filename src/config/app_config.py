"""Конфигурация приложения CleanOps.

Модуль содержит Singleton-класс AppConfig, который хранит все настройки
приложения в одном месте: пути, параметры БД, режимы работы.
"""

from pathlib import Path
from typing import Optional


class AppConfig:
    """Singleton-конфигурация приложения.

    Обеспечивает единственный экземпляр настроек на всё приложение.
    Позволяет обращаться к настройкам из любого места программы без
    создания новых объектов.

    Attributes:
        BASE_DIR: Корневая директория проекта.
        DATA_DIR: Директория для хранения данных (БД, файлы).
        DB_PATH: Путь к файлу базы данных SQLite.
        APP_NAME: Название приложения.
        APP_VERSION: Версия приложения.
        DEBUG: Режим отладки.
    """

    _instance: Optional["AppConfig"] = None

    def __new__(cls) -> "AppConfig":
        """Создаёт или возвращает единственный экземпляр конфигурации."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Инициализирует настройки приложения."""
        # BASE_DIR — на 2 уровня выше файла app_config.py
        # src/config/app_config.py → src/config/ → src/ → корень проекта
        self.BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
        self.DATA_DIR: Path = self.BASE_DIR / "data"
        self.DB_PATH: Path = self.DATA_DIR / "cleanops.db"

        # Создаём директорию для данных, если её нет
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Параметры приложения
        self.APP_NAME: str = "CleanOps"
        self.APP_VERSION: str = "0.1.0"
        self.DEBUG: bool = False

    def __repr__(self) -> str:
        """Строковое представление конфигурации."""
        return (
            f"AppConfig(app_name={self.APP_NAME!r}, "
            f"version={self.APP_VERSION!r}, "
            f"db_path={str(self.DB_PATH)!r})"
        )


# Глобальный экземпляр — импортируется в других модулях
config = AppConfig()
