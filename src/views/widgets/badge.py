"""Виджет цветного бейджа (Badge).

Отображает статус или метку в виде цветного «pill»-элемента.
Используется для статусов заказов, ролей и т.д.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget


# Цвета статусов заказов (из Figma)
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

# Русские названия статусов
STATUS_LABELS = {
    "new": "Новый",
    "calculated": "Рассчитан",
    "confirmed": "Подтверждён",
    "assigned": "Назначен",
    "in_progress": "В работе",
    "completed": "Завершён",
    "paid": "Оплачен",
    "cancelled": "Отменён",
}


class Badge(QLabel):
    """Цветной бейдж для статусов.

    Attributes:
        status: Ключ статуса (new, in_progress, completed...).
    """

    def __init__(
        self,
        status: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализирует бейдж.

        Args:
            status: Ключ статуса.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.status = status

        label = STATUS_LABELS.get(status, status)
        bg, fg = STATUS_COLORS.get(status, ("#E2E8F0", "#64748B"))

        self.setText(label)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(90, 24)
        self.setStyleSheet(
            f"""
            background-color: {bg};
            color: {fg};
            border-radius: 12px;
            font-family: 'Inter';
            font-size: 12px;
            font-weight: 500;
            padding: 0 8px;
            """
        )
