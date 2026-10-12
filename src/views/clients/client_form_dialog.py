"""Модальное окно создания/редактирования клиента.

Форма с полями: тип, имя, телефон, email, скидка, заметки.
Соответствует F-2.2 из ТЗ.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.models.client import Client, ClientType


COLOR_PRIMARY = "#0EA5A4"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"


class ClientFormDialog(QDialog):
    """Модальное окно создания/редактирования клиента."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        client: Optional[Client] = None,
    ) -> None:
        """Инициализирует диалог.

        Args:
            parent: Родительский виджет.
            client: Клиент для редактирования. None — создание.
        """
        super().__init__(parent)
        self.client = client
        self.is_edit = client is not None

        title = "Редактировать клиента" if self.is_edit else "Новый клиент"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(500)
        self.setStyleSheet(f"background-color: #F8FAFC;")

        self._build_ui()
        if self.is_edit:
            self._fill_form()

    def _build_ui(self) -> None:
        """Собирает интерфейс диалога."""
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        # Заголовок
        title = QLabel("Редактирование клиента" if self.is_edit else "Новый клиент")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 700;"
        )
        main.addWidget(title)

        # Форма
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # Тип клиента
        self.type_combo = QComboBox()
        self.type_combo.addItem("Физлицо", ClientType.INDIVIDUAL)
        self.type_combo.addItem("Юрлицо", ClientType.COMPANY)
        self.type_combo.setFixedHeight(38)
        self.type_combo.setStyleSheet(self._input_style())
        form.addRow(self._label("Тип:"), self.type_combo)

        # Имя
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Иванов Иван Иванович")
        self.name_input.setFixedHeight(38)
        self.name_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Имя / Название:"), self.name_input)

        # Телефон
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+7 (999) 123-45-67")
        self.phone_input.setFixedHeight(38)
        self.phone_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Телефон:"), self.phone_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("client@mail.ru")
        self.email_input.setFixedHeight(38)
        self.email_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Email:"), self.email_input)

        # Скидка
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0.0, 100.0)
        self.discount_input.setSuffix(" %")
        self.discount_input.setFixedHeight(38)
        self.discount_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Скидка:"), self.discount_input)

        # Заметки
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Комментарий...")
        self.notes_input.setFixedHeight(80)
        self.notes_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Заметки:"), self.notes_input)

        main.addLayout(form)

        # Ошибка
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(
            f"color: #EF4444; font-family: 'Inter'; font-size: 13px;"
        )
        self.error_label.setVisible(False)
        main.addWidget(self.error_label)

        # Кнопки
        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedSize(100, 38)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(self._button_outline())
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.setFixedSize(120, 38)
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
            QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit {{
                background-color: white;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Inter';
                font-size: 13px;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
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
        """Заполняет форму данными клиента (для редактирования)."""
        c = self.client
        if c.type == ClientType.COMPANY:
            self.type_combo.setCurrentIndex(1)
        self.name_input.setText(c.name)
        self.phone_input.setText(c.phone or "")
        self.email_input.setText(c.email or "")
        self.discount_input.setValue(float(c.discount or 0.0))
        self.notes_input.setPlainText(c.notes or "")

    def _on_save(self) -> None:
        """Валидирует и подтверждает."""
        if not self.name_input.text().strip():
            self._show_error("Введите имя клиента")
            return
        if not self.phone_input.text().strip():
            self._show_error("Введите телефон")
            return
        self.accept()

    def _show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def get_data(self) -> dict:
        """Возвращает введённые данные.

        Returns:
            Словарь с полями клиента.
        """
        return {
            "type": self.type_combo.currentData(),
            "name": self.name_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "discount": self.discount_input.value(),
            "notes": self.notes_input.toPlainText().strip() or None,
            "is_active": True,
        }
