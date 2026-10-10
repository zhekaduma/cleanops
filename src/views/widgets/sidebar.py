"""Виджет бокового меню (Sidebar).

Левое вертикальное меню навигации приложения CleanOps. Содержит логотип,
список разделов и активный пункт. Используется на всех экранах после
авторизации.

Соответствует макету из Figma: ширина 240px, тёмно-бирюзовый фон,
белый текст, активный пункт с белым фоном.
"""

from typing import Callable, List, Optional, Tuple

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


# Цвета (из макета Figma)
COLOR_BG = "#0F766E"          # Основной фон sidebar
COLOR_BG_HEADER = "#115E59"   # Фон шапки с логотипом
COLOR_ACTIVE_BG = "#FFFFFF"   # Фон активного пункта
COLOR_ACTIVE_TEXT = "#0F766E" # Текст активного пункта
COLOR_TEXT = "#E2E8F0"        # Обычный текст
COLOR_DIVIDER = "#115E59"     # Разделитель


class SidebarItem(QPushButton):
    """Пункт меню Sidebar.

    Кнопка с иконкой и текстом. Может быть в активном или обычном состоянии.

    Attributes:
        item_id: Идентификатор пункта (для навигации).
        icon_text: Текст-иконка (эмодзи или символ).
        label: Название пункта.
    """

    def __init__(
        self,
        item_id: str,
        icon_text: str,
        label: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализирует пункт меню.

        Args:
            item_id: Идентификатор пункта.
            icon_text: Текст-иконка.
            label: Название пункта.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.item_id = item_id
        self.icon_text = icon_text
        self.label = label

        self.setText(f"  {icon_text}   {label}")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)
        self.setStyleSheet(self._default_style())
        self._set_active(False)

    def _default_style(self) -> str:
        """Возвращает QSS стиль для пункта меню."""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT};
                border: none;
                border-radius: 8px;
                text-align: left;
                padding: 0 16px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BG_HEADER};
            }}
            QPushButton:checked {{
                background-color: {COLOR_ACTIVE_BG};
                color: {COLOR_ACTIVE_TEXT};
                font-weight: 600;
            }}
        """

    def _set_active(self, active: bool) -> None:
        """Устанавливает состояние активности.

        Args:
            active: True для активного состояния.
        """
        self.setChecked(active)


class Sidebar(QFrame):
    """Боковое меню приложения.

    Отображает логотип, список разделов и нижний блок с версией.
    При клике на пункт меню emit-ит сигнал `navigation_changed` с
    идентификатором пункта.

    Signals:
        navigation_changed: Испускается при выборе пункта меню.
            Аргумент: item_id (str).
    """

    navigation_changed = pyqtSignal(str)

    # Список пунктов меню: (item_id, icon, label)
    MENU_ITEMS: List[Tuple[str, str, str]] = [
        ("dashboard", "📊", "Дашборд"),
        ("orders", "📋", "Заказы"),
        ("calendar", "📅", "Календарь"),
        ("calculator", "🧮", "Калькулятор"),
        ("clients", "👥", "Клиенты"),
        ("references", "📚", "Справочники"),
        ("finance", "💰", "Финансы"),
        ("users", "👤", "Пользователи"),
        ("log", "📜", "Журнал"),
    ]

    def __init__(
        self,
        active_item: str = "dashboard",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализирует Sidebar.

        Args:
            active_item: ID пункта, который выделен изначально.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.active_item = active_item
        self.items: dict = {}

        self.setFixedWidth(240)
        self.setStyleSheet(f"background-color: {COLOR_BG};")

        self._build_ui()

    def _build_ui(self) -> None:
        """Собирает интерфейс Sidebar."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Шапка с логотипом
        header = self._create_header()
        layout.addWidget(header)

        # Разделитель
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {COLOR_DIVIDER};")
        layout.addWidget(divider)

        # Пункты меню
        menu_container = QWidget()
        menu_layout = QVBoxLayout(menu_container)
        menu_layout.setContentsMargins(8, 12, 8, 12)
        menu_layout.setSpacing(4)

        for item_id, icon, label in self.MENU_ITEMS:
            item = SidebarItem(item_id, icon, label)
            item.setChecked(item_id == self.active_item)
            item.clicked.connect(
                lambda checked, iid=item_id: self._on_item_clicked(iid)
            )
            self.items[item_id] = item
            menu_layout.addWidget(item)

        layout.addWidget(menu_container)
        layout.addStretch()

        # Нижний блок — версия
        version = QLabel("v0.1.0")
        version.setStyleSheet(
            "color: #A7F3D0; font-size: 12px; padding: 16px 24px;"
        )
        layout.addWidget(version)

    def _create_header(self) -> QWidget:
        """Создаёт шапку с логотипом.

        Returns:
            Виджет шапки.
        """
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet(f"background-color: {COLOR_BG_HEADER};")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)

        logo = QLabel("🧹  CleanOps")
        logo.setStyleSheet(
            "color: #FFFFFF; font-family: 'Inter'; "
            "font-size: 18px; font-weight: 700;"
        )
        layout.addWidget(logo)

        return header

    def _on_item_clicked(self, item_id: str) -> None:
        """Обрабатывает клик по пункту меню.

        Args:
            item_id: ID выбранного пункта.
        """
        self.set_active(item_id)
        self.navigation_changed.emit(item_id)

    def set_active(self, item_id: str) -> None:
        """Устанавливает активный пункт.

        Args:
            item_id: ID пункта.
        """
        for iid, item in self.items.items():
            item.setChecked(iid == item_id)
        self.active_item = item_id
