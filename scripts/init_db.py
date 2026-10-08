"""Скрипт инициализации базы данных CleanOps.

Создаёт таблицы согласно моделям и наполняет БД тестовыми данными.
Запускать: python scripts/init_db.py

Скрипт идемпотентен — можно запускать несколько раз, он пересоздаёт БД.
"""

import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

# Добавляем корень проекта в path, чтобы импорты работали
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config.database import Base, db  # noqa: E402
from src.models import (  # noqa: E402
    AuditLog,
    ChecklistTask,
    CleaningType,
    Client,
    ClientType,
    Crew,
    Object,
    ObjectType,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Service,
    ServiceUnit,
    User,
    UserRole,
)


def create_tables() -> None:
    """Создаёт все таблицы в БД (удаляя существующие)."""
    print("Создание таблиц...")
    Base.metadata.drop_all(db.engine)
    Base.metadata.create_all(db.engine)
    print(f"Создано таблиц: {len(Base.metadata.tables)}")
    for table_name in Base.metadata.tables:
        print(f"  - {table_name}")


def seed_users(session) -> dict[str, User]:
    """Создаёт тестовых пользователей.

    Returns:
        Словарь {role: User} для использования при создании заказов.
    """
    print("Создание пользователей...")

    users = {
        UserRole.ADMIN: User(
            username="admin",
            password_hash="$2b$12$dummy_hash_admin",  # заглушка
            full_name="Кудусов Евгений Александрович",
            phone="+7 (999) 100-10-10",
            email="admin@cleanops.ru",
            role=UserRole.ADMIN,
            is_active=True,
        ),
        UserRole.MANAGER: User(
            username="manager",
            password_hash="$2b$12$dummy_hash_manager",
            full_name="Иванов Иван Иванович",
            phone="+7 (999) 200-20-20",
            email="manager@cleanops.ru",
            role=UserRole.MANAGER,
            is_active=True,
        ),
        UserRole.BRIGADIER: User(
            username="brigadier",
            password_hash="$2b$12$dummy_hash_brigadier",
            full_name="Петрова Мария Ивановна",
            phone="+7 (999) 300-30-30",
            email="brigadier@cleanops.ru",
            role=UserRole.BRIGADIER,
            is_active=True,
        ),
        UserRole.CLEANER: User(
            username="cleaner",
            password_hash="$2b$12$dummy_hash_cleaner",
            full_name="Сидоров Алексей Петрович",
            phone="+7 (999) 400-40-40",
            email="cleaner@cleanops.ru",
            role=UserRole.CLEANER,
            is_active=True,
        ),
        UserRole.ACCOUNTANT: User(
            username="accountant",
            password_hash="$2b$12$dummy_hash_accountant",
            full_name="Козлова Ольга Сергеевна",
            phone="+7 (999) 500-50-50",
            email="accountant@cleanops.ru",
            role=UserRole.ACCOUNTANT,
            is_active=True,
        ),
    }

    for user in users.values():
        session.add(user)

    session.flush()
    print(f"Создано пользователей: {len(users)}")
    return users


def seed_clients(session) -> list[Client]:
    """Создаёт тестовых клиентов с объектами."""
    print("Создание клиентов...")

    client1 = Client(
        type=ClientType.INDIVIDUAL,
        name="Иванов Алексей Сергеевич",
        phone="+7 (913) 111-11-11",
        email="ivanov@mail.ru",
        discount=5.0,
        notes="Постоянный клиент",
    )
    client2 = Client(
        type=ClientType.COMPANY,
        name="ООО «Ромашка»",
        phone="+7 (383) 222-22-22",
        email="info@romashka.ru",
        address="г. Новосибирск, ул. Кирова, 8, офис 12",
        discount=10.0,
    )
    client3 = Client(
        type=ClientType.INDIVIDUAL,
        name="Сидорова Мария Петровна",
        phone="+7 (913) 333-33-33",
        email="sidorova@mail.ru",
    )

    session.add_all([client1, client2, client3])
    session.flush()

    # Объекты
    objects = [
        Object(
            client_id=client1.client_id,
            address="г. Новосибирск, ул. Ленина, 5, кв. 12",
            area=60.0,
            object_type=ObjectType.APARTMENT,
            access_notes="Код домофона 1234",
        ),
        Object(
            client_id=client1.client_id,
            address="г. Новосибирск, ул. Мира, 12, кв. 45",
            area=80.0,
            object_type=ObjectType.APARTMENT,
        ),
        Object(
            client_id=client2.client_id,
            address="г. Новосибирск, ул. Кирова, 8, офис 12",
            area=120.0,
            object_type=ObjectType.OFFICE,
            access_notes="Пропуск на вахте",
        ),
        Object(
            client_id=client3.client_id,
            address="г. Новосибирск, ул. Гоголя, 3, кв. 7",
            area=45.0,
            object_type=ObjectType.APARTMENT,
        ),
    ]
    session.add_all(objects)
    session.flush()

    print(f"Создано клиентов: 3, объектов: {len(objects)}")
    return [client1, client2, client3]


def seed_services(session) -> list[Service]:
    """Создаёт тестовые услуги."""
    print("Создание услуг...")

    services = [
        Service(name="Мытьё окон", unit=ServiceUnit.PIECE, price=300.0, norm_hours=0.5),
        Service(name="Химчистка мебели", unit=ServiceUnit.PIECE, price=800.0, norm_hours=1.0),
        Service(name="Мойка люстры", unit=ServiceUnit.PIECE, price=500.0, norm_hours=0.3),
        Service(name="Уборка балкона", unit=ServiceUnit.SQM, price=100.0, norm_hours=0.2),
        Service(name="Дезинфекция", unit=ServiceUnit.SQM, price=50.0, norm_hours=0.1),
    ]

    session.add_all(services)
    session.flush()
    print(f"Создано услуг: {len(services)}")
    return services


def seed_crews(session) -> list[Crew]:
    """Создаёт тестовые бригады."""
    print("Создание бригад...")

    crews = [
        Crew(name="Бригада 1", zone="Центральный район", transport="Газель А123БВ"),
        Crew(name="Бригада 2", zone="Ленинский район", transport="Ford Transit В456ГД"),
        Crew(name="Бригада 3", zone="Октябрьский район", transport="Лада Ларгус Е789ЖЗ"),
        Crew(name="Бригада 4", zone="Заельцовский район", transport=None),
    ]

    session.add_all(crews)
    session.flush()
    print(f"Создано бригад: {len(crews)}")
    return crews


def seed_orders(session, users, clients, services, crews) -> None:
    """Создаёт тестовые заказы с позициями, чек-листами и платежами."""
    print("Создание заказов...")

    today = date.today()
    manager = users[UserRole.MANAGER]

    # Получаем объекты для ссылок
    objects = session.query(Object).all()

    # Заказ 1 — в работе
    order1 = Order(
        client_id=clients[0].client_id,
        object_id=objects[0].object_id,
        crew_id=crews[0].crew_id,
        manager_id=manager.user_id,
        status=OrderStatus.IN_PROGRESS,
        cleaning_type=CleaningType.GENERAL,
        area=60.0,
        urgency_coef=1.5,
        dirt_coef=1.2,
        discount=500.0,
        total_price=20748.0,
        planned_date=today,
        planned_start=time(10, 0),
        planned_end=time(13, 0),
        actual_start=datetime.combine(today, time(10, 5)),
        notes="Генеральная уборка с мытьём окон",
    )
    session.add(order1)
    session.flush()

    # Позиции заказа 1
    session.add_all([
        OrderItem(
            order_id=order1.order_id,
            service_id=services[0].service_id,
            quantity=3.0, price=300.0, sum=900.0,
        ),
        OrderItem(
            order_id=order1.order_id,
            service_id=services[1].service_id,
            quantity=1.0, price=800.0, sum=800.0,
        ),
    ])

    # Чек-лист заказа 1
    session.add_all([
        ChecklistTask(
            order_id=order1.order_id,
            description="Пропылесосить все комнаты",
            is_required=True, is_done=True,
            done_at=datetime.combine(today, time(10, 30)),
        ),
        ChecklistTask(
            order_id=order1.order_id,
            description="Помыть полы",
            is_required=True, is_done=True,
            done_at=datetime.combine(today, time(11, 0)),
        ),
        ChecklistTask(
            order_id=order1.order_id,
            description="Мытьё окон (3 шт)",
            is_required=True, is_done=False,
        ),
        ChecklistTask(
            order_id=order1.order_id,
            description="Химчистка дивана",
            is_required=False, is_done=False,
        ),
    ])

    # Заказ 2 — назначен
    order2 = Order(
        client_id=clients[1].client_id,
        object_id=objects[2].object_id,
        crew_id=crews[1].crew_id,
        manager_id=manager.user_id,
        status=OrderStatus.ASSIGNED,
        cleaning_type=CleaningType.MAINTENANCE,
        area=120.0,
        urgency_coef=1.0,
        dirt_coef=1.0,
        total_price=12000.0,
        planned_date=today + timedelta(days=1),
        planned_start=time(9, 0),
        planned_end=time(12, 0),
    )
    session.add(order2)

    # Заказ 3 — новый
    order3 = Order(
        client_id=clients[2].client_id,
        object_id=objects[3].object_id,
        crew_id=None,
        manager_id=manager.user_id,
        status=OrderStatus.NEW,
        cleaning_type=CleaningType.POST_RENOVATION,
        area=45.0,
        urgency_coef=1.0,
        dirt_coef=1.5,
        total_price=0.0,
        planned_date=today + timedelta(days=2),
    )
    session.add(order3)

    # Заказ 4 — завершён
    order4 = Order(
        client_id=clients[0].client_id,
        object_id=objects[1].object_id,
        crew_id=crews[0].crew_id,
        manager_id=manager.user_id,
        status=OrderStatus.COMPLETED,
        cleaning_type=CleaningType.MAINTENANCE,
        area=80.0,
        urgency_coef=1.0,
        dirt_coef=1.0,
        total_price=9000.0,
        planned_date=today - timedelta(days=2),
        actual_start=datetime.combine(today - timedelta(days=2), time(10, 0)),
        actual_end=datetime.combine(today - timedelta(days=2), time(12, 30)),
    )
    session.add(order4)
    session.flush()

    # Платёж по заказу 4
    session.add(Payment(
        order_id=order4.order_id,
        amount=9000.0,
        method=PaymentMethod.CARD,
        status=PaymentStatus.PAID,
        paid_at=datetime.combine(today - timedelta(days=2), time(12, 45)),
        created_by=users[UserRole.MANAGER].user_id,
    ))

    # Запись в audit log
    session.add(AuditLog(
        user_id=manager.user_id,
        action="create",
        entity="Order",
        entity_id=order1.order_id,
        details='{"client": "Иванов А.С.", "amount": 20748}',
        ip_address="192.168.1.10",
    ))

    print("Создано заказов: 4, позиций, чек-листов, платежей")


def main() -> None:
    """Точка входа скрипта инициализации."""
    print("=" * 50)
    print("CleanOps — Инициализация базы данных")
    print("=" * 50)

    create_tables()

    session = db.get_session()
    try:
        users = seed_users(session)
        clients = seed_clients(session)
        services = seed_services(session)
        crews = seed_crews(session)
        seed_orders(session, users, clients, services, crews)

        session.commit()
        print("=" * 50)
        print("База данных успешно инициализирована!")
        print(f"Файл БД: {db.engine.url}")
        print("=" * 50)

    except Exception as e:
        session.rollback()
        print(f"Ошибка: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
