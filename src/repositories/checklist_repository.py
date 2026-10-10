"""Репозиторий задач чек-листа.

Модуль содержит ChecklistTaskRepository — CRUD для модели ChecklistTask
плюс фильтрация по заказу, выполнению, фотоотчётам.
"""

from typing import List

from src.models.checklist import ChecklistTask
from src.repositories.base_repository import BaseRepository


class ChecklistTaskRepository(BaseRepository[ChecklistTask]):
    """Репозиторий для работы с задачами чек-листов.

    Расширяет BaseRepository специфичными методами:
    - получение задач заказа;
    - фильтрация по выполнению;
    - работа с фотоотчётами.
    """

    def __init__(self) -> None:
        """Инициализирует репозиторий для модели ChecklistTask."""
        super().__init__(ChecklistTask)

    def get_by_order(self, order_id: int) -> List[ChecklistTask]:
        """Возвращает все задачи заказа.

        Args:
            order_id: ID заказа.

        Returns:
            Список задач.
        """
        return (
            self.session.query(ChecklistTask)
            .filter_by(order_id=order_id)
            .order_by(ChecklistTask.task_id)
            .all()
        )

    def get_done(self, order_id: int) -> List[ChecklistTask]:
        """Возвращает выполненные задачи заказа.

        Args:
            order_id: ID заказа.

        Returns:
            Список выполненных задач.
        """
        return (
            self.session.query(ChecklistTask)
            .filter_by(order_id=order_id, is_done=True)
            .all()
        )

    def get_pending(self, order_id: int) -> List[ChecklistTask]:
        """Возвращает невыполненные задачи заказа.

        Args:
            order_id: ID заказа.

        Returns:
            Список невыполненных задач.
        """
        return (
            self.session.query(ChecklistTask)
            .filter_by(order_id=order_id, is_done=False)
            .all()
        )

    def get_required(self, order_id: int) -> List[ChecklistTask]:
        """Возвращает обязательные задачи заказа.

        Args:
            order_id: ID заказа.

        Returns:
            Список обязательных задач.
        """
        return (
            self.session.query(ChecklistTask)
            .filter_by(order_id=order_id, is_required=True)
            .all()
        )

    def get_progress(self, order_id: int) -> tuple:
        """Возвращает прогресс выполнения чек-листа.

        Args:
            order_id: ID заказа.

        Returns:
            Кортеж (выполнено, всего).
        """
        total = self.session.query(ChecklistTask).filter_by(order_id=order_id).count()
        done = (
            self.session.query(ChecklistTask)
            .filter_by(order_id=order_id, is_done=True)
            .count()
        )
        return done, total

    def is_complete(self, order_id: int) -> bool:
        """Проверяет, все ли обязательные задачи выполнены.

        Args:
            order_id: ID заказа.

        Returns:
            True если все обязательные задачи выполнены.
        """
        required = self.get_required(order_id)
        if not required:
            return True
        return all(task.is_done for task in required)

    def delete_by_order(self, order_id: int) -> int:
        """Удаляет все задачи заказа.

        Args:
            order_id: ID заказа.

        Returns:
            Количество удалённых задач.
        """
        tasks = self.get_by_order(order_id)
        count = len(tasks)
        for task in tasks:
            self.session.delete(task)
        self.session.commit()
        return count
