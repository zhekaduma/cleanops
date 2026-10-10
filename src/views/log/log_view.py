"""Экран журнала действий.

Реализует F-7.3: audit log с фильтрами по действию и пользователю.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.repositories.audit_repository import AuditLogRepository


COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"


# Цвета действий
ACTION_COLORS = {
    "create": ("#D1FAE5", "#047857", "Создание"),
    "update": ("#DBEAFE", "#1D4ED8", "Изменение"),
    "delete": ("#FEE2E2", "#B91C1C", "Удаление"),
    "login": ("#CCFBF1", "#0F766E", "Вход"),
    "logout": ("#E2E8F0", "#64748B", "Выход"),
}


class LogView(QWidget):
    """Экран журнала."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует экран."""
        super().__init__(parent)
        self.audit_repo = AuditLogRepository()

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._load_logs()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(20)

        # Заголовок
        title_box = QVBoxLayout()
        title = QLabel("Журнал действий")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        title_box.addWidget(title)

        self.subtitle = QLabel("Всего записей: 0")
        self.subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 14px;"
        )
        title_box.addWidget(self.subtitle)
        main.addLayout(title_box)

        # Фильтры
        filters = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Поиск по сущности или ID")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self._load_logs)
        filters.addWidget(self.search_input, 2)

        self.action_filter = QComboBox()
        self.action_filter.addItem("Все действия", None)
        self.action_filter.addItem("Создание", "create")
        self.action_filter.addItem("Изменение", "update")
        self.action_filter.addItem("Удаление", "delete")
        self.action_filter.addItem("Вход", "login")
        self.action_filter.addItem("Выход", "logout")
        self.action_filter.setFixedHeight(40)
        self.action_filter.setStyleSheet(self._input_style())
        self.action_filter.currentIndexChanged.connect(self._load_logs)
        filters.addWidget(self.action_filter)

        main.addLayout(filters)

        # Таблица
        block = QFrame()
        block.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_CARD}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Время", "Пользователь", "Действие", "Объект", "Детали",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet(self._table_style())
        layout.addWidget(self.table)

        main.addWidget(block, 1)

    def _input_style(self) -> str:
        """QSS для полей."""
        return f"""
            QLineEdit, QComboBox {{
                background-color: {COLOR_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-family: 'Inter';
                font-size: 13px;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """

    def _table_style(self) -> str:
        """QSS для таблицы."""
        return f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                font-family: 'Inter';
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-bottom: 1px solid {COLOR_BORDER};
                padding: 12px 8px;
                font-size: 12px;
                font-weight: 500;
                text-align: left;
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                border-bottom: 1px solid #F1F5F9;
            }}
        """

    def _load_logs(self) -> None:
        """Загружает записи журнала."""
        action = self.action_filter.currentData()
        query = self.search_input.text().lower()

        if action:
            logs = self.audit_repo.get_by_action(action)
        else:
            logs = self.audit_repo.get_recent(limit=100)

        if query:
            logs = [
                log for log in logs
                if query in (log.entity or "").lower()
                or query in str(log.entity_id or "")
            ]

        self.subtitle.setText(f"Всего записей: {len(logs)}")
        self.table.setRowCount(len(logs))

        for i, log in enumerate(logs):
            # Время
            time_str = (
                log.created_at.strftime("%d.%m.%Y %H:%M:%S")
                if log.created_at else "—"
            )

            # Пользователь
            user_name = "Система"
            if log.user:
                user_name = log.user.full_name

            # Действие — badge
            bg, fg, label = ACTION_COLORS.get(
                log.action, ("#E2E8F0", "#64748B", log.action)
            )
            action_badge = QLabel(label)
            action_badge.setAlignment(Qt.AlignCenter)
            action_badge.setFixedSize(100, 24)
            action_badge.setStyleSheet(
                f"background-color: {bg}; color: {fg}; "
                f"border-radius: 12px; font-size: 12px; font-weight: 500;"
            )
            cell = QWidget()
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(8, 0, 0, 0)
            cell_layout.addWidget(action_badge)
            cell_layout.addStretch()
            self.table.setCellWidget(i, 2, cell)

            # Объект
            entity = f"{log.entity or '—'}"
            if log.entity_id:
                entity += f" #{log.entity_id}"

            self.table.setItem(i, 0, QTableWidgetItem(time_str))
            self.table.setItem(i, 1, QTableWidgetItem(user_name))
            self.table.setItem(i, 3, QTableWidgetItem(entity))
            self.table.setItem(i, 4, QTableWidgetItem(log.details or "—"))

            self.table.setRowHeight(i, 52)
