"""Экран дашборда.

Главный экран менеджера после входа. Показывает KPI, ближайшие заказы
и загрузку бригад.

Соответствует макету Figma: приветствие, 4 KPI-карточки, таблица
заказов, прогресс-бары загрузки бригад.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.services.report_service import ReportService
from src.views.widgets.badge import STATUS_LABELS
from src.views.widgets.badge import Badge
from src.views.widgets.kpi_card import KpiCard


# Цвета
COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"
COLOR_SUCCESS = "#22C55E"
COLOR_WARNING = "#F59E0B"
COLOR_ERROR = "#EF4444"


class DashboardView(QWidget):
    """Экран дашборда.

    Показывает KPI, ближайшие заказы, загрузку бригад. Данные берутся
    из ReportService.
    """

    def __init__(
        self,
        user_name: str = "Пользователь",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализирует дашборд.

        Args:
            user_name: Имя пользователя для приветствия.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.user_name = user_name
        self.report_service = ReportService()

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._load_data()

    def _build_ui(self) -> None:
        """Собирает интерфейс дашборда."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(24)

        # Заголовок + кнопка
        header = self._create_header()
        main.addWidget(header)

        # KPI-карточки
        kpi_row = self._create_kpi_row()
        main.addWidget(kpi_row)

        # Ближайшие заказы
        orders_block = self._create_orders_block()
        main.addWidget(orders_block, 1)

        # Загрузка бригад
        crews_block = self._create_crews_block()
        main.addWidget(crews_block)

    def _create_header(self) -> QWidget:
        """Создаёт заголовок с приветствием и кнопкой.

        Returns:
            Виджет заголовка.
        """
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # Приветствие
        greeting = QWidget()
        greet_layout = QVBoxLayout(greeting)
        greet_layout.setContentsMargins(0, 0, 0, 0)
        greet_layout.setSpacing(4)

        title = QLabel(f"Добрый день, {self.user_name}!")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        greet_layout.addWidget(title)

        subtitle = QLabel("Сводка на сегодня")
        subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 14px;"
        )
        greet_layout.addWidget(subtitle)

        layout.addWidget(greeting)
        layout.addStretch()

        # Кнопка «+ Новый заказ»
        btn = QPushButton("+  Новый заказ")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(160, 44)
        btn.setStyleSheet(
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
            QPushButton:hover {{
                background-color: #0F766E;
            }}
            """
        )
        layout.addWidget(btn)

        return header

    def _create_kpi_row(self) -> QWidget:
        """Создаёт ряд KPI-карточек.

        Returns:
            Виджет с 4 KPI-карточками.
        """
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        kpi = self.report_service.get_dashboard_kpi()

        self.kpi_orders = KpiCard(
            title="Заказов сегодня",
            value=str(kpi["orders_today"]),
            subtitle="↑ Активные заказы",
            subtitle_color=COLOR_SUCCESS,
            icon="📋",
        )
        layout.addWidget(self.kpi_orders)

        self.kpi_revenue = KpiCard(
            title="Выручка за день",
            value=f"{kpi['revenue_today']:,.0f} ₽",
            subtitle="↑ Оплачено",
            subtitle_color=COLOR_SUCCESS,
            icon="💰",
        )
        layout.addWidget(self.kpi_revenue)

        self.kpi_crews = KpiCard(
            title="Активных бригад",
            value=str(kpi["active_crews"]),
            subtitle="Готовы к работе",
            subtitle_color=COLOR_TEXT_SECONDARY,
            icon="👥",
        )
        layout.addWidget(self.kpi_crews)

        self.kpi_avg = KpiCard(
            title="Средний чек",
            value=f"{kpi['avg_check']:,.0f} ₽",
            subtitle="По оплаченным",
            subtitle_color=COLOR_TEXT_SECONDARY,
            icon="📊",
        )
        layout.addWidget(self.kpi_avg)

        layout.addStretch()
        return row

    def _create_orders_block(self) -> QWidget:
        """Создаёт блок «Ближайшие заказы».

        Returns:
            Виджет блока.
        """
        block = QFrame()
        block.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLOR_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            """
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Заголовок + ссылка
        header = QHBoxLayout()

        title = QLabel("Ближайшие заказы")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 600; border: none;"
        )
        header.addWidget(title)
        header.addStretch()

        link = QLabel("Все заказы →")
        link.setStyleSheet(
            f"color: {COLOR_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 14px; border: none;"
        )
        link.setCursor(Qt.PointingHandCursor)
        header.addWidget(link)

        layout.addLayout(header)

        # Таблица
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(
            ["Время", "Клиент", "Адрес", "Бригада", "Статус"]
        )
        self.orders_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setShowGrid(False)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.setSelectionMode(QTableWidget.NoSelection)
        self.orders_table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                font-family: 'Inter';
                font-size: 14px;
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                padding: 8px;
                font-size: 12px;
                text-align: left;
            }}
            """
        )
        self.orders_table.setFixedHeight(220)

        layout.addWidget(self.orders_table)
        return block

    def _create_crews_block(self) -> QWidget:
        """Создаёт блок «Загрузка бригад».

        Returns:
            Виджет блока.
        """
        block = QFrame()
        block.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLOR_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            """
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Загрузка бригад")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 600; border: none;"
        )
        layout.addWidget(title)

        # Заполним прогресс-барами
        self.crews_layout = layout
        self._load_crews()

        return block

    def _load_data(self) -> None:
        """Загружает данные для дашборда."""
        self._load_upcoming_orders()

    def _load_upcoming_orders(self) -> None:
        """Заполняет таблицу ближайших заказов."""
        from src.repositories.order_repository import OrderRepository

        order_repo = OrderRepository()
        orders = order_repo.get_upcoming(limit=5)

        self.orders_table.setRowCount(len(orders))

        for i, order in enumerate(orders):
            time_str = (
                order.planned_start.strftime("%H:%M")
                if order.planned_start else "—"
            )
            client_name = (
                order.client.name if order.client else "—"
            )
            address = order.object.address if order.object else "—"
            crew_name = order.crew.name if order.crew else "—"

            self.orders_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.orders_table.setItem(i, 1, QTableWidgetItem(client_name))
            self.orders_table.setItem(i, 2, QTableWidgetItem(address[:30]))
            self.orders_table.setItem(i, 3, QTableWidgetItem(crew_name))

            # Статус — Badge
            badge = Badge(order.status)
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(8, 0, 0, 0)
            cell_layout.addWidget(badge)
            cell_layout.addStretch()
            self.orders_table.setCellWidget(i, 4, cell_widget)

    def _load_crews(self) -> None:
        """Заполняет блок загрузки бригад."""
        workloads = self.report_service.get_workload_by_crew()

        for w in workloads[:4]:  # первые 4
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 4, 0, 4)

            # Имя бригады
            name = QLabel(w["name"])
            name.setFixedWidth(120)
            name.setStyleSheet(
                f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
                f"font-size: 13px; border: none;"
            )
            row_layout.addWidget(name)

            # Прогресс-бар
            bar = QProgressBar()
            bar.setValue(int(w["workload"]))
            bar.setFixedHeight(12)
            bar.setTextVisible(False)

            # Цвет по загрузке
            if w["workload"] > 80:
                color = COLOR_ERROR
            elif w["workload"] > 50:
                color = COLOR_WARNING
            else:
                color = COLOR_SUCCESS

            bar.setStyleSheet(
                f"""
                QProgressBar {{
                    background-color: #F1F5F9;
                    border: none;
                    border-radius: 6px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 6px;
                }}
                """
            )
            row_layout.addWidget(bar, 1)

            # Процент
            percent = QLabel(f"{w['workload']:.0f}%")
            percent.setFixedWidth(50)
            percent.setAlignment(Qt.AlignRight)
            percent.setStyleSheet(
                f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
                f"font-size: 13px; border: none;"
            )
            row_layout.addWidget(percent)

            self.crews_layout.addWidget(row)
