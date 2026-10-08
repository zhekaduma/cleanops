"""Скрипт проверки базы данных CleanOps.

Выводит сводку по всем таблицам: количество записей и примеры данных.
Запуск: python scripts/check_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config.database import db  # noqa: E402
from src.models import (  # noqa: E402
    ChecklistTask,
    Client,
    Crew,
    Object,
    Order,
    OrderItem,
    Payment,
    Service,
    User,
)


def main() -> None:
    """Проверяет БД и выводит статистику по таблицам."""
    session = db.get_session()

    print("=" * 60)
    print("CleanOps — Проверка базы данных")
    print("=" * 60)

    tables = {
        "Пользователи": User,
        "Клиенты": Client,
        "Объекты": Object,
        "Услуги": Service,
        "Бригады": Crew,
        "Заказы": Order,
        "Позиции заказов": OrderItem,
        "Задачи чек-листов": ChecklistTask,
        "Платежи": Payment,
    }

    for label, model in tables.items():
        count = session.query(model).count()
        print(f"{label:25} {count:>5}")

    print("-" * 60)
    print("Примеры данных:")
    print("-" * 60)

    print("\nПользователи:")
    for user in session.query(User).limit(3).all():
        print(f"  #{user.user_id} {user.full_name} ({user.role})")

    print("\nЗаказы:")
    for order in session.query(Order).all():
        print(
            f"  #{order.order_id} {order.status:12} "
            f"{order.area} м² — {order.total_price} ₽"
        )

    session.close()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
