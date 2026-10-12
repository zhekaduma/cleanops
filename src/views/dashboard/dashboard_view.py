"""Экран дашборда."""

from typing import Optional
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QHeaderView, QLabel, QProgressBar,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from src.repositories.order_repository import OrderRepository
from src.services.report_service import ReportService
from src.views.widgets.badge import Badge
from src.views.widgets.kpi_card import KpiCard


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
    """Экран дашборда."""

    new_order_requested = pyqtSignal()

    def __init__(self, user_name: str = "Пользователь", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.user_name = user_name
        self.report_service = ReportService()
        self.order_repo = OrderRepository()
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self.refresh()

        # Автообновление каждые 30 секунд
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30000)

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(24)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel(f"Добрый день, {self.user_name}!")
        title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; font-size: 24px; font-weight: 700;")
        title_box.addWidget(title)
        subtitle = QLabel("Сводка на сегодня")
        subtitle.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 14px;")
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        btn = QPushButton("+  Новый заказ")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(160, 44)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {COLOR_PRIMARY}; color: white;
                border: none; border-radius: 8px;
                font-family: 'Inter'; font-size: 14px; font-weight: 600; }}
            QPushButton:hover {{ background-color: #0F766E; }}
        """)
        btn.clicked.connect(self.new_order_requested.emit)
        header.addWidget(btn)

        # Кнопка обновления
        refresh_btn = QPushButton("🔄  Обновить")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setFixedSize(140, 44)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; color: {COLOR_PRIMARY};
                border: 1px solid {COLOR_PRIMARY}; border-radius: 8px;
                font-family: 'Inter'; font-size: 14px; font-weight: 500; }}
            QPushButton:hover {{ background-color: #F0FDFA; }}
        """)
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)

        main.addLayout(header)

        self.kpi_row = QWidget()
        self.kpi_layout = QHBoxLayout(self.kpi_row)
        self.kpi_layout.setContentsMargins(0, 0, 0, 0)
        self.kpi_layout.setSpacing(24)
        main.addWidget(self.kpi_row)

        orders_block = self._create_orders_block()
        main.addWidget(orders_block, 1)

        crews_block = self._create_crews_block()
        main.addWidget(crews_block)

    def _create_orders_block(self) -> QWidget:
        block = QFrame()
        block.setStyleSheet(f"QFrame {{ background-color: {COLOR_CARD}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}")
        layout = QVBoxLayout(block)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        title = QLabel("Ближайшие заказы")
        title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; font-size: 18px; font-weight: 600; border: none;")
        layout.addWidget(title)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Время", "Клиент", "Адрес", "Бригада", "Статус"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setShowGrid(False)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.setSelectionMode(QTableWidget.NoSelection)
        self.orders_table.setStyleSheet(f"""
            QTableWidget {{ background-color: transparent; border: none; font-family: 'Inter'; font-size: 13px; }}
            QHeaderView::section {{ background-color: transparent; color: {COLOR_TEXT_SECONDARY}; border: none; padding: 8px; font-size: 12px; }}
        """)
        self.orders_table.setFixedHeight(220)
        layout.addWidget(self.orders_table)
        return block

    def _create_crews_block(self) -> QWidget:
        block = QFrame()
        block.setStyleSheet(f"QFrame {{ background-color: {COLOR_CARD}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}")
        layout = QVBoxLayout(block)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        title = QLabel("Загрузка бригад")
        title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; font-size: 18px; font-weight: 600; border: none;")
        layout.addWidget(title)
        self.crews_layout = layout
        return block

    def refresh(self) -> None:
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        kpi = self.report_service.get_dashboard_kpi()
        self.kpi_layout.addWidget(KpiCard(title="Заказов сегодня", value=str(kpi["orders_today"]), subtitle="Активные", subtitle_color=COLOR_SUCCESS, icon="📋"))
        self.kpi_layout.addWidget(KpiCard(title="Выручка за день", value=f"{kpi['revenue_today']:,.0f} Р", subtitle="Оплачено", subtitle_color=COLOR_SUCCESS, icon="💰"))
        self.kpi_layout.addWidget(KpiCard(title="Активных бригад", value=str(kpi["active_crews"]), subtitle="Готовы", subtitle_color=COLOR_TEXT_SECONDARY, icon="👥"))
        self.kpi_layout.addWidget(KpiCard(title="Средний чек", value=f"{kpi['avg_check']:,.0f} Р", subtitle="Оплаченные", subtitle_color=COLOR_TEXT_SECONDARY, icon="📊"))
        self.kpi_layout.addStretch()

        self._load_upcoming_orders()
        self._load_crews()
        print(f"[DashboardView] Обновлено: заказов сегодня = {kpi['orders_today']}")

    def _load_upcoming_orders(self) -> None:
        orders = self.order_repo.get_upcoming(limit=5)
        self.orders_table.setRowCount(len(orders))
        for i, order in enumerate(orders):
            time_str = order.planned_start.strftime("%H:%M") if order.planned_start else "—"
            client_name = order.client.name if order.client else "—"
            address = order.object.address[:30] if order.object else "—"
            crew_name = order.crew.name if order.crew else "—"
            self.orders_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.orders_table.setItem(i, 1, QTableWidgetItem(client_name))
            self.orders_table.setItem(i, 2, QTableWidgetItem(address))
            self.orders_table.setItem(i, 3, QTableWidgetItem(crew_name))
            badge = Badge(order.status)
            cell = QWidget()
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(8, 0, 0, 0)
            cl.addWidget(badge)
            cl.addStretch()
            self.orders_table.setCellWidget(i, 4, cell)
            self.orders_table.setRowHeight(i, 52)

    def _load_crews(self) -> None:
        while self.crews_layout.count() > 1:
            item = self.crews_layout.takeAt(self.crews_layout.count() - 1)
            if item.widget():
                item.widget().deleteLater()

        workloads = self.report_service.get_workload_by_crew()
        for w in workloads[:4]:
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 4, 0, 4)
            name = QLabel(w["name"])
            name.setFixedWidth(120)
            name.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; font-size: 13px; border: none;")
            rl.addWidget(name)
            bar = QProgressBar()
            bar.setValue(int(w["workload"]))
            bar.setFixedHeight(12)
            bar.setTextVisible(False)
            color = COLOR_ERROR if w["workload"] > 80 else (COLOR_WARNING if w["workload"] > 50 else COLOR_SUCCESS)
            bar.setStyleSheet(f"""
                QProgressBar {{ background-color: #F1F5F9; border: none; border-radius: 6px; }}
                QProgressBar::chunk {{ background-color: {color}; border-radius: 6px; }}
            """)
            rl.addWidget(bar, 1)
            percent = QLabel(f"{w['workload']:.0f}%")
            percent.setFixedWidth(50)
            percent.setAlignment(Qt.AlignRight)
            percent.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 13px; border: none;")
            rl.addWidget(percent)
            self.crews_layout.addWidget(row)
