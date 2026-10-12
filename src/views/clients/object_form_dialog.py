"""Модальное окно создания/редактирования объекта уборки.

Форма с полями: адрес, площадь, тип, заметки о доступе.
Соответствует F-2.1 из ТЗ.
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

from src.models.client import Object, ObjectType


COLOR_PRIMARY = "#0EA5A4"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"


class ObjectFormDialog(QDialog):
    """Модальное окно создания/редактирования объекта."""

    def __init__(
        self,
        client_id: int,
        parent: Optional[QWidget] = None,
        obj: Optional[Object] = None,
    ) -> None:
        """Инициализирует диалог.

        Args:
            client_id: ID клиента-владельца.
            parent: Родительский виджет.
            obj: Объект для редактирования. None — создание.
        """
        super().__init__(parent)
        self.client_id = client_id
        self.obj = obj
        self.is_edit = obj is not None

        title = "Редактировать объект" if self.is_edit else "Новый объект"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(500)
        self.setStyleSheet("background-color: #F8FAFC;")

        self._build_ui()
        if self.is_edit:
            self._fill_form()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        title = QLabel("Редактирование объекта" if self.is_edit else "Новый объект")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 700;"
        )
        main.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # Адрес
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("г. Новосибирск, ул. Ленина, 5, кв. 12")
        self.address_input.setFixedHeight(38)
        self.address_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Адрес:"), self.address_input)

        # Площадь
        self.area_input = QDoubleSpinBox()
        self.area_input.setRange(1.0, 10000.0)
        self.area_input.setValue(60.0)
        self.area_input.setSuffix(" м²")
        self.area_input.setFixedHeight(38)
        self.area_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Площадь:"), self.area_input)

        # Тип объекта
        self.type_combo = QComboBox()
        self.type_combo.addItem("Квартира", ObjectType.APARTMENT)
        self.type_combo.addItem("Дом", ObjectType.HOUSE)
        self.type_combo.addItem("Офис", ObjectType.OFFICE)
        self.type_combo.addItem("Склад", ObjectType.WAREHOUSE)
        self.type_combo.addItem("Другое", ObjectType.OTHER)
        self.type_combo.setFixedHeight(38)
        self.type_combo.setStyleSheet(self._input_style())
        form.addRow(self._label("Тип:"), self.type_combo)

        # Заметки о доступе
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Код домофона, пропуск, особенности...")
        self.notes_input.setFixedHeight(80)
        self.notes_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Доступ:"), self.notes_input)

        main.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(
            "color: #EF4444; font-family: 'Inter'; font-size: 13px;"
        )
        self.error_label.setVisible(False)
        main.addWidget(self.error_label)

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
        if self.obj:
            self.address_input.setText(self.obj.address)
            self.area_input.setValue(float(self.obj.area))
            idx = self.type_combo.findData(self.obj.object_type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
            self.notes_input.setPlainText(self.obj.access_notes or "")

    def _on_save(self) -> None:
        if not self.address_input.text().strip():
            self._show_error("Введите адрес")
            return
        if self.area_input.value() <= 0:
            self._show_error("Площадь должна быть больше 0")
            return
        self.accept()

    def _show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def get_data(self) -> dict:
        """Возвращает введённые данные.

        Returns:
            Словарь с полями объекта.
        """
        return {
            "client_id": self.client_id,
            "address": self.address_input.text().strip(),
            "area": self.area_input.value(),
            "object_type": self.type_combo.currentData(),
            "access_notes": self.notes_input.toPlainText().strip() or None,
            "is_active": True,
        }
