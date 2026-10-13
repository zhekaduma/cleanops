"""Экран журнала действий.

Реализует F-7.3: audit log с фильтрами по действию и пользователю.
"""

from datetime import date, timedelta
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
        filters.setSpacing(12)

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Поиск по сущности или ID")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self._load_logs)
        filters.addWidget(self.search_input, 2)

        # Фильтр по действию
        self.action_filter = QComboBox()
        self.action_filter.addItem("Все действия", None)
        self.action_filter.addItem("Создание", "create")
        self.action_filter.addItem("Изменение", "update")
        self.action_filter.addItem("Удаление", "delete")
        self.action_filter.addItem("Вход", "login")
        self.action_filter.addItem("Выход", "logout")
        self.action_filter.setFixedHeight(40)
        self.action_filter.setMinimumWidth(160)
        self.action_filter.setStyleSheet(self._input_style())
        self.action_filter.currentIndexChanged.connect(self._load_logs)
        filters.addWidget(self.action_filter)

        # Фильтр по периоду ← НОВЫЙ
        self.period_filter = QComboBox()
        self.period_filter.addItem("За всё время", "all")
        self.period_filter.addItem("Сегодня", "today")
        self.period_filter.addItem("За неделю", "week")
        self.period_filter.addItem("За месяц", "month")
        self.period_filter.addItem("За год", "year")
        self.period_filter.setFixedHeight(40)
        self.period_filter.setMinimumWidth(160)
        self.period_filter.setStyleSheet(self._input_style())
        self.period_filter.currentIndexChanged.connect(self._load_logs)
        filters.addWidget(self.period_filter)

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
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Время", "Пользователь", "Действие", "Объект",
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

    def _get_date_range(self) -> tuple:
        """Возвращает диапазон дат для фильтра периода.

        Returns:
            Кортеж (start, end) или (None, None) для «За всё время».
        """
        period = self.period_filter.currentData()
        today = date.today()

        if period == "today":
            return today, today
        elif period == "week":
            return today - timedelta(days=7), today
        elif period == "month":
            return today - timedelta(days=30), today
        elif period == "year":
            return today - timedelta(days=365), today
        else:  # all
            return None, None

    def _load_logs(self) -> None:
        """Загружает записи журнала с учётом фильтров."""
        action = self.action_filter.currentData()
        query = self.search_input.text().lower()
        start, end = self._get_date_range()

        # 1. Загружаем по периоду
        if start and end:
            logs = self.audit_repo.get_by_date_range(start, end)
        else:
            logs = self.audit_repo.get_recent(limit=500)

        # 2. Фильтр по действию
        if action:
            logs = [log for log in logs if log.action == action]

        # 3. Поиск по сущности / ID
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

            time_item = QTableWidgetItem(time_str)
            # Детали — в tooltip при наведении
            if log.details:
                time_item.setToolTip(f"Детали: {log.details}")

            self.table.setItem(i, 0, time_item)
            self.table.setItem(i, 1, QTableWidgetItem(user_name))
            self.table.setItem(i, 3, QTableWidgetItem(entity))

            self.table.setRowHeight(i, 52)
