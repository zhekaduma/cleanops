import sys
from pathlib import Path
from typing import Optional


class AppConfig:
    _instance: Optional["AppConfig"] = None

    def __new__(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        if getattr(sys, "frozen", False):
            self.BASE_DIR: Path = Path(sys.executable).parent
            self._MEIPASS_DIR: Path = Path(sys._MEIPASS)
        else:
            self.BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
            self._MEIPASS_DIR: Path = self.BASE_DIR

        self.DATA_DIR: Path = self.BASE_DIR / "data"
        self.DB_PATH: Path = self.DATA_DIR / "cleanops.db"
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.APP_NAME: str = "CleanOps"
        self.APP_VERSION: str = "0.1.0"
        self.DEBUG: bool = False

    def __repr__(self) -> str:
        return f"AppConfig(app_name={self.APP_NAME!r})"


config = AppConfig()
