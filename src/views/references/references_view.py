"""Экран справочников.

Реализует F-2.1, F-2.3, F-2.4, F-2.5, F-2.6 — управление справочниками
через левое меню категорий. Справа — таблица выбранной категории.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.repositories.client_repository import ObjectRepository
from src.repositories.crew_repository import CrewRepository
from src.repositories.service_repository import ServiceRepository
from src.repositories.user_repository import UserRepository


COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"


class ReferencesView(QWidget):
    """Экран справочников."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует экран."""
        super().__init__(parent)

        # Репозитории
        self.object_repo = ObjectRepository()
        self.service_repo = ServiceRepository()
        self.user_repo = UserRepository()
        self.crew_repo = CrewRepository()

        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()
        self._switch_category("objects")

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setSpacing(20)

        # Заголовок
        title = QLabel("Справочники")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        main.addWidget(title)

        subtitle = QLabel("Управление мастер-данными системы")
        subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 14px;"
        )
        main.addWidget(subtitle)

        # Двухколоночный layout
        content = QHBoxLayout()
        content.setSpacing(24)

        # Левая навигация
        nav = self._create_nav()
        # Левая колонка: кнопка + навигация
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # Универсальная кнопка добавления
        self.add_btn = QPushButton("+  Добавить")
        self.add_btn.setFixedHeight(40)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet(
            f'''
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
            '''
        )
        self.add_btn.clicked.connect(self._on_add)
        left_layout.addWidget(self.add_btn)
        left_layout.addWidget(nav)

        content.addWidget(left_col)

        # Правая область — QStackedWidget с таблицами
        self.stack = QStackedWidget()

        self.objects_table = self._create_objects_table()
        self.stack.addWidget(self.objects_table)

        self.services_table = self._create_services_table()
        self.stack.addWidget(self.services_table)

        self.users_table = self._create_users_table()
        self.stack.addWidget(self.users_table)

        self.crews_table = self._create_crews_table()
        self.stack.addWidget(self.crews_table)

        content.addWidget(self.stack, 1)

        main.addLayout(content, 1)

    def _create_nav(self) -> QWidget:
        """Создаёт левую навигацию.

        Returns:
            Виджет меню.
        """
        nav = QFrame()
        nav.setFixedWidth(200)
        nav.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_CARD}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        layout = QVBoxLayout(nav)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.nav_buttons = {}

        items = [
            ("objects", "📦  Объекты"),
            ("services", "🛠  Услуги"),
            ("users", "👤  Сотрудники"),
            ("crews", "👥  Бригады"),
        ]

        for item_id, label in items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setStyleSheet(self._nav_button_style())
            btn.clicked.connect(
                lambda checked, iid=item_id: self._switch_category(iid)
            )
            self.nav_buttons[item_id] = btn
            layout.addWidget(btn)

        layout.addStretch()
        return nav

    def _nav_button_style(self) -> str:
        """QSS для кнопок меню."""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 0 16px;
                font-family: 'Inter';
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
            }}
            QPushButton:checked {{
                background-color: #CCFBF1;
                color: {COLOR_PRIMARY};
                font-weight: 600;
            }}
        """

    def _create_table_widget(self, headers: list) -> QTableWidget:
        """Создаёт стандартную таблицу.

        Args:
            headers: Список заголовков колонок.

        Returns:
            Настроенная таблица.
        """
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {COLOR_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
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
            """
        )
        return table

    def _create_objects_table(self) -> QTableWidget:
        """Таблица объектов."""
        table = self._create_table_widget([
            "Адрес", "Клиент", "Площадь", "Тип", "Заметки",
        ])
        objects = self.object_repo.get_all()
        table.setRowCount(len(objects))

        for i, obj in enumerate(objects):
            client = obj.client.name if obj.client else "—"
            table.setItem(i, 0, QTableWidgetItem(obj.address))
            table.setItem(i, 1, QTableWidgetItem(client))
            table.setItem(i, 2, QTableWidgetItem(f"{float(obj.area):.0f} м²"))
            table.setItem(i, 3, QTableWidgetItem(obj.object_type))
            table.setItem(i, 4, QTableWidgetItem(obj.access_notes or "—"))
            table.setRowHeight(i, 48)
        return table

    def _create_services_table(self) -> QTableWidget:
        """Таблица услуг."""
        table = self._create_table_widget([
            "Название", "Единица", "Цена", "Нормо-часы", "Активна",
        ])
        services = self.service_repo.get_all()
        table.setRowCount(len(services))

        for i, svc in enumerate(services):
            active = "✅" if svc.is_active else "❌"
            table.setItem(i, 0, QTableWidgetItem(svc.name))
            table.setItem(i, 1, QTableWidgetItem(svc.unit))
            table.setItem(i, 2, QTableWidgetItem(f"{float(svc.price):,.0f} ₽"))
            table.setItem(i, 3, QTableWidgetItem(f"{float(svc.norm_hours):.1f} ч"))
            table.setItem(i, 4, QTableWidgetItem(active))
            table.setRowHeight(i, 48)
        return table

    def _create_users_table(self) -> QTableWidget:
        """Таблица сотрудников."""
        table = self._create_table_widget([
            "ФИО", "Логин", "Роль", "Email", "Телефон",
        ])
        users = self.user_repo.get_all()
        table.setRowCount(len(users))

        for i, u in enumerate(users):
            table.setItem(i, 0, QTableWidgetItem(u.full_name))
            table.setItem(i, 1, QTableWidgetItem(u.username))
            table.setItem(i, 2, QTableWidgetItem(u.role))
            table.setItem(i, 3, QTableWidgetItem(u.email or "—"))
            table.setItem(i, 4, QTableWidgetItem(u.phone or "—"))
            table.setRowHeight(i, 48)
        return table

    def _create_crews_table(self) -> QTableWidget:
        """Таблица бригад."""
        table = self._create_table_widget([
            "Название", "Зона", "Транспорт", "Активна",
        ])
        crews = self.crew_repo.get_all()
        table.setRowCount(len(crews))

        for i, c in enumerate(crews):
            active = "✅" if c.is_active else "❌"
            table.setItem(i, 0, QTableWidgetItem(c.name))
            table.setItem(i, 1, QTableWidgetItem(c.zone or "—"))
            table.setItem(i, 2, QTableWidgetItem(c.transport or "—"))
            table.setItem(i, 3, QTableWidgetItem(active))
            table.setRowHeight(i, 48)
        return table

    def _on_add(self) -> None:
        """Обработка кнопки + Добавить."""
        active = getattr(self, "active_category", "crews")
        if active == "crews":
            self._on_new_crew()
        else:
            print(f"[ReferencesView] Создание '{active}' в разработке")

    def _on_new_crew(self) -> None:
        """Открывает диалог создания бригады."""
        from src.views.references.crew_form_dialog import CrewFormDialog

        dialog = CrewFormDialog(parent=self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            self.crew_repo.create(**data)
            print(f"[ReferencesView] Создана бригада: {data['name']}")

            # Пересоздаём таблицу бригад
            old = self.stack.widget(3)
            if old:
                self.stack.removeWidget(old)
                old.deleteLater()
            self.crews_table = self._create_crews_table()
            self.stack.insertWidget(3, self.crews_table)
            self.stack.setCurrentIndex(3)

    def _switch_category(self, item_id: str) -> None:
        """Переключает категорию.

        Args:
            item_id: ID категории.
        """
        index_map = {
            "objects": 0,
            "services": 1,
            "users": 2,
            "crews": 3,
        }

        self.active_category = item_id

        if item_id in index_map:
            self.stack.setCurrentIndex(index_map[item_id])

        for iid, btn in self.nav_buttons.items():
            btn.setChecked(iid == item_id)
