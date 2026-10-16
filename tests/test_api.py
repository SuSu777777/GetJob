from collections.abc import Iterator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.repository import InMemoryTaskRepository
from app.schemas import Task, TaskCreate, TaskUpdate


class FakeTaskRepository:
    """Configurable GET fake; reject unrelated repository interactions."""

    def __init__(self, get_result: Task | None) -> None:
        self.get_result = get_result
        self.get_calls: list[UUID] = []

    def list(self) -> list[Task]:
        raise AssertionError("Unexpected list() call")

    def create(self, task_create: TaskCreate) -> Task:
        raise AssertionError("Unexpected create() call")

    def get(self, task_id: UUID) -> Task | None:
        self.get_calls.append(task_id)
        return self.get_result

    def update(self, task_id: UUID, task_update: TaskUpdate) -> Task | None:
        raise AssertionError("Unexpected update() call")


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(InMemoryTaskRepository())
    with TestClient(app) as test_client:
        yield test_client


def create_task(client: TestClient, name: str = "Write project brief") -> dict:
    response = client.post("/tasks", json={"name": name})
    assert response.status_code == 201
    return response.json()


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tasks_start_empty(client: TestClient) -> None:
    assert client.get("/tasks").json() == []


def test_create_and_list_task(client: TestClient) -> None:
    created = create_task(client)

    assert created["name"] == "Write project brief"
    assert created["completed"] is False
    assert client.get("/tasks").json() == [created]


def test_create_task_rejects_blank_name(client: TestClient) -> None:
    response = client.post("/tasks", json={"name": "   "})

    assert response.status_code == 422


def test_get_task(client: TestClient) -> None:
    created = create_task(client)

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_task_returns_404(client: TestClient) -> None:
    response = client.get(f"/tasks/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_get_task_uses_injected_repository() -> None:
    task = Task(id=uuid4(), name="Task from fake", completed=True)
    fake_repository = FakeTaskRepository(get_result=task)

    with TestClient(create_app(fake_repository)) as client:
        response = client.get(f"/tasks/{task.id}")

    assert fake_repository.get_calls == [task.id]
    assert isinstance(fake_repository.get_calls[0], UUID)
    assert response.status_code == 200
    assert response.json() == task.model_dump(mode="json")


def test_get_missing_task_uses_injected_repository() -> None:
    task_id = uuid4()
    fake_repository = FakeTaskRepository(get_result=None)

    with TestClient(create_app(fake_repository)) as client:
        response = client.get(f"/tasks/{task_id}")

    assert fake_repository.get_calls == [task_id]
    assert isinstance(fake_repository.get_calls[0], UUID)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@pytest.mark.parametrize(
    ("patch", "expected_name", "expected_completed"),
    [
        ({"name": "Updated name"}, "Updated name", False),
        ({"completed": True}, "Write project brief", True),
        ({"name": "Done", "completed": True}, "Done", True),
    ],
)
def test_update_task(
    client: TestClient,
    patch: dict,
    expected_name: str,
    expected_completed: bool,
) -> None:
    created = create_task(client)

    response = client.patch(f"/tasks/{created['id']}", json=patch)

    assert response.status_code == 200
    assert response.json()["name"] == expected_name
    assert response.json()["completed"] is expected_completed


@pytest.mark.parametrize("patch", [{}, {"name": None}, {"completed": None}])
def test_update_requires_non_null_field(client: TestClient, patch: dict) -> None:
    created = create_task(client)

    response = client.patch(f"/tasks/{created['id']}", json=patch)

    assert response.status_code == 422


def test_update_missing_task_returns_404(client: TestClient) -> None:
    response = client.patch(f"/tasks/{uuid4()}", json={"completed": True})

    assert response.status_code == 404


@pytest.mark.parametrize(
    "name",
    [
        "",
        "   ",
        "A" * 201,  # Maximum name length is 200 characters.
    ],
)
def test_create_rejects_invalid_name(client: TestClient, name: str) -> None:
    response = client.post("/tasks", json={"name": name})

    assert response.status_code == 422


def test_create_strips_whitespace(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={"name": "   Python   "},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Python"


def test_get_invalid_uuid_returns_422(client: TestClient) -> None:
    response = client.get("/tasks/not-a-uuid")

    assert response.status_code == 422
