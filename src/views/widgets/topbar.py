"""Виджет верхней панели (Topbar).

Отображается на всех экранах после авторизации. Содержит заголовок
страницы, уведомления и профиль пользователя.

Соответствует макету из Figma: высота 56px, белый фон, нижняя граница.
"""

from typing import Optional

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
COLOR_BG = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_PRIMARY = "#0EA5A4"


class Topbar(QFrame):
    """Верхняя панель приложения.

    Отображает заголовок страницы, уведомления и профиль пользователя.
    Emit-ит сигнал `logout_requested` при нажатии кнопки «Выйти».

    Signals:
        logout_requested: Испускается при клике на «Выйти».
    """

    logout_requested = pyqtSignal()

    def __init__(
        self,
        title: str = "Дашборд",
        user_name: str = "Пользователь",
        user_role: str = "Менеджер",
        notifications_count: int = 0,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализирует Topbar.

        Args:
            title: Заголовок страницы.
            user_name: Имя пользователя.
            user_role: Роль пользователя.
            notifications_count: Количество непрочитанных уведомлений.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.title_text = title
        self.user_name = user_name
        self.user_role = user_role
        self.notifications_count = notifications_count

        self.setFixedHeight(56)
        self.setStyleSheet(
            f"Topbar {{ background-color: {COLOR_BG}; "
            f"border-bottom: 1px solid {COLOR_BORDER}; }}"
        )

        self._build_ui()

    def _build_ui(self) -> None:
        """Собирает интерфейс Topbar."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        # Заголовок страницы (слева)
        self.title_label = QLabel(self.title_text)
        self.title_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 16px; font-weight: 600;"
        )
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Уведомления
        notif_btn = self._create_notification_button()
        layout.addWidget(notif_btn)

        # Профиль
        profile = self._create_profile_widget()
        layout.addWidget(profile)

        # Кнопка «Выйти»
        logout_btn = QPushButton("Выйти")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setFixedSize(80, 32)
        logout_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                font-family: 'Inter';
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
                color: {COLOR_TEXT_PRIMARY};
            }}
            """
        )
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

    def _create_notification_button(self) -> QPushButton:
        """Создаёт кнопку уведомлений с бейджем.

        Returns:
            Кнопка уведомлений.
        """
        btn = QPushButton("🔔")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(80, 36)

        if self.notifications_count > 0:
            btn.setText(f"🔔 {self.notifications_count}")

        btn.setStyleSheet(
            """
            QPushButton {
                background-color: #F1F5F9;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
            """
        )
        return btn

    def _create_profile_widget(self) -> QWidget:
        """Создаёт блок с аватаром и именем пользователя.

        Returns:
            Виджет профиля.
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Аватар (инициалы)
        avatar = QLabel(self._get_initials())
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            f"""
            background-color: {COLOR_PRIMARY};
            color: white;
            border-radius: 18px;
            font-family: 'Inter';
            font-size: 13px;
            font-weight: 600;
            """
        )
        layout.addWidget(avatar)

        # Имя + роль
        info = QWidget()
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(0)

        name_label = QLabel(self.user_name)
        name_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 14px; font-weight: 500;"
        )
        info_layout.addWidget(name_label)

        role_label = QLabel(self.user_role)
        role_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 12px;"
        )
        info_layout.addWidget(role_label)

        layout.addWidget(info)
        return widget

    def _get_initials(self) -> str:
        """Возвращает инициалы пользователя.

        Returns:
            Строка из 1-2 букв.
        """
        parts = self.user_name.split()
        if len(parts) >= 2:
            return (parts[0][:1] + parts[1][:1]).upper()
        return self.user_name[:2].upper()

    def set_title(self, title: str) -> None:
        """Обновляет заголовок страницы.

        Args:
            title: Новый заголовок.
        """
        self.title_text = title
        self.title_label.setText(title)
