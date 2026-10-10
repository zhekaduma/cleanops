"""Тестовый запуск главного окна."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication  # noqa: E402

from src.views.main_window import MainWindow  # noqa: E402


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(
        user_name="Иванов Иван",
        user_role="Менеджер",
    )
    window.show()
    sys.exit(app.exec_())
