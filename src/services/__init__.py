"""Сервисы CleanOps.

Пакет содержит бизнес-логику приложения. Сервисы работают с
репозиториями и DTO, не зная про UI.

Example:
    >>> from src.services import CalculatorService, AuthService
    >>> calc = CalculatorService()
    >>> result = calc.calculate(...)
"""

from src.services.auth_service import AuthService, AuthResult
from src.services.calculator_service import CalculatorService
from src.services.dtos import (
    CalculationInput,
    CalculationResult,
    OrderCreateDTO,
    OrderItemDTO,
)
from src.services.order_service import OrderService
from src.services.report_service import ReportService

__all__ = [
    "AuthService",
    "AuthResult",
    "CalculatorService",
    "OrderService",
    "ReportService",
    "CalculationInput",
    "CalculationResult",
    "OrderCreateDTO",
    "OrderItemDTO",
]
