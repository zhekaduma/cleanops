"""Экран авторизации.

Первое окно, которое видит пользователь. Содержит форму входа
с полями логин/пароль и кнопкой «Войти».

Соответствует макету Figma: центрированная карточка 400×420 с
логотипом, полями и кнопкой Primary.
"""

from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models.user import User
from src.services.auth_service import AuthService


# Цвета (из Figma)
COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_PRIMARY = "#0EA5A4"
COLOR_PRIMARY_HOVER = "#0F766E"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_BORDER = "#E2E8F0"
COLOR_ERROR = "#EF4444"


class LoginWindow(QWidget):
    """Окно авторизации.

    Отображает форму входа. При успешной авторизации emit-ит сигнал
    `login_success` с объектом User.

    Signals:
        login_success: Успешный вход. Аргумент: User.
    """

    login_success = pyqtSignal(object)  # object = User

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует окно авторизации.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.auth_service = AuthService()

        self.setWindowTitle("CleanOps — Вход в систему")
        self.setGeometry(100, 100, 1440, 900)
        self.setStyleSheet(f"background-color: {COLOR_BG};")

        self._build_ui()

    def _build_ui(self) -> None:
        """Собирает интерфейс окна авторизации."""
        # Внешний layout — центрирует карточку
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        # Карточка
        card = self._create_card()
        outer.addWidget(card)

    def _create_card(self) -> QFrame:
        """Создаёт центральную карточку с формой.

        Returns:
            Карточка-фрейм.
        """
        card = QFrame()
        card.setFixedSize(400, 480)
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLOR_CARD};
                border-radius: 12px;
                border: 1px solid {COLOR_BORDER};
            }}
            """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        # Логотип
        logo = QLabel("🧹  CleanOps")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(
            f"color: {COLOR_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700; border: none;"
        )
        layout.addWidget(logo)

        # Заголовок
        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 16px; font-weight: 500; border: none;"
        )
        layout.addWidget(title)

        layout.addSpacing(8)

        # Поле Email
        email_label = QLabel("Email или логин")
        email_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 13px; border: none;"
        )
        layout.addWidget(email_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("admin")
        self.username_input.setFixedHeight(44)
        self.username_input.setStyleSheet(self._input_style())
        layout.addWidget(self.username_input)

        # Поле Пароль
        password_label = QLabel("Пароль")
        password_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 13px; border: none;"
        )
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet(self._input_style())
        self.password_input.returnPressed.connect(self._on_login)
        layout.addWidget(self.password_input)

        # Чекбокс «Запомнить меня»
        remember = QCheckBox("Запомнить меня")
        remember.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 13px; border: none;"
        )
        layout.addWidget(remember)

        # Сообщение об ошибке
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(
            f"color: {COLOR_ERROR}; font-family: 'Inter'; "
            f"font-size: 13px; border: none;"
        )
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Кнопка «Войти»
        self.login_button = QPushButton("Войти")
        self.login_button.setFixedHeight(48)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet(self._button_style())
        self.login_button.clicked.connect(self._on_login)
        layout.addWidget(self.login_button)

        layout.addStretch()
        return card

    def _input_style(self) -> str:
        """Возвращает QSS для поля ввода.

        Returns:
            Стиль input.
        """
        return f"""
            QLineEdit {{
                background-color: {COLOR_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 0 12px;
                font-family: 'Inter';
                font-size: 14px;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """

    def _button_style(self) -> str:
        """Возвращает QSS для кнопки «Войти».

        Returns:
            Стиль кнопки.
        """
        return f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-family: 'Inter';
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #115E59;
            }}
        """

    def _on_login(self) -> None:
        """Обрабатывает нажатие кнопки «Войти»."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # Валидация на пустые поля
        if not username or not password:
            self._show_error("Заполните все поля")
            return

        # Авторизация через сервис
        result = self.auth_service.login(username, password)

        if result.success:
            self.error_label.setVisible(False)
            self.login_success.emit(result.user)
        else:
            self._show_error(result.message)

    def _show_error(self, message: str) -> None:
        """Показывает сообщение об ошибке.

        Args:
            message: Текст ошибки.
        """
        self.error_label.setText(message)
        self.error_label.setVisible(True)
