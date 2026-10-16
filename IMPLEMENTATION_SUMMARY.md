# TaskRepository Protocol Implementation Summary

## Goal

Introduce a `TaskRepository` protocol without changing the existing FastAPI API,
application factory, dependency injection, or in-memory repository behavior.

## Changes

### Added: `app/interfaces.py`

Defines the structural `TaskRepository` protocol with the existing repository
operations and schema types:

- `list() -> list[Task]`
- `create(task_create: TaskCreate) -> Task`
- `get(task_id: UUID) -> Task | None`
- `update(task_id: UUID, task_update: TaskUpdate) -> Task | None`

### Updated: `app/main.py`

Repository-facing type annotations now use `TaskRepository` in:

- The `create_app` repository parameter
- The repository dependency provider
- The list, create, retrieve, and update route dependencies

`InMemoryTaskRepository` remains imported and instantiated as the default
repository when no implementation is supplied to `create_app`.

## Behavior and Architecture

- Existing endpoint behavior is unchanged.
- `InMemoryTaskRepository` was not modified.
- The protocol uses structural typing, so implementations do not need to inherit
  from `TaskRepository` explicitly.
- The application factory and dependency injection behavior are preserved.
- No PostgreSQL integration, new dependency, or unrelated refactoring was added.

## Verification

The requested command could not run as written:

```text
python -m pytest -v test/test_api.py
zsh: command not found: python
```

The environment provides the project interpreter at `.venv/bin/python`, and the
existing test file is `tests/test_api.py`. The equivalent command was run:

```text
.venv/bin/python -m pytest -v tests/test_api.py
```

Result:

```text
18 passed, 1 warning in 0.29s
```

Warning:

```text
StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated;
install httpx2 instead.
```

The warning originates from FastAPI/Starlette test dependencies and did not
affect the test result.
