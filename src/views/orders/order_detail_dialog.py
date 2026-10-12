"""Карточка заказа с возможностью смены статуса.

Модальное окно для просмотра деталей заказа и управления им:
- изменение статуса (F-4.2);
- назначение бригады (F-4.4);
- просмотр чек-листа и позиций.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.models.order import CleaningType, OrderStatus
from src.repositories.crew_repository import CrewRepository
from src.services import OrderService
from src.views.widgets.badge import Badge


# Цвета
COLOR_PRIMARY = "#0EA5A4"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_SUCCESS = "#22C55E"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"


class OrderDetailDialog(QDialog):
    """Карточка заказа.

    Позволяет менеджеру:
    - просмотреть детали;
    - изменить статус заказа;
    - назначить бригаду;
    - просмотреть позиции и чек-лист.
    """

    def __init__(
        self,
        order_id: int,
        current_user=None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализирует карточку.

        Args:
            order_id: ID заказа.
            current_user: Текущий пользователь (для audit log).
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.order_id = order_id
        self.current_user = current_user
        self.order_service = OrderService()
        self.crew_repo = CrewRepository()

        self.order_data = self.order_service.get_order_with_items(order_id)
        if not self.order_data:
            QMessageBox.critical(self, "Ошибка", f"Заказ #{order_id} не найден")
            self.reject()
            return

        self.order = self.order_data["order"]

        self.setWindowTitle(f"Заказ #{order_id}")
        self.setModal(True)
        self.setFixedSize(800, 700)
        self.setStyleSheet("background-color: #F8FAFC;")

        self._build_ui()

    def _build_ui(self) -> None:
        """Собирает интерфейс."""
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        # Заголовок
        header = self._create_header()
        main.addWidget(header)

        # Инфо-блок
        info = self._create_info_block()
        main.addWidget(info)

        # Позиции
        items_block = self._create_items_block()
        main.addWidget(items_block)

        # Чек-лист
        checklist_block = self._create_checklist_block()
        main.addWidget(checklist_block)

        # Кнопки действий
        buttons = self._create_action_buttons()
        main.addLayout(buttons)

    def _create_header(self) -> QWidget:
        """Создаёт заголовок с номером и статусом."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # Номер заказа
        title = QLabel(f"Заказ #{self.order.order_id}")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 22px; font-weight: 700;"
        )
        layout.addWidget(title)
        layout.addSpacing(16)

        # Статус — badge
        badge = Badge(self.order.status)
        layout.addWidget(badge)

        layout.addStretch()

        # Сумма
        total = QLabel(f"{float(self.order.total_price):,.0f} ₽")
        total.setStyleSheet(
            f"color: {COLOR_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 24px; font-weight: 700;"
        )
        layout.addWidget(total)

        return header

    def _create_info_block(self) -> QWidget:
        """Создаёт блок с информацией о заказе."""
        block = QFrame()
        block.setStyleSheet(
            f"QFrame {{ background-color: white; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 8px; }}"
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Клиент
        client_name = self.order.client.name if self.order.client else "—"
        self._add_info_row(layout, "Клиент:", client_name)

        # Адрес
        address = self.order.object.address if self.order.object else "—"
        self._add_info_row(layout, "Адрес:", address)

        # Площадь
        self._add_info_row(layout, "Площадь:", f"{float(self.order.area):.0f} м²")

        # Тип уборки
        ct_label = CleaningType.LABELS.get(self.order.cleaning_type, self.order.cleaning_type)
        self._add_info_row(layout, "Тип уборки:", ct_label)

        # Дата
        date_str = "—"
        if self.order.planned_date:
            date_str = self.order.planned_date.strftime("%d.%m.%Y")
            if self.order.planned_start:
                date_str += f", {self.order.planned_start.strftime('%H:%M')}"
        self._add_info_row(layout, "Дата:", date_str)

        # Бригада
        crew_name = self.order.crew.name if self.order.crew else "не назначена"
        self._add_info_row(layout, "Бригада:", crew_name)

        # Коэффициенты
        coefs = f"срочность ×{float(self.order.urgency_coef)}, загрязнение ×{float(self.order.dirt_coef)}"
        self._add_info_row(layout, "Коэффициенты:", coefs)

        return block

    def _add_info_row(self, layout: QVBoxLayout, label: str, value: str) -> None:
        """Добавляет строку с label + значение."""
        row = QHBoxLayout()

        lbl = QLabel(label)
        lbl.setFixedWidth(120)
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; "
            f"font-size: 13px;"
        )
        row.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 500;"
        )
        row.addWidget(val)
        row.addStretch()

        layout.addLayout(row)

    def _create_items_block(self) -> QWidget:
        """Создаёт блок с позициями заказа."""
        items = self.order_data.get("items", [])

        block = QFrame()
        block.setStyleSheet(
            f"QFrame {{ background-color: white; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 8px; }}"
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title = QLabel(f"Доп. услуги ({len(items)})")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 14px; font-weight: 600;"
        )
        layout.addWidget(title)

        if not items:
            empty = QLabel("Нет дополнительных услуг")
            empty.setStyleSheet(
                f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 12px;"
            )
            layout.addWidget(empty)
        else:
            for item in items:
                row = QHBoxLayout()
                svc_name = item.service.name if item.service else "—"
                name = QLabel(f"• {svc_name}")
                name.setStyleSheet(
                    f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; font-size: 13px;"
                )
                row.addWidget(name)
                row.addStretch()

                qty = QLabel(f"{float(item.quantity):.0f} × {float(item.price):,.0f} ₽")
                qty.setStyleSheet(
                    f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 12px;"
                )
                row.addWidget(qty)
                row.addSpacing(16)

                total = QLabel(f"{float(item.sum):,.0f} ₽")
                total.setStyleSheet(
                    f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
                    f"font-size: 13px; font-weight: 600;"
                )
                row.addWidget(total)

                layout.addLayout(row)

        return block

    def _create_checklist_block(self) -> QWidget:
        """Создаёт блок с чек-листом."""
        tasks = self.order_data.get("tasks", [])
        progress = self.order_data.get("progress", {"done": 0, "total": 0})

        block = QFrame()
        block.setStyleSheet(
            f"QFrame {{ background-color: white; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 8px; }}"
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title = QLabel(
            f"Чек-лист ({progress['done']}/{progress['total']})"
        )
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Inter'; "
            f"font-size: 14px; font-weight: 600;"
        )
        layout.addWidget(title)

        if not tasks:
            empty = QLabel("Чек-лист пуст")
            empty.setStyleSheet(
                f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Inter'; font-size: 12px;"
            )
            layout.addWidget(empty)
        else:
            for task in tasks:
                check = "☑" if task.is_done else "☐"
                color = COLOR_SUCCESS if task.is_done else COLOR_TEXT_SECONDARY
                item = QLabel(f"{check} {task.description}")
                item.setStyleSheet(
                    f"color: {color}; font-family: 'Inter'; font-size: 13px;"
                )
                layout.addWidget(item)

        return block

    def _create_action_buttons(self) -> QHBoxLayout:
        """Создаёт кнопки действий (зависят от текущего статуса)."""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        status = self.order.status

        # Кнопки по статусу
        if status in (OrderStatus.NEW, OrderStatus.CALCULATED):
            confirm_btn = self._action_button("Подтвердить", COLOR_PRIMARY)
            confirm_btn.clicked.connect(lambda: self._change_status(OrderStatus.CONFIRMED))
            layout.addWidget(confirm_btn)

        if status == OrderStatus.CONFIRMED:
            # Выбор бригады + кнопка назначения
            self.crew_combo = QComboBox()
            self.crew_combo.setFixedHeight(38)
            self.crew_combo.setStyleSheet(
                f"""
                QComboBox {{
                    background-color: white;
                    border: 1px solid {COLOR_BORDER};
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-family: 'Inter';
                    font-size: 13px;
                }}
                """
            )
            crews = self.crew_repo.get_active()
            for c in crews:
                self.crew_combo.addItem(c.name, c.crew_id)
            layout.addWidget(self.crew_combo)

            assign_btn = self._action_button("Назначить", COLOR_PRIMARY)
            assign_btn.clicked.connect(self._on_assign_crew)
            layout.addWidget(assign_btn)

        if status == OrderStatus.ASSIGNED:
            start_btn = self._action_button("Начать работу", COLOR_WARNING)
            start_btn.clicked.connect(lambda: self._change_status(OrderStatus.IN_PROGRESS))
            layout.addWidget(start_btn)

        if status == OrderStatus.IN_PROGRESS:
            done_btn = self._action_button("Завершить", COLOR_SUCCESS)
            done_btn.clicked.connect(lambda: self._change_status(OrderStatus.COMPLETED))
            layout.addWidget(done_btn)

        if status == OrderStatus.COMPLETED:
            pay_btn = self._action_button("Оплачен", COLOR_SUCCESS)
            pay_btn.clicked.connect(lambda: self._change_status(OrderStatus.PAID))
            layout.addWidget(pay_btn)

        layout.addStretch()

        # Кнопка отмены (если не Оплачен)
        if status != OrderStatus.PAID:
            cancel_btn = self._action_button("Отменить", COLOR_DANGER, outline=True)
            cancel_btn.clicked.connect(self._on_cancel)
            layout.addWidget(cancel_btn)

        # Закрыть
        close_btn = self._action_button("Закрыть", COLOR_TEXT_SECONDARY, outline=True)
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

        return layout

    def _action_button(self, text: str, color: str, outline: bool = False) -> QPushButton:
        """Создаёт кнопку действия."""
        btn = QPushButton(text)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.PointingHandCursor)

        if outline:
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: transparent;
                    color: {color};
                    border: 1px solid {COLOR_BORDER};
                    border-radius: 6px;
                    padding: 0 16px;
                    font-family: 'Inter';
                    font-size: 13px;
                }}
                QPushButton:hover {{ background-color: #F1F5F9; }}
                """
            )
        else:
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 0 16px;
                    font-family: 'Inter';
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{ background-color: #0F766E; }}
                """
            )
        return btn

    def _change_status(self, new_status: str) -> None:
        """Меняет статус заказа."""
        try:
            self.order_service.update_status(self.order_id, new_status)
            label = OrderStatus.LABELS.get(new_status, new_status)
            print(f"[OrderDetailDialog] Статус заказа #{self.order_id}: {label}")
            QMessageBox.information(
                self, "Готово", f"Статус изменён: {label}"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус:\n{e}")

    def _on_assign_crew(self) -> None:
        """Назначает бригаду."""
        try:
            crew_id = self.crew_combo.currentData()
            manager_id = self.current_user.user_id if self.current_user else None
            self.order_service.assign_crew(self.order_id, crew_id, manager_id)
            print(f"[OrderDetailDialog] Бригада {crew_id} назначена на заказ #{self.order_id}")
            QMessageBox.information(self, "Готово", "Бригада назначена")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось назначить бригаду:\n{e}")

    def _on_cancel(self) -> None:
        """Отменяет заказ."""
        reply = QMessageBox.question(
            self, "Отмена заказа",
            "Вы уверены, что хотите отменить заказ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.order_service.cancel_order(self.order_id, "Отменён менеджером")
                QMessageBox.information(self, "Готово", "Заказ отменён")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось отменить:\n{e}")
