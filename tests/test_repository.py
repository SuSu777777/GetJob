from uuid import UUID, uuid4

from app.repository import InMemoryTaskRepository
from app.schemas import TaskCreate, TaskUpdate


def test_new_repository_starts_empty() -> None:
    repository = InMemoryTaskRepository()

    assert repository.list() == []


def test_create_generates_uuid_and_stores_task() -> None:
    repository = InMemoryTaskRepository()

    task = repository.create(TaskCreate(name="Write project brief"))

    assert isinstance(task.id, UUID)
    assert task.name == "Write project brief"
    assert repository.list() == [task]


def test_new_task_is_not_completed() -> None:
    repository = InMemoryTaskRepository()

    task = repository.create(TaskCreate(name="Write project brief"))

    assert task.completed is False


def test_get_retrieves_existing_task() -> None:
    repository = InMemoryTaskRepository()
    task = repository.create(TaskCreate(name="Write project brief"))

    assert repository.get(task.id) == task


def test_get_missing_task_returns_none() -> None:
    repository = InMemoryTaskRepository()

    assert repository.get(uuid4()) is None


def test_update_can_change_name() -> None:
    repository = InMemoryTaskRepository()
    task = repository.create(TaskCreate(name="Write project brief"))

    updated = repository.update(task.id, TaskUpdate(name="Review project brief"))

    assert updated is not None
    assert updated.id == task.id
    assert updated.name == "Review project brief"
    assert updated.completed is False
    assert repository.get(task.id) == updated


def test_update_can_change_completed() -> None:
    repository = InMemoryTaskRepository()
    task = repository.create(TaskCreate(name="Write project brief"))

    updated = repository.update(task.id, TaskUpdate(completed=True))

    assert updated is not None
    assert updated.id == task.id
    assert updated.name == task.name
    assert updated.completed is True
    assert repository.get(task.id) == updated


def test_update_missing_task_returns_none() -> None:
    repository = InMemoryTaskRepository()

    assert repository.update(uuid4(), TaskUpdate(completed=True)) is None
    assert repository.list() == []


def test_repositories_have_independent_state() -> None:
    first = InMemoryTaskRepository()
    second = InMemoryTaskRepository()

    first_task = first.create(TaskCreate(name="First task"))
    second_task = second.create(TaskCreate(name="Second task"))

    assert first.list() == [first_task]
    assert second.list() == [second_task]
    assert first.get(second_task.id) is None
    assert second.get(first_task.id) is None
