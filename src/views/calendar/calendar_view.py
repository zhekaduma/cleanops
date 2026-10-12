"""Экран календаря заказов.

Реализует F-4.1: календарь по дням/неделям с бригадами.
Показывает заказы на неделю в виде сетки: дни × бригады.
"""

from datetime import date, timedelta
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.models.order import OrderStatus
from src.repositories.crew_repository import CrewRepository
from src.repositories.order_repository import OrderRepository


# Цвета
COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"

# Цвета статусов (фон + полоска слева)
STATUS_COLORS = {
    "new": ("#E2E8F0", "#64748B"),
    "calculated": ("#DBEAFE", "#1D4ED8"),
    "confirmed": ("#C7D2FE", "#4338CA"),
    "assigned": ("#C7D2FE", "#4338CA"),
    "in_progress": ("#FEF3C7", "#D97706"),
    "completed": ("#D1FAE5", "#047857"),
    "paid": ("#A7F3D0", "#065F46"),
    "cancelled": ("#FEE2E2", "#B91C1C"),
}

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MONTHS = [
    "янв", "фев", "мар", "апр", "май", "июн",
    "июл", "авг", "сен", "окт", "ноя", "дек",
]


class CalendarView(QWidget):
    """Экран календаря.

    Показывает заказы на неделю в виде сетки: дни × бригады.

    Signals:
        new_order_requested: Запрос на создание нового заказа.
    """

    from PyQt5.QtCore import pyqtSignal
    new_order_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует экран."""
        super().__init__(parent)
        self.order_repo = OrderRepository()
        self.crew_repo = CrewRepository()

        # Текущая дата — начало недели (понедельник)
        self.current_date = date.today()
        # Сдвигаем к понедельнику
        self.current_date -= timedelta(days=self.current_date.weekday())

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._load_week()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(20)

        # Заголовок
        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Календарь")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        title_box.addWidget(title)

        self.subtitle = QLabel("")
        self.subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 14px;"
        )
        title_box.addWidget(self.subtitle)

        header.addLayout(title_box)
        header.addStretch()

        new_btn = QPushButton("+  Новый заказ")
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setFixedSize(160, 44)
        new_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY}; color: white;
                border: none; border-radius: 8px;
                font-family: 'Inter'; font-size: 14px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #0F766E; }}
            """
        )
        new_btn.clicked.connect(self.new_order_requested.emit)
        header.addWidget(new_btn)

        main.addLayout(header)

        # Навигация по неделям
        nav = self._create_navigation()
        main.addWidget(nav)

        # Сетка календаря (в ScrollArea)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: 1px solid {COLOR_BORDER}; "
            f"border-radius: 12px; background-color: {COLOR_CARD}; }}"
        )

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet(f"background-color: {COLOR_CARD};")
        self.grid_layout = QVBoxLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        self.grid_layout.setSpacing(0)

        scroll.setWidget(self.grid_widget)
        main.addWidget(scroll, 1)

    def _create_navigation(self) -> QWidget:
        """Создаёт панель навигации (◀ неделя ▶)."""
        nav = QWidget()
        layout = QHBoxLayout(nav)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        prev_btn = QPushButton("◀")
        prev_btn.setFixedSize(40, 40)
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.setStyleSheet(self._nav_button_style())
        prev_btn.clicked.connect(self._prev_week)
        layout.addWidget(prev_btn)

        self.week_label = QLabel("")
        self.week_label.setFixedWidth(200)
        self.week_label.setAlignment(Qt.AlignCenter)
        self.week_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 15px; font-weight: 600;"
        )
        layout.addWidget(self.week_label)

        next_btn = QPushButton("▶")
        next_btn.setFixedSize(40, 40)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.setStyleSheet(self._nav_button_style())
        next_btn.clicked.connect(self._next_week)
        layout.addWidget(next_btn)

        today_btn = QPushButton("Сегодня")
        today_btn.setFixedHeight(40)
        today_btn.setCursor(Qt.PointingHandCursor)
        today_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_PRIMARY};
                border: 1px solid {COLOR_PRIMARY};
                border-radius: 8px;
                padding: 0 16px;
                font-family: 'Inter'; font-size: 13px; font-weight: 500;
            }}
            QPushButton:hover {{ background-color: #F0FDFA; }}
            """
        )
        today_btn.clicked.connect(self._go_today)
        layout.addWidget(today_btn)

        layout.addStretch()

        # Фильтр по бригаде
        filter_label = QLabel("Бригада:")
        filter_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 13px;"
        )
        layout.addWidget(filter_label)

        self.crew_filter = QComboBox()
        self.crew_filter.addItem("Все бригады", None)
        for crew in self.crew_repo.get_active():
            self.crew_filter.addItem(crew.name, crew.crew_id)
        self.crew_filter.setFixedHeight(40)
        self.crew_filter.setMinimumWidth(180)
        self.crew_filter.setStyleSheet(
            f"""
            QComboBox {{
                background-color: white;
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-family: 'Inter'; font-size: 13px;
                color: {COLOR_TEXT_PRIMARY};
            }}
            """
        )
        self.crew_filter.currentIndexChanged.connect(self._load_week)
        layout.addWidget(self.crew_filter)

        return nav

    def _nav_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: white;
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{ background-color: #F1F5F9; }}
        """

    def _load_week(self) -> None:
        """Перерисовывает неделю."""
        # Очищаем сетку
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

        # Заголовок недели
        start = self.current_date
        end = start + timedelta(days=6)
        self.subtitle.setText(
            f"{start.strftime('%d.%m.%Y')} — {end.strftime('%d.%m.%Y')}"
        )
        self.week_label.setText(
            f"{start.day:02d} {MONTHS[start.month-1]} — "
            f"{end.day:02d} {MONTHS[end.month-1]}"
        )

        # Получаем бригады
        crew_filter_id = self.crew_filter.currentData()
        if crew_filter_id:
            crews = [self.crew_repo.get_by_id(crew_filter_id)]
            crews = [c for c in crews if c]
        else:
            crews = self.crew_repo.get_active()

        # Получаем заказы за неделю
        orders = self.order_repo.get_by_date_range(start, end)

        # Рисуем заголовок с днями
        header = self._create_week_header()
        self.grid_layout.addWidget(header)

        # Рисуем строки для каждой бригады
        for crew in crews:
            row = self._create_crew_row(crew, orders, start)
            self.grid_layout.addWidget(row)

        self.grid_layout.addStretch()

    def _clear_layout(self, layout) -> None:
        """Рекурсивно очищает layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

    def _create_week_header(self) -> QWidget:
        """Создаёт заголовок с днями недели."""
        header = QWidget()
        header.setFixedHeight(50)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Пустая ячейка под названия бригад
        empty = QLabel("")
        empty.setFixedWidth(120)
        empty.setStyleSheet(
            f"border-bottom: 1px solid {COLOR_BORDER};"
        )
        layout.addWidget(empty)

        today = date.today()
        for i in range(7):
            day = self.current_date + timedelta(days=i)
            is_today = day == today

            cell = QLabel(f"{WEEKDAYS[i]}\n{day.day:02d}")
            cell.setAlignment(Qt.AlignCenter)
            cell.setStyleSheet(
                f"""
                color: {'#0EA5A4' if is_today else COLOR_TEXT_PRIMARY};
                background-color: {'#F0FDFA' if is_today else 'transparent'};
                font-family: 'Inter';
                font-size: 12px;
                font-weight: {'700' if is_today else '500'};
                border-bottom: 1px solid {COLOR_BORDER};
                padding: 8px 4px;
                """
            )
            layout.addWidget(cell, 1)

        return header

    def _create_crew_row(self, crew, orders: list, start: date) -> QWidget:
        """Создаёт строку для бригады (с карточками заказов)."""
        row = QWidget()
        row.setStyleSheet(f"border-bottom: 1px solid {COLOR_BORDER};")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(4)

        # Название бригады
        name = QLabel(crew.name)
        name.setFixedWidth(120)
        name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 600; padding-left: 8px;"
        )
        layout.addWidget(name)

        # Заказы на неделю по дням
        for i in range(7):
            day = start + timedelta(days=i)
            day_orders = [
                o for o in orders
                if o.crew_id == crew.crew_id and o.planned_date == day
            ]

            cell = self._create_day_cell(day_orders)
            layout.addWidget(cell, 1)

        return row

    def _create_day_cell(self, orders: list) -> QWidget:
        """Создаёт ячейку дня с карточками заказов."""
        cell = QWidget()
        layout = QVBoxLayout(cell)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        for order in orders[:3]:  # максимум 3 заказа
            card = self._create_order_card(order)
            layout.addWidget(card)

        if len(orders) > 3:
            more = QLabel(f"+{len(orders) - 3}")
            more.setAlignment(Qt.AlignCenter)
            more.setStyleSheet(
                f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 11px;"
            )
            layout.addWidget(more)

        layout.addStretch()
        return cell

    def _create_order_card(self, order) -> QWidget:
        """Создаёт карточку заказа в ячейке."""
        card = QFrame()
        bg, fg = STATUS_COLORS.get(order.status, ("#E2E8F0", "#64748B"))

        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {bg};
                border-left: 3px solid {fg};
                border-radius: 4px;
            }}
            """
        )
        card.setFixedHeight(56)
        card.setToolTip(
            f"Заказ #{order.order_id}\n"
            f"{order.client.name if order.client else '—'}\n"
            f"{float(order.total_price):,.0f} ₽"
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(0)

        time_str = (
            order.planned_start.strftime("%H:%M")
            if order.planned_start else "—"
        )
        time_label = QLabel(time_str)
        time_label.setStyleSheet(
            f"color: {fg}; font-family: 'Inter'; font-size: 10px; font-weight: 700;"
        )
        layout.addWidget(time_label)

        client_name = order.client.name if order.client else "—"
        if len(client_name) > 15:
            client_name = client_name[:15] + "…"
        name_label = QLabel(client_name)
        name_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 10px; font-weight: 500;"
        )
        layout.addWidget(name_label)

        return card

    def _prev_week(self) -> None:
        self.current_date -= timedelta(days=7)
        self._load_week()

    def _next_week(self) -> None:
        self.current_date += timedelta(days=7)
        self._load_week()

    def _go_today(self) -> None:
        self.current_date = date.today()
        self.current_date -= timedelta(days=self.current_date.weekday())
        self._load_week()

    def refresh(self) -> None:
        """Публичный метод для перезагрузки."""
        self._load_week()
