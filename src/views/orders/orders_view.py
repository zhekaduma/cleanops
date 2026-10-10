"""Экран заказов.

Реализует F-4.2: таблица всех заказов компании с фильтрами и поиском.
Позволяет менеджеру видеть все заказы, фильтровать по статусу и дате.

Соответствует макету из Figma.
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
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.repositories.order_repository import OrderRepository
from src.views.widgets.badge import Badge


# Цвета
COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"


class OrdersView(QWidget):
    """Экран заказов.

    Показывает таблицу всех заказов с фильтрами. Данные берутся из
    OrderRepository.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует экран заказов.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.order_repo = OrderRepository()

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._load_orders()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(20)

        # Заголовок + кнопка
        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Заказы")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        title_box.addWidget(title)

        self.subtitle = QLabel("Всего: 0 заказов")
        self.subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 14px;"
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
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-family: 'Inter';
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #0F766E; }}
            """
        )
        header.addWidget(new_btn)

        main.addLayout(header)

        # Фильтры
        filters = self._create_filters()
        main.addWidget(filters)

        # Таблица
        table_block = self._create_table_block()
        main.addWidget(table_block, 1)

    def _create_filters(self) -> QWidget:
        """Создаёт панель фильтров.

        Returns:
            Виджет с фильтрами.
        """
        filters = QWidget()
        layout = QHBoxLayout(filters)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Поиск по клиенту или адресу")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self._on_search)
        layout.addWidget(self.search_input, 2)

        # Статус
        self.status_filter = QComboBox()
        self.status_filter.addItem("Все статусы", None)
        self.status_filter.addItem("Новый", "new")
        self.status_filter.addItem("Назначен", "assigned")
        self.status_filter.addItem("В работе", "in_progress")
        self.status_filter.addItem("Завершён", "completed")
        self.status_filter.addItem("Оплачен", "paid")
        self.status_filter.addItem("Отменён", "cancelled")
        self.status_filter.setFixedHeight(40)
        self.status_filter.setStyleSheet(self._input_style())
        self.status_filter.currentIndexChanged.connect(self._on_filter)
        layout.addWidget(self.status_filter)

        return filters

    def _create_table_block(self) -> QWidget:
        """Создаёт блок с таблицей.

        Returns:
            Виджет таблицы.
        """
        block = QFrame()
        block.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_CARD}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "№", "Клиент", "Адрес", "Дата",
            "Бригада", "Сумма", "Статус",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet(
            f"""
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
            QTableWidget::item:selected {{
                background-color: #F0FDFA;
                color: {COLOR_TEXT_PRIMARY};
            }}
            """
        )
        layout.addWidget(self.table)

        return block

    def _input_style(self) -> str:
        """QSS для полей фильтров."""
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

    def _load_orders(self, status: Optional[str] = None, query: str = "") -> None:
        """Загружает заказы с учётом фильтров.

        Args:
            status: Фильтр по статусу (None = все).
            query: Поисковый запрос.
        """
        if status:
            orders = self.order_repo.get_by_status(status)
        else:
            orders = self.order_repo.get_all()

        # Фильтр по тексту
        if query:
            q = query.lower()
            orders = [
                o for o in orders
                if (o.client and q in o.client.name.lower())
                or (o.object and q in o.object.address.lower())
            ]

        self.subtitle.setText(f"Всего: {len(orders)} заказов")
        self.table.setRowCount(len(orders))

        for i, order in enumerate(orders):
            client_name = order.client.name if order.client else "—"
            address = order.object.address[:35] if order.object else "—"
            date_str = (
                f"{order.planned_date.strftime('%d.%m')} "
                f"{order.planned_start.strftime('%H:%M')}"
                if order.planned_date and order.planned_start else "—"
            )
            crew_name = order.crew.name if order.crew else "—"
            total = f"{float(order.total_price):,.0f} ₽"

            self.table.setItem(i, 0, QTableWidgetItem(f"#{order.order_id}"))
            self.table.setItem(i, 1, QTableWidgetItem(client_name))
            self.table.setItem(i, 2, QTableWidgetItem(address))
            self.table.setItem(i, 3, QTableWidgetItem(date_str))
            self.table.setItem(i, 4, QTableWidgetItem(crew_name))
            self.table.setItem(i, 5, QTableWidgetItem(total))

            # Статус — Badge
            badge = Badge(order.status)
            cell = QWidget()
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(8, 0, 0, 0)
            cell_layout.addWidget(badge)
            cell_layout.addStretch()
            self.table.setCellWidget(i, 6, cell)

            self.table.setRowHeight(i, 52)

    def _on_search(self, text: str) -> None:
        """Обрабатывает ввод в поиск.

        Args:
            text: Текст поиска.
        """
        status = self.status_filter.currentData()
        self._load_orders(status=status, query=text)

    def _on_filter(self) -> None:
        """Обрабатывает изменение фильтра статуса."""
        status = self.status_filter.currentData()
        query = self.search_input.text()
        self._load_orders(status=status, query=query)
