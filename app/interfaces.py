from typing import Protocol
from uuid import UUID

from app.schemas import Task, TaskCreate, TaskUpdate


class TaskRepository(Protocol):
    def list(self) -> list[Task]: ...

    def create(self, task_create: TaskCreate) -> Task: ...

    def get(self, task_id: UUID) -> Task | None: ...

    def update(self, task_id: UUID, task_update: TaskUpdate) -> Task | None: ...

