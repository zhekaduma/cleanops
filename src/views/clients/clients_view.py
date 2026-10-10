"""Экран клиентов.

Реализует F-2.2: таблица клиентов с поиском и фильтрами.
Показывает контактные данные, количество заказов и сумму.

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

from src.repositories.client_repository import ClientRepository
from src.repositories.order_repository import OrderRepository


# Цвета
COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"
COLOR_SUCCESS = "#22C55E"


class ClientsView(QWidget):
    """Экран клиентов.

    Показывает таблицу клиентов с фильтрами. Данные берутся из
    ClientRepository и OrderRepository (для подсчёта заказов).
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует экран клиентов.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.client_repo = ClientRepository()
        self.order_repo = OrderRepository()

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._load_clients()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(20)

        # Заголовок + кнопка
        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Клиенты")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        title_box.addWidget(title)

        self.subtitle = QLabel("Всего: 0 клиентов")
        self.subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 14px;"
        )
        title_box.addWidget(self.subtitle)

        header.addLayout(title_box)
        header.addStretch()

        new_btn = QPushButton("+  Новый клиент")
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

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Поиск по имени, телефону, email")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self._on_search)
        layout.addWidget(self.search_input, 2)

        self.type_filter = QComboBox()
        self.type_filter.addItem("Все типы", None)
        self.type_filter.addItem("Физлицо", "individual")
        self.type_filter.addItem("Юрлицо", "company")
        self.type_filter.setFixedHeight(40)
        self.type_filter.setStyleSheet(self._input_style())
        self.type_filter.currentIndexChanged.connect(self._on_filter)
        layout.addWidget(self.type_filter)

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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Имя", "Телефон", "Email", "Заказов", "Сумма", "Скидка",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

    def _load_clients(
        self,
        client_type: Optional[str] = None,
        query: str = "",
    ) -> None:
        """Загружает клиентов с учётом фильтров.

        Args:
            client_type: Тип клиента (None = все).
            query: Поисковый запрос.
        """
        if client_type:
            clients = self.client_repo.get_by_type(client_type)
        else:
            clients = self.client_repo.get_all()

        # Фильтр по тексту
        if query:
            q = query.lower()
            clients = [
                c for c in clients
                if (q in c.name.lower())
                or (c.phone and q in c.phone.lower())
                or (c.email and q in c.email.lower())
            ]

        self.subtitle.setText(f"Всего: {len(clients)} клиентов")
        self.table.setRowCount(len(clients))

        for i, client in enumerate(clients):
            # Считаем заказы клиента
            orders = self.order_repo.get_by_client(client.client_id)
            orders_count = len(orders)
            total_sum = sum(float(o.total_price) for o in orders)

            self.table.setItem(i, 0, QTableWidgetItem(client.name))
            self.table.setItem(i, 1, QTableWidgetItem(client.phone or "—"))
            self.table.setItem(i, 2, QTableWidgetItem(client.email or "—"))
            self.table.setItem(i, 3, QTableWidgetItem(str(orders_count)))
            self.table.setItem(
                i, 4, QTableWidgetItem(f"{total_sum:,.0f} ₽")
            )

            # Скидка — badge
            discount = float(client.discount) if client.discount else 0.0
            if discount > 0:
                badge = QLabel(f"{discount:.0f}%")
                badge.setFixedSize(50, 24)
                badge.setAlignment(Qt.AlignCenter)
                badge.setStyleSheet(
                    f"""
                    background-color: #D1FAE5;
                    color: #047857;
                    border-radius: 12px;
                    font-family: 'Inter';
                    font-size: 12px;
                    font-weight: 500;
                    """
                )
                cell = QWidget()
                cell_layout = QHBoxLayout(cell)
                cell_layout.setContentsMargins(8, 0, 0, 0)
                cell_layout.addWidget(badge)
                cell_layout.addStretch()
                self.table.setCellWidget(i, 5, cell)
            else:
                self.table.setItem(i, 5, QTableWidgetItem("—"))

            self.table.setRowHeight(i, 52)

    def _on_search(self, text: str) -> None:
        """Обрабатывает ввод в поиск."""
        client_type = self.type_filter.currentData()
        self._load_clients(client_type=client_type, query=text)

    def _on_filter(self) -> None:
        """Обрабатывает изменение фильтра типа."""
        client_type = self.type_filter.currentData()
        query = self.search_input.text()
        self._load_clients(client_type=client_type, query=query)
