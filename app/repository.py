from uuid import UUID, uuid4

from app.schemas import Task, TaskCreate, TaskUpdate


class InMemoryTaskRepository:
    """In-process task storage. Data is lost when the application stops."""

    def __init__(self) -> None:
        self._tasks: dict[UUID, Task] = {}

    def list(self) -> list[Task]:
        return list(self._tasks.values())

    def create(self, task_create: TaskCreate) -> Task:
        task = Task(id=uuid4(), name=task_create.name, completed=False)
        self._tasks[task.id] = task
        return task

    def get(self, task_id: UUID) -> Task | None:
        return self._tasks.get(task_id)

    def update(self, task_id: UUID, task_update: TaskUpdate) -> Task | None:
        task = self.get(task_id)
        if task is None:
            return None

        updated_task = task.model_copy(update=task_update.model_dump(exclude_unset=True))
        self._tasks[task_id] = updated_task
        return updated_task

