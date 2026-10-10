"""Сервис отчётов и аналитики.

Модуль реализует бизнес-логику отчётов (см. ТЗ, F-6):
- KPI для дашборда;
- выручка за период;
- загрузка бригад;
- топ клиентов;
- статистика по статусам и способам оплаты.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List

from src.models.order import Order, OrderStatus
from src.models.payment import Payment, PaymentMethod, PaymentStatus
from src.repositories.client_repository import ClientRepository
from src.repositories.crew_repository import CrewRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.payment_repository import PaymentRepository


class ReportService:
    """Сервис отчётов и аналитики.

    Формирует агрегированные данные для дашборда и экрана Финансы.
    """

    def __init__(self) -> None:
        """Инициализирует сервис с репозиториями."""
        self.order_repo = OrderRepository()
        self.payment_repo = PaymentRepository()
        self.client_repo = ClientRepository()
        self.crew_repo = CrewRepository()

    def get_dashboard_kpi(self) -> Dict:
        """Возвращает KPI для дашборда.

        Returns:
            Словарь с ключевыми метриками:
            - orders_today: заказов на сегодня
            - revenue_today: выручка за сегодня
            - active_crews: активных бригад
            - avg_check: средний чек
        """
        today = date.today()
        orders_today = self.order_repo.get_by_date(today)

        # Выручка за сегодня — сумма оплаченных платежей
        payments_today = self.payment_repo.get_by_date(today)
        revenue_today = sum(
            p.amount for p in payments_today if p.status == PaymentStatus.PAID
        )

        active_crews = len(self.crew_repo.get_active())

        # Средний чек — по оплаченным заказам
        paid_orders = self.order_repo.get_by_status(OrderStatus.PAID)
        avg_check = (
            sum(o.total_price for o in paid_orders) / len(paid_orders)
            if paid_orders else 0.0
        )

        return {
            "orders_today": len(orders_today),
            "revenue_today": round(revenue_today, 2),
            "active_crews": active_crews,
            "avg_check": round(avg_check, 2),
        }

    def get_revenue_for_period(self, start: date, end: date) -> Dict:
        """Возвращает выручку за период.

        Args:
            start: Начало периода.
            end: Конец периода.

        Returns:
            Словарь с метриками периода:
            - revenue: общая выручка
            - orders_count: количество заказов
            - avg_check: средний чек
            - payments_count: количество платежей
        """
        orders = self.order_repo.get_by_date_range(start, end)
        payments = self.payment_repo.get_by_date_range(start, end)
        paid_payments = [p for p in payments if p.status == PaymentStatus.PAID]

        revenue = sum(p.amount for p in paid_payments)
        orders_count = len(orders)
        avg_check = revenue / orders_count if orders_count else 0.0

        return {
            "revenue": round(revenue, 2),
            "orders_count": orders_count,
            "avg_check": round(avg_check, 2),
            "payments_count": len(paid_payments),
            "period": {"start": start, "end": end},
        }

    def get_workload_by_crew(self) -> List[Dict]:
        """Возвращает загрузку бригад на сегодня.

        Returns:
            Список словарей с загрузкой по каждой бригаде.
        """
        today = date.today()
        crews = self.crew_repo.get_active()
        result = []

        for crew in crews:
            crew_orders = [
                o for o in self.order_repo.get_by_crew(crew.crew_id)
                if o.planned_date == today
            ]
            # Условно: 3 заказа = 100% загрузка
            workload = min(len(crew_orders) * 33.3, 100.0)
            result.append({
                "crew_id": crew.crew_id,
                "name": crew.name,
                "zone": crew.zone,
                "orders_count": len(crew_orders),
                "workload": round(workload, 1),
            })
        return result

    def get_orders_count_by_status(self) -> Dict[str, int]:
        """Возвращает количество заказов по каждому статусу.

        Returns:
            Словарь {status: count}.
        """
        result = {}
        for status in OrderStatus.ALL:
            result[status] = len(self.order_repo.get_by_status(status))
        return result

    def get_top_clients(self, limit: int = 10) -> List[Dict]:
        """Возвращает топ клиентов по сумме заказов.

        Args:
            limit: Максимум записей.

        Returns:
            Список словарей с клиентами и их суммами.
        """
        clients = self.client_repo.get_all()
        result = []

        for client in clients:
            orders = self.order_repo.get_by_client(client.client_id)
            total = sum(o.total_price for o in orders if o.total_price)
            result.append({
                "client_id": client.client_id,
                "name": client.name,
                "orders_count": len(orders),
                "total_sum": round(total, 2),
            })

        result.sort(key=lambda x: x["total_sum"], reverse=True)
        return result[:limit]

    def get_payment_methods_stats(
        self,
        start: date = None,
        end: date = None,
    ) -> Dict[str, float]:
        """Возвращает статистику по способам оплаты.

        Args:
            start: Начало периода (опционально).
            end: Конец периода (опционально).

        Returns:
            Словарь {method: total_amount}.
        """
        if start and end:
            payments = self.payment_repo.get_by_date_range(start, end)
        else:
            payments = self.payment_repo.get_paid()

        result = {method: 0.0 for method in PaymentMethod.ALL}
        for payment in payments:
            if payment.status == PaymentStatus.PAID:
                result[payment.method] += payment.amount

        return {k: round(v, 2) for k, v in result.items()}

    def get_orders_per_day(
        self,
        days: int = 7,
    ) -> List[Dict]:
        """Возвращает количество заказов и выручку по дням.

        Для графика динамики на дашборде.

        Args:
            days: Количество дней.

        Returns:
            Список словарей с датой, количеством и выручкой.
        """
        result = []
        today = date.today()

        for i in range(days - 1, -1, -1):
            target = today - timedelta(days=i)
            orders = self.order_repo.get_by_date(target)
            payments = self.payment_repo.get_by_date(target)
            revenue = sum(
                p.amount for p in payments if p.status == PaymentStatus.PAID
            )
            result.append({
                "date": target,
                "orders_count": len(orders),
                "revenue": round(revenue, 2),
            })
        return result
