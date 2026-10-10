"""Экран финансов и отчётности.

Реализует F-6.1–F-6.4: KPI, статистика способов оплаты, последние платежи.
Данные берутся из ReportService и PaymentRepository.

Соответствует макету из Figma.
"""

from datetime import date, timedelta
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models.payment import PaymentMethod
from src.repositories.payment_repository import PaymentRepository
from src.services.report_service import ReportService
from src.views.widgets.kpi_card import KpiCard


# Цвета
COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"
COLOR_SUCCESS = "#22C55E"


class FinanceView(QWidget):
    """Экран финансов.

    Показывает KPI, способы оплаты и последние платежи.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует экран финансов.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.report_service = ReportService()
        self.payment_repo = PaymentRepository()

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._load_data()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(24)

        # Заголовок + экспорт
        header = self._create_header()
        main.addWidget(header)

        # KPI-карточки
        kpi_row = self._create_kpi_row()
        main.addWidget(kpi_row)

        # Диаграмма способов оплаты + таблица
        bottom = QHBoxLayout()
        bottom.setSpacing(24)

        payments_chart = self._create_payment_methods_block()
        bottom.addWidget(payments_chart, 1)

        recent_block = self._create_recent_payments_block()
        bottom.addWidget(recent_block, 2)

        main.addLayout(bottom, 1)

    def _create_header(self) -> QWidget:
        """Создаёт заголовок + период + кнопку экспорта.

        Returns:
            Виджет заголовка.
        """
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        title_box = QVBoxLayout()
        title = QLabel("Финансы")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        title_box.addWidget(title)

        self.period_label = QLabel("Последние 30 дней")
        self.period_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 14px;"
        )
        title_box.addWidget(self.period_label)

        layout.addLayout(title_box)
        layout.addStretch()

        export_btn = QPushButton("📥  Экспорт")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setFixedSize(140, 44)
        export_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                font-family: 'Inter';
                font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #F1F5F9; }}
            """
        )
        layout.addWidget(export_btn)

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

        # За период (30 дней)
        end = date.today()
        start = end - timedelta(days=30)
        revenue_data = self.report_service.get_revenue_for_period(start, end)

        self.kpi_revenue = KpiCard(
            title="Выручка",
            value=f"{revenue_data['revenue']:,.0f} ₽",
            subtitle="За 30 дней",
            subtitle_color=COLOR_SUCCESS,
            icon="💰",
        )
        layout.addWidget(self.kpi_revenue)

        self.kpi_avg = KpiCard(
            title="Средний чек",
            value=f"{revenue_data['avg_check']:,.0f} ₽",
            subtitle="По оплаченным",
            subtitle_color=COLOR_TEXT_SECONDARY,
            icon="📊",
        )
        layout.addWidget(self.kpi_avg)

        self.kpi_margin = KpiCard(
            title="Маржинальность",
            value="38%",
            subtitle="↑ +3 п.п.",
            subtitle_color=COLOR_SUCCESS,
            icon="📈",
        )
        layout.addWidget(self.kpi_margin)

        self.kpi_orders = KpiCard(
            title="Заказов оплачено",
            value=str(revenue_data["orders_count"]),
            subtitle="За 30 дней",
            subtitle_color=COLOR_TEXT_SECONDARY,
            icon="📋",
        )
        layout.addWidget(self.kpi_orders)

        layout.addStretch()
        return row

    def _create_payment_methods_block(self) -> QWidget:
        """Создаёт блок со способами оплаты.

        Returns:
            Виджет блока.
        """
        block = QFrame()
        block.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_CARD}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("Способы оплаты")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 600; border: none;"
        )
        layout.addWidget(title)

        # Метки способов оплаты
        end = date.today()
        start = end - timedelta(days=30)
        stats = self.report_service.get_payment_methods_stats(start, end)

        total = sum(stats.values()) or 1

        colors = {
            "cash": "#0EA5A4",
            "card": "#3B82F6",
            "transfer": "#F59E0B",
            "bank": "#8B5CF6",
        }

        for method in PaymentMethod.ALL:
            amount = stats.get(method, 0.0)
            percent = (amount / total) * 100 if total else 0
            label = PaymentMethod.LABELS.get(method, method)

            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)

            color_dot = QLabel("●")
            color_dot.setStyleSheet(
                f"color: {colors.get(method, COLOR_PRIMARY)}; "
                f"font-size: 16px; border: none;"
            )
            row_layout.addWidget(color_dot)

            name = QLabel(label)
            name.setFixedWidth(90)
            name.setStyleSheet(
                f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
                f"font-size: 13px; border: none;"
            )
            row_layout.addWidget(name)

            row_layout.addStretch()

            amount_label = QLabel(f"{amount:,.0f} ₽ ({percent:.0f}%)")
            amount_label.setStyleSheet(
                f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
                f"font-size: 13px; border: none;"
            )
            row_layout.addWidget(amount_label)

            layout.addWidget(row)

        layout.addStretch()
        return block

    def _create_recent_payments_block(self) -> QWidget:
        """Создаёт блок последних платежей.

        Returns:
            Виджет блока с таблицей.
        """
        block = QFrame()
        block.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_CARD}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QHBoxLayout()

        title = QLabel("Последние платежи")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 18px; font-weight: 600; border: none;"
        )
        header.addWidget(title)
        header.addStretch()

        link = QLabel("Все платежи →")
        link.setStyleSheet(
            f"color: {COLOR_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 14px; border: none;"
        )
        link.setCursor(Qt.PointingHandCursor)
        header.addWidget(link)

        layout.addLayout(header)

        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(5)
        self.payments_table.setHorizontalHeaderLabels([
            "Дата", "Клиент", "Заказ", "Способ", "Сумма",
        ])
        self.payments_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.payments_table.verticalHeader().setVisible(False)
        self.payments_table.setShowGrid(False)
        self.payments_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.payments_table.setStyleSheet(
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
                padding: 8px;
                font-size: 12px;
                text-align: left;
            }}
            """
        )
        layout.addWidget(self.payments_table)

        return block

    def _load_data(self) -> None:
        """Загружает данные для таблицы платежей."""
        payments = self.payment_repo.get_all()

        self.payments_table.setRowCount(len(payments))

        for i, payment in enumerate(payments):
            # Дата
            date_str = (
                payment.paid_at.strftime("%d.%m.%Y %H:%M")
                if payment.paid_at else "—"
            )

            # Клиент
            client_name = "—"
            if payment.order and payment.order.client:
                client_name = payment.order.client.name

            # Заказ
            order_num = (
                f"#{payment.order_id}" if payment.order_id else "—"
            )

            # Способ
            method_label = PaymentMethod.LABELS.get(
                payment.method, payment.method
            )

            # Сумма
            amount = f"{float(payment.amount):,.0f} ₽"

            self.payments_table.setItem(i, 0, QTableWidgetItem(date_str))
            self.payments_table.setItem(i, 1, QTableWidgetItem(client_name))
            self.payments_table.setItem(i, 2, QTableWidgetItem(order_num))
            self.payments_table.setItem(i, 3, QTableWidgetItem(method_label))
            self.payments_table.setItem(i, 4, QTableWidgetItem(amount))

            self.payments_table.setRowHeight(i, 44)
