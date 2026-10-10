"""DTO (Data Transfer Objects) для сервисов CleanOps.

Модуль содержит dataclass-структуры для передачи данных между слоями
приложения: UI → Controller → Service → Repository.

Использование DTO позволяет:
- Чётко определить контракт между слоями.
- Избежать передачи сырых dict-ов.
- Обеспечить типизацию.
"""

from dataclasses import dataclass, field
from datetime import date, time
from typing import List, Optional


@dataclass
class OrderItemDTO:
    """Позиция заказа (услуга) для расчёта.

    Attributes:
        service_id: ID услуги.
        service_name: Название (для отображения).
        quantity: Количество.
        price: Цена за единицу.
        sum: Сумма (quantity × price).
    """

    service_id: int
    service_name: str = ""
    quantity: float = 1.0
    price: float = 0.0
    sum: float = 0.0


@dataclass
class CalculationInput:
    """Входные данные для расчёта стоимости заказа.

    Attributes:
        area: Площадь уборки в м².
        cleaning_type: Тип уборки (maintenance/general/post_renovation/windows).
        urgency_coef: Коэффициент срочности.
        dirt_coef: Коэффициент загрязнения.
        items: Список доп. услуг.
        transport_cost: Транспортные расходы.
        discount: Скидка в рублях.
        vat_percent: НДС в процентах (0, если без НДС).
    """

    area: float
    cleaning_type: str = "maintenance"
    urgency_coef: float = 1.0
    dirt_coef: float = 1.0
    items: List[OrderItemDTO] = field(default_factory=list)
    transport_cost: float = 0.0
    discount: float = 0.0
    vat_percent: float = 0.0


@dataclass
class CalculationResult:
    """Результат расчёта стоимости заказа.

    Attributes:
        base_price: Базовая стоимость (площадь × тариф).
        tariff: Использованный тариф за м².
        subtotal: Стоимость с коэффициентами.
        items_sum: Сумма доп. услуг.
        transport_cost: Транспорт.
        discount: Скидка.
        subtotal_after_discount: Подытог после скидки.
        vat_amount: Сумма НДС.
        total: Итоговая стоимость.
    """

    base_price: float = 0.0
    tariff: float = 0.0
    subtotal: float = 0.0
    items_sum: float = 0.0
    transport_cost: float = 0.0
    discount: float = 0.0
    subtotal_after_discount: float = 0.0
    vat_amount: float = 0.0
    total: float = 0.0

    def to_dict(self) -> dict:
        """Возвращает результат как dict для UI.

        Returns:
            Словарь со всеми полями.
        """
        return {
            "base_price": self.base_price,
            "tariff": self.tariff,
            "subtotal": self.subtotal,
            "items_sum": self.items_sum,
            "transport_cost": self.transport_cost,
            "discount": self.discount,
            "subtotal_after_discount": self.subtotal_after_discount,
            "vat_amount": self.vat_amount,
            "total": self.total,
        }


@dataclass
class OrderCreateDTO:
    """Данные для создания нового заказа.

    Attributes:
        client_id: ID клиента.
        object_id: ID объекта уборки.
        manager_id: ID менеджера.
        cleaning_type: Тип уборки.
        area: Площадь.
        urgency_coef: Коэффициент срочности.
        dirt_coef: Коэффициент загрязнения.
        discount: Скидка.
        total_price: Итоговая цена.
        planned_date: Планируемая дата.
        planned_start: Планируемое время начала.
        planned_end: Планируемое время окончания.
        notes: Заметки.
        items: Позиции заказа.
    """

    client_id: int
    object_id: int
    manager_id: int
    cleaning_type: str
    area: float
    urgency_coef: float = 1.0
    dirt_coef: float = 1.0
    discount: float = 0.0
    total_price: float = 0.0
    planned_date: Optional[date] = None
    planned_start: Optional[time] = None
    planned_end: Optional[time] = None
    notes: Optional[str] = None
    items: List[OrderItemDTO] = field(default_factory=list)
