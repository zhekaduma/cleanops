"""Главное окно приложения CleanOps.

Объединяет Sidebar, Topbar и область контента. Управляет навигацией
между экранами через QStackedWidget.

Архитектура:
    - Sidebar (слева) — навигация между разделами
    - Topbar (сверху) — заголовок, уведомления, профиль
    - Content (центр) — QStackedWidget с экранами
"""

from typing import Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.views.widgets.sidebar import Sidebar
from src.views.widgets.topbar import Topbar


# Цвета
COLOR_BG = "#F8FAFC"


class PlaceholderView(QWidget):
    """Заглушка для экранов, которые ещё не реализованы.

    Показывает название раздела и сообщение «в разработке».
    """

    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        """Инициализирует заглушку.

        Args:
            title: Название экрана.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: #0F172A; font-family: 'Inter'; "
            "font-size: 24px; font-weight: 700;"
        )
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        subtitle = QLabel("Раздел в разработке")
        subtitle.setStyleSheet(
            "color: #64748B; font-family: 'Inter'; font-size: 14px;"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)


class MainWindow(QMainWindow):
    """Главное окно приложения.

    Содержит Sidebar, Topbar и QStackedWidget с экранами.
    При клике на пункт меню переключает соответствующий экран.

    Attributes:
        sidebar: Левое меню.
        topbar: Верхняя панель.
        content: Область контента (QStackedWidget).
        views: Словарь {item_id: индекс в content}.
    """

    # Соответствие ID → заголовок Topbar
    TITLES: Dict[str, str] = {
        "dashboard": "Дашборд",
        "orders": "Заказы",
        "calendar": "Календарь",
        "calculator": "Калькулятор",
        "clients": "Клиенты",
        "references": "Справочники",
        "finance": "Финансы",
        "users": "Пользователи",
        "log": "Журнал",
    }

    def __init__(
        self,
        user_name: str = "Иванов Иван",
        user_role: str = "Менеджер",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализирует главное окно.

        Args:
            user_name: Имя пользователя.
            user_role: Роль пользователя.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.user_name = user_name
        self.user_role = user_role
        self.views: Dict[str, int] = {}

        self.setWindowTitle("CleanOps — Управление клининговой службой")
        self.setGeometry(100, 100, 1440, 900)
        self.setStyleSheet(f"background-color: {COLOR_BG};")

        self._build_ui()

    def _build_ui(self) -> None:
        """Собирает интерфейс главного окна."""
        central = QWidget()
        self.setCentralWidget(central)

        # Главный layout — вертикальный (topbar сверху, ниже — контент)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Нижний layout — горизонтальный (sidebar + content)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(active_item="dashboard")
        self.sidebar.navigation_changed.connect(self._on_navigation)
        bottom_layout.addWidget(self.sidebar)

        # Content (QStackedWidget)
        self.content = QStackedWidget()
        self.content.setStyleSheet(f"background-color: {COLOR_BG};")
        self._populate_content()
        bottom_layout.addWidget(self.content, 1)

        # Topbar (сверху, над всем)
        self.topbar = Topbar(
            title="Дашборд",
            user_name=self.user_name,
            user_role=self.user_role,
            notifications_count=0,
        )
        self.topbar.logout_requested.connect(self._on_logout)

        main_layout.addWidget(self.topbar)
        main_layout.addLayout(bottom_layout)

    def _populate_content(self) -> None:
        """Заполняет QStackedWidget экранами (пока заглушками)."""
        for item_id, title in self.TITLES.items():
            view = PlaceholderView(title)
            index = self.content.addWidget(view)
            self.views[item_id] = index

    def _on_navigation(self, item_id: str) -> None:
        """Обрабатывает переключение раздела.

        Args:
            item_id: ID выбранного пункта меню.
        """
        if item_id in self.views:
            self.content.setCurrentIndex(self.views[item_id])

        # Обновляем заголовок Topbar
        title = self.TITLES.get(item_id, "")
        self.topbar.set_title(title)

    def _on_logout(self) -> None:
        """Обрабатывает выход из системы."""
        print("Logout requested")
        # В будущем — закрыть окно и показать LoginWindow
        self.close()

    def register_view(self, item_id: str, widget: QWidget) -> None:
        """Регистрирует реальный экран вместо заглушки.

        Вызывается после создания полноценных экранов
        (Дашборд, Калькулятор и т.д.).

        Args:
            item_id: ID раздела.
            widget: Виджет экрана.
        """
        if item_id not in self.views:
            return

        # Удаляем старую заглушку и добавляем новый виджет
        old_index = self.views[item_id]
        old_widget = self.content.widget(old_index)
        self.content.removeWidget(old_widget)
        old_widget.deleteLater()

        # Вставляем новый виджет на то же место
        new_index = self.content.insertWidget(old_index, widget)
        self.views[item_id] = new_index
