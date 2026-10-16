# Knowledge & Task Assistant

The first increment of a production-oriented assistant backend. It provides a
small task API backed by process-local memory. Data is intentionally reset when
the server restarts; PostgreSQL can replace the repository in a later increment.

## Requirements

- Python 3.12 or newer

## Setup and run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the generated interactive API docs.

## Test

```bash
pytest
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check service health |
| `GET` | `/tasks` | List tasks |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks/{task_id}` | Retrieve a task |
| `PATCH` | `/tasks/{task_id}` | Change a task's name and/or completion state |

Create a task:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"name": "Review notes"}'
```

Tasks have UUID identifiers. Names are trimmed, must contain 1–200 characters,
and new tasks start with `completed: false`. PATCH requests must contain at
least one non-null supported field.

## Project structure

```text
app/
  main.py        # Application factory and HTTP routes
  repository.py  # In-memory persistence operations
  schemas.py     # Pydantic request and response models
tests/
  test_api.py    # Isolated endpoint tests
pyproject.toml   # Package metadata and dependencies
```

## Request flow

FastAPI matches an incoming request to a route in `main.py`. Pydantic validates
and normalizes its path and JSON inputs. The route calls the injected task
repository, then FastAPI validates the returned response model and serializes it
as JSON. A missing repository record is translated by the route into HTTP 404.

## Design decisions

1. **Repository boundary:** storage behavior is kept out of route handlers, so a
   PostgreSQL implementation can later replace in-memory storage with minimal API
   changes.
2. **Application factory:** tests construct a new application and repository for
   every test, preventing state leakage and making results deterministic.
3. **Separate input models:** create, patch, and response payloads express
   different contracts. Clients cannot choose IDs or initial completion state,
   and an empty or null-only patch is rejected.

## Practice change

Add `DELETE /tasks/{task_id}`. Return HTTP 204 when deletion succeeds and HTTP
404 for an unknown UUID. Add tests for both cases and ensure one test verifies
that a deleted task no longer appears in `GET /tasks`.
