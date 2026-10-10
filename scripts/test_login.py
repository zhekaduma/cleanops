"""Тестовый запуск окна авторизации."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication  # noqa: E402

from src.views.auth.login_window import LoginWindow  # noqa: E402


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()

    def on_login(user):
        print(f"УСПЕШНЫЙ ВХОД: {user.full_name} ({user.role})")
        # В реальном приложении здесь откроется MainWindow

    window.login_success.connect(on_login)
    window.show()
    sys.exit(app.exec_())
