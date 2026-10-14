"""Диалог создания/редактирования бригады.

Реализует F-2.5 — управление бригадами.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.models.crew import Crew


COLOR_PRIMARY = "#0EA5A4"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_ERROR = "#EF4444"


class CrewFormDialog(QDialog):
    """Диалог создания/редактирования бригады."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        crew: Optional[Crew] = None,
    ) -> None:
        super().__init__(parent)
        self.crew = crew
        self.is_edit = crew is not None

        title = "Редактировать бригаду" if self.is_edit else "Новая бригада"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(500)
        self.setStyleSheet("background-color: #F8FAFC;")

        self._build_ui()
        if self.is_edit:
            self._fill_form()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(16)

        title = QLabel(
            "Редактирование бригады" if self.is_edit else "Новая бригада"
        )
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 20px; font-weight: 700;"
        )
        main.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Бригада 5")
        self.name_input.setFixedHeight(38)
        self.name_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Название:"), self.name_input)

        self.zone_input = QLineEdit()
        self.zone_input.setPlaceholderText("Центральный район")
        self.zone_input.setFixedHeight(38)
        self.zone_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Зона:"), self.zone_input)

        self.transport_input = QLineEdit()
        self.transport_input.setPlaceholderText("Газель А123БВ")
        self.transport_input.setFixedHeight(38)
        self.transport_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Транспорт:"), self.transport_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Комментарий...")
        self.notes_input.setFixedHeight(80)
        self.notes_input.setStyleSheet(self._input_style())
        form.addRow(self._label("Заметки:"), self.notes_input)

        self.is_active_cb = QCheckBox("Активна")
        self.is_active_cb.setChecked(True)
        self.is_active_cb.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; font-size: 13px;"
        )
        form.addRow(self._label("Статус:"), self.is_active_cb)

        main.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(
            f"color: {COLOR_ERROR}; font-family: 'Inter'; font-size: 13px;"
        )
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        main.addWidget(self.error_label)

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
            QLineEdit, QTextEdit {{
                background-color: white;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Inter';
                font-size: 13px;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus, QTextEdit:focus {{
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
        if self.crew:
            self.name_input.setText(self.crew.name)
            self.zone_input.setText(self.crew.zone or "")
            self.transport_input.setText(self.crew.transport or "")
            self.notes_input.setPlainText(self.crew.notes or "")
            self.is_active_cb.setChecked(bool(self.crew.is_active))

    def _show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def _on_save(self) -> None:
        if not self.name_input.text().strip():
            self._show_error("Введите название бригады")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "zone": self.zone_input.text().strip() or None,
            "transport": self.transport_input.text().strip() or None,
            "notes": self.notes_input.toPlainText().strip() or None,
            "is_active": self.is_active_cb.isChecked(),
        }
