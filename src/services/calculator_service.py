"""Сервис расчёта стоимости заказа.

Модуль реализует бизнес-логику калькулятора (см. ТЗ, F-1.1–F-1.8).
Формула расчёта:

    Итог = (Площадь × Тариф × Коэф.срочности × Коэф.загрязнения)
           + Σ(Доп.услуги × Кол-во)
           + Транспорт
           − Скидка
           + НДС

Сервис не знает про UI и БД — работает только с DTO.
"""

from src.services.dtos import (
    CalculationInput,
    CalculationResult,
)


class CleaningTariff:
    """Тарифы за м² по типу уборки.

    Соответствует прайс-листу компании (см. ТЗ, F-2.6).
    """

    TARIFFS = {
        "maintenance": 100.0,
        "general": 150.0,
        "post_renovation": 220.0,
        "windows": 300.0,
    }

    DEFAULT = 150.0

    @classmethod
    def get_tariff(cls, cleaning_type: str) -> float:
        """Возвращает тариф для типа уборки.

        Args:
            cleaning_type: Тип уборки.

        Returns:
            Тариф за м².
        """
        return cls.TARIFFS.get(cleaning_type, cls.DEFAULT)


class CalculatorService:
    """Сервис расчёта стоимости заказа.

    Реализует полную формулу расчёта из ТЗ. Принимает DTO с параметрами,
    возвращает DTO с детализированным результатом.
    """

    def calculate(self, data: CalculationInput) -> CalculationResult:
        """Считает стоимость заказа по формуле из ТЗ.

        Args:
            data: Входные параметры расчёта.

        Returns:
            Детализированный результат с разбивкой по строкам.
        """
        # 1. Базовая стоимость: площадь × тариф
        tariff = CleaningTariff.get_tariff(data.cleaning_type)
        base_price = round(data.area * tariff, 2)

        # 2. Применяем коэффициенты
        subtotal = round(
            base_price * data.urgency_coef * data.dirt_coef,
            2,
        )

        # 3. Сумма доп. услуг
        items_sum = round(
            sum(item.quantity * item.price for item in data.items),
            2,
        )

        # 4. Подытог
        subtotal_with_items = round(
            subtotal + items_sum + data.transport_cost,
            2,
        )

        # 5. Скидка
        subtotal_after_discount = round(
            max(subtotal_with_items - data.discount, 0.0),
            2,
        )

        # 6. НДС
        vat_amount = round(
            subtotal_after_discount * (data.vat_percent / 100.0),
            2,
        )

        # 7. Итоговая стоимость
        total = round(subtotal_after_discount + vat_amount, 2)

        return CalculationResult(
            base_price=base_price,
            tariff=tariff,
            subtotal=subtotal,
            items_sum=items_sum,
            transport_cost=data.transport_cost,
            discount=data.discount,
            subtotal_after_discount=subtotal_after_discount,
            vat_amount=vat_amount,
            total=total,
        )

    def calculate_quick(
        self,
        area: float,
        cleaning_type: str = "maintenance",
        urgency_coef: float = 1.0,
        dirt_coef: float = 1.0,
        discount: float = 0.0,
    ) -> float:
        """Быстрый расчёт итоговой стоимости (без детализации).

        Args:
            area: Площадь в м².
            cleaning_type: Тип уборки.
            urgency_coef: Коэффициент срочности.
            dirt_coef: Коэффициент загрязнения.
            discount: Скидка в рублях.

        Returns:
            Итоговая стоимость.
        """
        data = CalculationInput(
            area=area,
            cleaning_type=cleaning_type,
            urgency_coef=urgency_coef,
            dirt_coef=dirt_coef,
            discount=discount,
        )
        return self.calculate(data).total
