"""Виджет KPI-карточки.

Отображает ключевую метрику: иконку, подпись, значение и дополнительную
строку (например, динамику). Используется на дашборде.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


# Цвета
COLOR_BG = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_SUCCESS = "#22C55E"
COLOR_ERROR = "#EF4444"


class KpiCard(QFrame):
    """KPI-карточка с метрикой.

    Attributes:
        title: Подпись (например, «Заказов сегодня»).
        value: Основное значение (например, «12»).
        subtitle: Дополнительная строка (например, «+2 к вчера»).
        subtitle_color: Цвет подзаголовка (зелёный/красный/серый).
        icon: Эмодзи-иконка.
    """

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str = "",
        subtitle_color: str = COLOR_TEXT_SECONDARY,
        icon: str = "📊",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализирует KPI-карточку.

        Args:
            title: Подпись.
            value: Основное значение.
            subtitle: Дополнительная строка.
            subtitle_color: Цвет дополнительной строки.
            icon: Эмодзи-иконка.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.setFixedSize(266, 120)
        self.setStyleSheet(
            f"""
            KpiCard {{
                background-color: {COLOR_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            """
        )

        self._build_ui(title, value, subtitle, subtitle_color, icon)

    def _build_ui(
        self,
        title: str,
        value: str,
        subtitle: str,
        subtitle_color: str,
        icon: str,
    ) -> None:
        """Собирает интерфейс карточки."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)

        # Верхняя строка: подпись + иконка
        top = QLabel(f"{title}    {icon}")
        top.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 13px; border: none;"
        )
        layout.addWidget(top)

        # Значение
        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 26px; font-weight: 700; border: none;"
        )
        layout.addWidget(value_label)

        # Дополнительная строка
        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(
                f"color: {subtitle_color}; font-family: 'Inter'; "
                f"font-size: 12px; border: none;"
            )
            layout.addWidget(sub)

        layout.addStretch()
