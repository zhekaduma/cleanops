"""Сервис управления заказами.

Модуль реализует бизнес-логику работы с заказами (см. ТЗ, F-4):
- создание заказа с позициями и чек-листом;
- изменение статуса;
- назначение бригады;
- завершение и отмена.
"""

from datetime import datetime
from typing import List, Optional

from src.models.checklist import ChecklistTask
from src.models.order import Order, OrderItem, OrderStatus
from src.repositories.checklist_repository import ChecklistTaskRepository
from src.repositories.order_repository import (
    OrderItemRepository,
    OrderRepository,
)
from src.services.auth_service import AuthService
from src.services.dtos import OrderCreateDTO
from src.services.dtos import OrderItemDTO


class OrderService:
    """Сервис управления заказами.

    Создаёт заказы, управляет их статусами, назначает бригады,
    автоматически генерирует чек-листы.
    """

    # Шаблоны чек-листов по типу уборки
    CHECKLIST_TEMPLATES = {
        "maintenance": [
            "Пропылесосить все комнаты",
            "Протереть пыль",
            "Вымыть полы",
            "Убрать мусор",
        ],
        "general": [
            "Пропылесосить все комнаты",
            "Протереть пыль со всех поверхностей",
            "Вымыть полы",
            "Вымыть сантехнику",
            "Вымыть кухню",
            "Убрать мусор",
        ],
        "post_renovation": [
            "Убрать строительный мусор",
            "Пропылесосить все комнаты",
            "Вымыть полы (2 раза)",
            "Вымыть окна",
            "Вымыть стены",
            "Вымыть сантехнику",
        ],
        "windows": [
            "Вымыть окна с внутренней стороны",
            "Вымыть окна с наружной стороны",
            "Протереть подоконники",
            "Вымыть рамы",
        ],
    }

    def __init__(self) -> None:
        """Инициализирует сервис с репозиториями."""
        self.order_repo = OrderRepository()
        self.item_repo = OrderItemRepository()
        self.checklist_repo = ChecklistTaskRepository()
        self.auth_service = AuthService()

    def create_order(self, dto: OrderCreateDTO) -> Order:
        """Создаёт новый заказ с позициями и чек-листом.

        Args:
            dto: Данные для создания заказа.

        Returns:
            Созданный заказ.
        """
        # 1. Создаём заказ
        order = self.order_repo.create(
            client_id=dto.client_id,
            object_id=dto.object_id,
            manager_id=dto.manager_id,
            cleaning_type=dto.cleaning_type,
            area=dto.area,
            urgency_coef=dto.urgency_coef,
            dirt_coef=dto.dirt_coef,
            discount=dto.discount,
            total_price=dto.total_price,
            status=OrderStatus.NEW,
            planned_date=dto.planned_date,
            planned_start=dto.planned_start,
            planned_end=dto.planned_end,
            notes=dto.notes,
        )

        # 2. Добавляем позиции заказа
        for item_dto in dto.items:
            self.item_repo.create(
                order_id=order.order_id,
                service_id=item_dto.service_id,
                quantity=item_dto.quantity,
                price=item_dto.price,
                sum=item_dto.quantity * item_dto.price,
            )

        # 3. Генерируем чек-лист по типу уборки
        self._generate_checklist(order.order_id, dto.cleaning_type)

        # 4. Логируем создание
        self.auth_service.log_action(
            user_id=dto.manager_id,
            action="create",
            entity="Order",
            entity_id=order.order_id,
            details=f'{{"client_id": {dto.client_id}, "total": {dto.total_price}}}',
        )

        return order

    def _generate_checklist(
        self,
        order_id: int,
        cleaning_type: str,
    ) -> List[ChecklistTask]:
        """Генерирует чек-лист по типу уборки.

        Args:
            order_id: ID заказа.
            cleaning_type: Тип уборки.

        Returns:
            Список созданных задач.
        """
        template = self.CHECKLIST_TEMPLATES.get(
            cleaning_type,
            self.CHECKLIST_TEMPLATES["maintenance"],
        )
        tasks = []
        for description in template:
            task = self.checklist_repo.create(
                order_id=order_id,
                template_type=cleaning_type,
                description=description,
                is_required=True,
                is_done=False,
            )
            tasks.append(task)
        return tasks

    def update_status(self, order_id: int, new_status: str) -> Optional[Order]:
        """Обновляет статус заказа.

        Args:
            order_id: ID заказа.
            new_status: Новый статус (см. OrderStatus).

        Returns:
            Обновлённый заказ или None.
        """
        order = self.order_repo.update(order_id, status=new_status)

        if order:
            self.auth_service.log_action(
                user_id=order.manager_id,
                action="update",
                entity="Order",
                entity_id=order_id,
                details=f'{{"status": "{new_status}"}}',
            )
        return order

    def assign_crew(
        self,
        order_id: int,
        crew_id: int,
        manager_id: Optional[int] = None,
    ) -> Optional[Order]:
        """Назначает бригаду на заказ.

        Args:
            order_id: ID заказа.
            crew_id: ID бригады.
            manager_id: ID менеджера (для audit log).

        Returns:
            Обновлённый заказ или None.
        """
        order = self.order_repo.update(
            order_id,
            crew_id=crew_id,
            status=OrderStatus.ASSIGNED,
        )

        if order:
            self.auth_service.log_action(
                user_id=manager_id or order.manager_id,
                action="update",
                entity="Order",
                entity_id=order_id,
                details=f'{{"crew_id": {crew_id}, "status": "assigned"}}',
            )
        return order

    def start_order(self, order_id: int) -> Optional[Order]:
        """Помечает заказ как «в работе».

        Args:
            order_id: ID заказа.

        Returns:
            Обновлённый заказ.
        """
        return self.order_repo.update(
            order_id,
            status=OrderStatus.IN_PROGRESS,
            actual_start=datetime.now(),
        )

    def complete_order(self, order_id: int) -> Optional[Order]:
        """Помечает заказ как завершённый.

        Args:
            order_id: ID заказа.

        Returns:
            Обновлённый заказ.
        """
        return self.order_repo.update(
            order_id,
            status=OrderStatus.COMPLETED,
            actual_end=datetime.now(),
        )

    def cancel_order(self, order_id: int, reason: str = "") -> Optional[Order]:
        """Отменяет заказ.

        Args:
            order_id: ID заказа.
            reason: Причина отмены.

        Returns:
            Обновлённый заказ.
        """
        order = self.order_repo.update(
            order_id,
            status=OrderStatus.CANCELLED,
            notes=reason,
        )
        if order:
            self.auth_service.log_action(
                user_id=order.manager_id,
                action="update",
                entity="Order",
                entity_id=order_id,
                details=f'{{"status": "cancelled", "reason": "{reason}"}}',
            )
        return order

    def mark_paid(self, order_id: int) -> Optional[Order]:
        """Помечает заказ как оплаченный.

        Args:
            order_id: ID заказа.

        Returns:
            Обновлённый заказ.
        """
        return self.order_repo.update(order_id, status=OrderStatus.PAID)

    def get_order_with_items(self, order_id: int) -> dict:
        """Возвращает заказ вместе с позициями и чек-листом.

        Args:
            order_id: ID заказа.

        Returns:
            Словарь с заказом, позициями, чек-листом.
        """
        order = self.order_repo.get_by_id(order_id)
        if order is None:
            return {}

        items = self.item_repo.get_by_order(order_id)
        tasks = self.checklist_repo.get_by_order(order_id)
        progress = self.checklist_repo.get_progress(order_id)

        return {
            "order": order,
            "items": items,
            "tasks": tasks,
            "progress": {"done": progress[0], "total": progress[1]},
        }
