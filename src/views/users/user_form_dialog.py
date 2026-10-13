"""Диалог создания/редактирования пользователя.

Позволяет администратору создавать пользователей с любой ролью
и редактировать существующих. Пароль при создании обязателен,
при редактировании — опционален.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
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

from src.models.user import User, UserRole


COLOR_BG = "#F8FAFC"
COLOR_PRIMARY = "#0EA5A4"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_ERROR = "#EF4444"


class UserFormDialog(QDialog):
    """Диалог создания/редактирования пользователя."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        user: Optional[User] = None,
    ) -> None:
        """Инициализирует диалог.

        Args:
            parent: Родительский виджет.
            user: Пользователь для редактирования. None — создание.
        """
        super().__init__(parent)
        self.user = user
        self.is_edit = user is not None

        title = "Редактировать пользователя" if self.is_edit else "Новый пользователь"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(500)
        self.setStyleSheet(f"background-color: {COLOR_BG};")

        self._build_ui()
        if self.is_edit:
            self._fill_form()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(16)

        title = QLabel(
            "Редактирование пользователя" if self.is_edit else "Новый пользователь"
        )
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 20px; font-weight: 700;"
        )
        main.addWidget(title)

        # Форма
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # Логин
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("ivanov")
        self.username_input.setFixedHeight(38)
        self.username_input.setStyleSheet(self._input_style())
        if self.is_edit:
            self.username_input.setReadOnly(True)
            self.username_input.setStyleSheet(
                self._input_style() + "background-color: #F1F5F9;"
            )
        form.addRow(self._label("Логин:"), self.username_input)

        # Пароль
        pwd_label = "Новый пароль:" if self.is_edit else "Пароль:"
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(
            "Оставьте пустым, чтобы не менять" if self.is_edit else "Минимум 6 символов"
        )
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(38)
        self.password_input.setStyleSheet(self._input_style())
        form.addRow(self._label(pwd_label), self.password_input)

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

        # Роль — все 6 ролей
        self.role_combo = QComboBox()
        for role_value in UserRole.ALL:
            label = UserRole.LABELS.get(role_value, role_value)
            self.role_combo.addItem(label, role_value)
        self.role_combo.setFixedHeight(38)
        self.role_combo.setStyleSheet(self._input_style())
        form.addRow(self._label("Роль:"), self.role_combo)

        # Активен
        self.is_active_cb = QCheckBox("Активен")
        self.is_active_cb.setChecked(True)
        self.is_active_cb.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; font-size: 13px;"
        )
        form.addRow(self._label("Статус:"), self.is_active_cb)

        main.addLayout(form)

        # Ошибка
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(
            f"color: {COLOR_ERROR}; font-family: 'Inter'; "
            f"font-size: 13px; padding: 8px;"
        )
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        main.addWidget(self.error_label)

        # Кнопки
        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedSize(120, 40)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(self._button_outline())
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.setFixedSize(140, 40)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(self._button_primary())
        save_btn.clicked.connect(self._on_save)
        buttons.addWidget(save_btn)

        main.addLayout(buttons)

    def _label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 13px;"
        )
        return label

    def _input_style(self) -> str:
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

    def _fill_form(self) -> None:
        """Заполняет форму данными пользователя."""
        u = self.user
        self.username_input.setText(u.username)
        self.full_name_input.setText(u.full_name)
        self.email_input.setText(u.email or "")
        self.phone_input.setText(u.phone or "")
        self.is_active_cb.setChecked(bool(u.is_active))

        idx = self.role_combo.findData(u.role)
        if idx >= 0:
            self.role_combo.setCurrentIndex(idx)

    def _show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def _on_save(self) -> None:
        """Валидирует и подтверждает."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        full_name = self.full_name_input.text().strip()

        if not username:
            self._show_error("Введите логин")
            return
        if len(username) < 3:
            self._show_error("Логин должен содержать минимум 3 символа")
            return
        if not full_name:
            self._show_error("Введите ФИО")
            return

        # Пароль обязателен только при создании
        if not self.is_edit:
            if len(password) < 6:
                self._show_error("Пароль должен содержать минимум 6 символов")
                return
        else:
            if password and len(password) < 6:
                self._show_error("Новый пароль должен содержать минимум 6 символов")
                return

        # Проверка уникальности логина (только при создании)
        if not self.is_edit:
            from src.repositories import UserRepository
            repo = UserRepository()
            if repo.username_exists(username):
                self._show_error(f"Логин «{username}» уже занят")
                return

        self.accept()

    def get_data(self) -> dict:
        """Возвращает введённые данные.

        Returns:
            Словарь с полями пользователя.
        """
        return {
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "full_name": self.full_name_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "phone": self.phone_input.text().strip() or None,
            "role": self.role_combo.currentData(),
            "is_active": self.is_active_cb.isChecked(),
        }
