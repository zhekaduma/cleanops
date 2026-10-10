"""Точка входа приложения CleanOps."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication  # noqa: E402

from src.models.user import User, UserRole  # noqa: E402
from src.views.auth.login_window import LoginWindow  # noqa: E402
from src.views.main_window import MainWindow  # noqa: E402


class Application:
    """Контроллер приложения."""

    def __init__(self) -> None:
        """Инициализирует приложение."""
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.main_window = None
        self.current_user = None

    def run(self) -> int:
        """Запускает приложение."""
        self._show_login()
        return self.app.exec_()

    def _show_login(self) -> None:
        """Показывает окно авторизации."""
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self._on_login_success)
        self.login_window.show()
        print("[Application] LoginWindow открыт")

    def _on_login_success(self, user: User) -> None:
        """Обрабатывает успешный вход."""
        print(f"[Application] Успешный вход: {user.full_name}")
        self.current_user = user

        # Сначала СКРЫВАЕМ (не закрываем) — это предотвращает segfault
        if self.login_window:
            self.login_window.hide()

        # Открываем главное окно
        self._show_main_window()

        # Теперь безопасно удаляем LoginWindow через deleteLater
        if self.login_window:
            self.login_window.deleteLater()
            self.login_window = None
            print("[Application] LoginWindow удалён")

    def _show_main_window(self) -> None:
        """Показывает главное окно."""
        user = self.current_user
        role_label = UserRole.LABELS.get(user.role, user.role)

        self.main_window = MainWindow(
            user_name=user.full_name,
            user_role=role_label,
        )
        self.main_window.topbar.logout_requested.connect(self._on_logout)
        self.main_window.show()
        print(f"[Application] MainWindow открыт для {user.full_name}")

    def _on_logout(self) -> None:
        """Обрабатывает выход."""
        print("[Application] Выход")
        if self.main_window:
            self.main_window.hide()
            self.main_window.deleteLater()
            self.main_window = None
        self.current_user = None
        self._show_login()


def main() -> None:
    """Точка входа."""
    print("CleanOps starting...")
    print("Логины: admin/admin123, manager/manager123, cleaner/clean123")

    application = Application()
    sys.exit(application.run())


if __name__ == "__main__":
    main()
