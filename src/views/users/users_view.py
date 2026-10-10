"""Экран управления пользователями.

Реализует F-7.1: таблица пользователей с ролями и статусами.
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

from src.models.user import UserRole
from src.repositories.user_repository import UserRepository


COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"


# Цвета ролей
ROLE_COLORS = {
    "admin": ("#FEE2E2", "#B91C1C"),
    "manager": ("#DBEAFE", "#1D4ED8"),
    "brigadier": ("#EDE9FE", "#7C3AED"),
    "cleaner": ("#CCFBF1", "#0F766E"),
    "accountant": ("#FEF3C7", "#D97706"),
    "observer": ("#E2E8F0", "#64748B"),
}


class UsersView(QWidget):
    """Экран пользователей."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует экран."""
        super().__init__(parent)
        self.user_repo = UserRepository()

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._load_users()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(20)

        # Заголовок
        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Пользователи")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        title_box.addWidget(title)

        self.subtitle = QLabel("Всего: 0 пользователей")
        self.subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 14px;"
        )
        title_box.addWidget(self.subtitle)

        header.addLayout(title_box)
        header.addStretch()

        new_btn = QPushButton("+  Новый пользователь")
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setFixedSize(200, 44)
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
        filters = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Поиск по ФИО или логину")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self._load_users)
        filters.addWidget(self.search_input, 2)

        self.role_filter = QComboBox()
        self.role_filter.addItem("Все роли", None)
        for role_key in UserRole.ALL:
            self.role_filter.addItem(
                UserRole.LABELS.get(role_key, role_key), role_key
            )
        self.role_filter.setFixedHeight(40)
        self.role_filter.setStyleSheet(self._input_style())
        self.role_filter.currentIndexChanged.connect(self._load_users)
        filters.addWidget(self.role_filter)

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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ФИО", "Логин", "Email", "Роль", "Статус", "Последний вход",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
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
            QTableWidget::item:selected {{
                background-color: #F0FDFA;
                color: {COLOR_TEXT_PRIMARY};
            }}
        """

    def _load_users(self) -> None:
        """Загружает список пользователей."""
        query = self.search_input.text().lower()
        role_filter = self.role_filter.currentData()

        users = self.user_repo.get_all()
        if role_filter:
            users = [u for u in users if u.role == role_filter]
        if query:
            users = [
                u for u in users
                if query in u.full_name.lower()
                or query in u.username.lower()
            ]

        self.subtitle.setText(f"Всего: {len(users)} пользователей")
        self.table.setRowCount(len(users))

        for i, user in enumerate(users):
            role_label = UserRole.LABELS.get(user.role, user.role)
            bg, fg = ROLE_COLORS.get(user.role, ("#E2E8F0", "#64748B"))

            self.table.setItem(i, 0, QTableWidgetItem(user.full_name))
            self.table.setItem(i, 1, QTableWidgetItem(user.username))
            self.table.setItem(i, 2, QTableWidgetItem(user.email or "—"))

            # Роль — badge
            role_badge = QLabel(role_label)
            role_badge.setAlignment(Qt.AlignCenter)
            role_badge.setFixedSize(110, 24)
            role_badge.setStyleSheet(
                f"background-color: {bg}; color: {fg}; "
                f"border-radius: 12px; font-size: 12px; font-weight: 500;"
            )
            cell = QWidget()
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(8, 0, 0, 0)
            cell_layout.addWidget(role_badge)
            cell_layout.addStretch()
            self.table.setCellWidget(i, 3, cell)

            # Статус
            status = "Активен" if user.is_active else "Заблокирован"
            status_color = "#047857" if user.is_active else "#B91C1C"
            status_bg = "#D1FAE5" if user.is_active else "#FEE2E2"

            status_badge = QLabel(status)
            status_badge.setAlignment(Qt.AlignCenter)
            status_badge.setFixedSize(110, 24)
            status_badge.setStyleSheet(
                f"background-color: {status_bg}; color: {status_color}; "
                f"border-radius: 12px; font-size: 12px; font-weight: 500;"
            )
            cell2 = QWidget()
            cell2_layout = QHBoxLayout(cell2)
            cell2_layout.setContentsMargins(8, 0, 0, 0)
            cell2_layout.addWidget(status_badge)
            cell2_layout.addStretch()
            self.table.setCellWidget(i, 4, cell2)

            # Последний вход
            last_login = (
                user.last_login.strftime("%d.%m.%Y %H:%M")
                if user.last_login else "—"
            )
            self.table.setItem(i, 5, QTableWidgetItem(last_login))

            self.table.setRowHeight(i, 52)
