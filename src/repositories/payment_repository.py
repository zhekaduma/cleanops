"""Репозиторий платежей.

Модуль содержит PaymentRepository — CRUD для модели Payment
плюс фильтрация по статусу, способу оплаты, дате.
"""

from datetime import date, datetime
from typing import List, Optional

from src.models.payment import Payment, PaymentStatus
from src.repositories.base_repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Репозиторий для работы с платежами.

    Расширяет BaseRepository специфичными методами:
    - получение платежей заказа;
    - фильтрация по статусу;
    - отчёты по выручке.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели Payment."""
        super().__init__(Payment)

    def get_by_order(self, order_id: int) -> List[Payment]:
        """Возвращает платежи заказа.

        Args:
            order_id: ID заказа.

        Returns:
            Список платежей.
        """
        return self.session.query(Payment).filter_by(order_id=order_id).all()

    def get_by_status(self, status: str) -> List[Payment]:
        """Возвращает платежи с указанным статусом.

        Args:
            status: Статус (см. PaymentStatus).

        Returns:
            Список платежей.
        """
        return self.session.query(Payment).filter_by(status=status).all()

    def get_paid(self) -> List[Payment]:
        """Возвращает все оплаченные платежи.

        Returns:
            Список оплаченных платежей.
        """
        return self.get_by_status(PaymentStatus.PAID)

    def get_by_date(self, target_date: date) -> List[Payment]:
        """Возвращает платежи за указанную дату.

        Args:
            target_date: Дата.

        Returns:
            Список платежей.
        """
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())
        return (
            self.session.query(Payment)
            .filter(Payment.paid_at.between(start, end))
            .all()
        )

    def get_by_date_range(self, start: date, end: date) -> List[Payment]:
        """Возвращает платежи за период.

        Args:
            start: Начало периода.
            end: Конец периода.

        Returns:
            Список платежей.
        """
        start_dt = datetime.combine(start, datetime.min.time())
        end_dt = datetime.combine(end, datetime.max.time())
        return (
            self.session.query(Payment)
            .filter(Payment.paid_at.between(start_dt, end_dt))
            .all()
        )

    def get_total_for_period(self, start: date, end: date) -> float:
        """Возвращает сумму платежей за период.

        Args:
            start: Начало периода.
            end: Конец периода.

        Returns:
            Общая сумма оплаченных платежей.
        """
        payments = self.get_by_date_range(start, end)
        return sum(p.amount for p in payments if p.status == PaymentStatus.PAID)

    def get_total_for_order(self, order_id: int) -> float:
        """Возвращает сумму оплат по заказу.

        Args:
            order_id: ID заказа.

        Returns:
            Сумма оплат.
        """
        payments = self.get_by_order(order_id)
        return sum(p.amount for p in payments if p.status == PaymentStatus.PAID)
