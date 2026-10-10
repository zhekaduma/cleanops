"""Тестовый запуск Topbar."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication, QMainWindow  # noqa: E402

from src.views.widgets.topbar import Topbar  # noqa: E402


class TestWindow(QMainWindow):
    """Тестовое окно с Topbar."""

    def __init__(self) -> None:
        """Инициализирует окно."""
        super().__init__()
        self.setWindowTitle("Test Topbar")
        self.setGeometry(100, 100, 1200, 200)

        topbar = Topbar(
            title="Дашборд",
            user_name="Иванов Иван",
            user_role="Менеджер",
            notifications_count=3,
        )
        topbar.logout_requested.connect(
            lambda: print("Logout нажат!")
        )
        self.setCentralWidget(topbar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
