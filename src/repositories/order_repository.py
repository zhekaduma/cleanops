"""Репозитории заказов и позиций заказов.

Модуль содержит два репозитория:
- OrderRepository — CRUD для заказов + фильтры по статусу, дате, клиенту, бригаде.
- OrderItemRepository — CRUD для позиций заказа.
"""

from datetime import date, datetime
from typing import List, Optional

from src.models.order import Order, OrderItem, OrderStatus
from src.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Репозиторий для работы с заказами.

    Расширяет BaseRepository специфичными методами:
    - фильтрация по статусу, дате, клиенту, бригаде, менеджеру;
    - получение активных заказов;
    - выборка заказов на сегодня / на период.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели Order."""
        super().__init__(Order)

    def get_by_status(self, status: str) -> List[Order]:
        """Возвращает заказы с указанным статусом.

        Args:
            status: Статус (см. OrderStatus).

        Returns:
            Список заказов.
        """
        return (
            self.session.query(Order)
            .filter_by(status=status)
            .order_by(Order.planned_date.desc())
            .all()
        )

    def get_by_client(self, client_id: int) -> List[Order]:
        """Возвращает заказы указанного клиента.

        Args:
            client_id: ID клиента.

        Returns:
            Список заказов.
        """
        return (
            self.session.query(Order)
            .filter_by(client_id=client_id)
            .order_by(Order.planned_date.desc())
            .all()
        )

    def get_by_crew(self, crew_id: int) -> List[Order]:
        """Возвращает заказы указанной бригады.

        Args:
            crew_id: ID бригады.

        Returns:
            Список заказов.
        """
        return (
            self.session.query(Order)
            .filter_by(crew_id=crew_id)
            .order_by(Order.planned_date.desc())
            .all()
        )

    def get_by_manager(self, manager_id: int) -> List[Order]:
        """Возвращает заказы, созданные менеджером.

        Args:
            manager_id: ID менеджера.

        Returns:
            Список заказов.
        """
        return self.session.query(Order).filter_by(manager_id=manager_id).all()

    def get_by_date(self, target_date: date) -> List[Order]:
        """Возвращает заказы на указанную дату.

        Args:
            target_date: Дата.

        Returns:
            Список заказов.
        """
        return (
            self.session.query(Order)
            .filter_by(planned_date=target_date)
            .order_by(Order.planned_start)
            .all()
        )

    def get_by_date_range(self, start: date, end: date) -> List[Order]:
        """Возвращает заказы за период.

        Args:
            start: Начало периода.
            end: Конец периода.

        Returns:
            Список заказов.
        """
        return (
            self.session.query(Order)
            .filter(Order.planned_date.between(start, end))
            .order_by(Order.planned_date, Order.planned_start)
            .all()
        )

    def get_today(self) -> List[Order]:
        """Возвращает заказы на сегодня.

        Returns:
            Список заказов на текущую дату.
        """
        return self.get_by_date(date.today())

    def get_active(self) -> List[Order]:
        """Возвращает все незавершённые заказы.

        Активные — те, что не в статусах COMPLETED, PAID, CANCELLED.

        Returns:
            Список активных заказов.
        """
        inactive = (
            OrderStatus.COMPLETED,
            OrderStatus.PAID,
            OrderStatus.CANCELLED,
        )
        return (
            self.session.query(Order)
            .filter(Order.status.notin_(inactive))
            .order_by(Order.planned_date, Order.planned_start)
            .all()
        )

    def get_upcoming(self, limit: int = 10) -> List[Order]:
        """Возвращает ближайшие заказы (для дашборда).

        Args:
            limit: Максимум записей.

        Returns:
            Список ближайших заказов.
        """
        now = datetime.now()
        return (
            self.session.query(Order)
            .filter(Order.planned_date >= now.date())
            .order_by(Order.planned_date, Order.planned_start)
            .limit(limit)
            .all()
        )

    def get_unassigned(self) -> List[Order]:
        """Возвращает заказы без назначенной бригады.

        Returns:
            Список заказов без бригады.
        """
        return (
            self.session.query(Order)
            .filter(Order.crew_id.is_(None))
            .filter(Order.status.in_((OrderStatus.NEW, OrderStatus.CALCULATED)))
            .all()
        )

    def get_max_order_number(self) -> int:
        """Возвращает максимальный номер заказа.

        Используется для генерации нового номера.

        Returns:
            Максимальный order_id или 0, если заказов нет.
        """
        max_id = self.session.query(Order.order_id).order_by(
            Order.order_id.desc()
        ).first()
        return max_id[0] if max_id else 0


class OrderItemRepository(BaseRepository[OrderItem]):
    """Репозиторий для работы с позициями заказов.

    Расширяет BaseRepository специфичными методами:
    - получение позиций конкретного заказа;
    - подсчёт суммы позиций заказа.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели OrderItem."""
        super().__init__(OrderItem)

    def get_by_order(self, order_id: int) -> List[OrderItem]:
        """Возвращает все позиции заказа.

        Args:
            order_id: ID заказа.

        Returns:
            Список позиций.
        """
        return self.session.query(OrderItem).filter_by(order_id=order_id).all()

    def get_total_sum(self, order_id: int) -> float:
        """Возвращает сумму всех позиций заказа.

        Args:
            order_id: ID заказа.

        Returns:
            Сумма позиций.
        """
        items = self.get_by_order(order_id)
        return sum(item.sum for item in items) if items else 0.0

    def delete_by_order(self, order_id: int) -> int:
        """Удаляет все позиции заказа.

        Args:
            order_id: ID заказа.

        Returns:
            Количество удалённых позиций.
        """
        items = self.get_by_order(order_id)
        count = len(items)
        for item in items:
            self.session.delete(item)
        self.session.commit()
        return count
