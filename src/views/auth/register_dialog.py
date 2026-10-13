"""Диалог регистрации нового пользователя.

Позволяет зарегистрировать нового пользователя с ролью Менеджер
или Клинер. Остальные роли создаются администратором через
раздел «Пользователи» (F-7.1).
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models.user import UserRole


COLOR_BG = "#F8FAFC"
COLOR_PRIMARY = "#0EA5A4"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_ERROR = "#EF4444"


class RegisterDialog(QDialog):
    """Диалог регистрации нового пользователя.

    Позволяет зарегистрировать менеджера или клинера.
    Для других ролей требуется администратор.

    Attributes:
        username: Логин.
        password: Пароль.
        full_name: ФИО.
        email: Email.
        phone: Телефон.
        role: Роль (manager / cleaner).
    """

    # Роли, доступные для самостоятельной регистрации
    ALLOWED_ROLES = [
        (UserRole.MANAGER, "Менеджер"),
        (UserRole.CLEANER, "Клинер"),
    ]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует диалог регистрации."""
        super().__init__(parent)
        self.setWindowTitle("Регистрация")
        self.setModal(True)
        self.setFixedWidth(500)
        self.setStyleSheet(f"background-color: {COLOR_BG};")

        self._build_ui()

    def _build_ui(self) -> None:
        """Собирает интерфейс диалога."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(16)

        # Заголовок
        title = QLabel("Регистрация")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 22px; font-weight: 700;"
        )
        main.addWidget(title)

        subtitle = QLabel("Создайте учётную запись для работы в системе")
        subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 13px;"
        )
        main.addWidget(subtitle)

        main.addSpacing(8)

        # Форма
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # Логин
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("ivanov")
        self.username_input.setFixedHeight(38)
        self.username_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Логин:"), self.username_input)

        # Пароль
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Минимум 6 символов")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(38)
        self.password_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Пароль:"), self.password_input)

        # Подтверждение пароля
        self.password2_input = QLineEdit()
        self.password2_input.setPlaceholderText("Повторите пароль")
        self.password2_input.setEchoMode(QLineEdit.Password)
        self.password2_input.setFixedHeight(38)
        self.password2_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Подтверждение:"), self.password2_input)

        # ФИО
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Иванов Иван Иванович")
        self.full_name_input.setFixedHeight(38)
        self.full_name_input.setStyleSheet(self._input_style())
        form.addRow(self._label("ФИО:"), self.full_name_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ivanov@example.ru")
        self.email_input.setFixedHeight(38)
        self.email_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Email:"), self.email_input)

        # Телефон
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+7 (999) 123-45-67")
        self.phone_input.setFixedHeight(38)
        self.phone_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Телефон:"), self.phone_input)

        # Роль
        self.role_combo = QComboBox()
        for role_value, role_label in self.ALLOWED_ROLES:
            self.role_combo.addItem(role_label, role_value)
        self.role_combo.setFixedHeight(38)
        self.role_combo.setStyleSheet(self._input_style())
        form.addRow(self._label("Роль:"), self.role_combo)

        main.addLayout(form)

        # Сообщение об ошибке
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(
            f"color: {COLOR_ERROR}; font-family: 'Inter'; "
            f"font-size: 13px; padding: 8px;"
        )
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        main.addWidget(self.error_label)

        main.addSpacing(8)

        # Кнопки
        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedSize(120, 40)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(self._button_outline())
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        register_btn = QPushButton("Зарегистрироваться")
        register_btn.setFixedSize(180, 40)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.setStyleSheet(self._button_primary())
        register_btn.clicked.connect(self._on_register)
        buttons.addWidget(register_btn)

        main.addLayout(buttons)

    def _label(self, text: str) -> QLabel:
        """Создаёт label."""
        label = QLabel(text)
        label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 13px;"
        )
        return label

    def _input_style(self) -> str:
        """QSS для полей."""
        return f"""
            QLineEdit, QComboBox {{
                background-color: white;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Inter';
                font-size: 13px;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """

    def _button_primary(self) -> str:
        """QSS для главной кнопки."""
        return f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                font-family: 'Inter';
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #0F766E; }}
        """

    def _button_outline(self) -> str:
        """QSS для контурной кнопки."""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                font-family: 'Inter';
                font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #F1F5F9; }}
        """

    def _show_error(self, message: str) -> None:
        """Показывает ошибку."""
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def _on_register(self) -> None:
        """Обрабатывает регистрацию."""
        # Валидация
        username = self.username_input.text().strip()
        password = self.password_input.text()
        password2 = self.password2_input.text()
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()

        if not username:
            self._show_error("Введите логин")
            return

        if len(username) < 3:
            self._show_error("Логин должен содержать минимум 3 символа")
            return

        if len(password) < 6:
            self._show_error("Пароль должен содержать минимум 6 символов")
            return

        if password != password2:
            self._show_error("Пароли не совпадают")
            return

        if not full_name:
            self._show_error("Введите ФИО")
            return

        # Проверка занятости логина
        from src.services import AuthService
        auth = AuthService()

        if auth.user_repo.username_exists(username):
            self._show_error(f"Логин «{username}» уже занят")
            return

        if email and auth.user_repo.email_exists(email):
            self._show_error(f"Email «{email}» уже используется")
            return

        # Создаём пользователя
        try:
            user = auth.create_user(
                username=username,
                password=password,
                full_name=full_name,
                role=self.role_combo.currentData(),
                email=email or None,
                phone=phone or None,
            )

            if user is None:
                self._show_error("Не удалось создать пользователя")
                return

            print(f"[RegisterDialog] Создан пользователь: {user.username} ({user.role})")
            self.accept()

        except Exception as e:
            self._show_error(f"Ошибка регистрации: {e}")

    def get_credentials(self) -> dict:
        """Возвращает данные зарегистрированного пользователя.

        Returns:
            Словарь с логином и паролем для автологина.
        """
        return {
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
        }
